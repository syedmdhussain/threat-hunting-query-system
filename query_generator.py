"""
Query Generator for AI Threat Hunting System

This module generates executable SQL queries from natural language threat hunting hypotheses
using OpenAI's GPT-4 with chain-of-thought reasoning and self-reflection.
"""

import os
import json
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, asdict
import openai
from openai import OpenAI


@dataclass
class QueryExplanation:
    """Structured explanation for generated queries"""
    hypothesis_interpretation: str
    query_reasoning: str
    assumptions: List[str]
    confidence_score: float
    key_fields_used: List[str]


@dataclass
class GeneratedQuery:
    """Container for generated query with metadata"""
    hypothesis_id: str
    hypothesis_name: str
    hypothesis_text: str
    sql_query: str
    explanation: QueryExplanation
    raw_response: str


class QueryGenerator:
    """
    Generates SQL queries from threat hunting hypotheses using LLM.
    
    Features:
    - Chain-of-thought reasoning
    - Self-reflection and validation
    - Confidence scoring
    - Explainable outputs
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        """
        Initialize the query generator.
        
        Args:
            api_key: OpenAI API key (if None, reads from environment)
            model: OpenAI model to use
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.schema_info = self._get_cloudtrail_schema()
        
    def _get_cloudtrail_schema(self) -> str:
        """Return CloudTrail schema information for query generation"""
        return """
CloudTrail Dataset Schema (nineteenFeaturesDf.csv):

Key Columns:
- eventTime: Timestamp of the event (ISO 8601 format)
- eventName: Name of the API action (e.g., ConsoleLogin, GetCallerIdentity, RunInstances)
- eventSource: AWS service that was called (e.g., signin.amazonaws.com, sts.amazonaws.com)
- sourceIPAddress: IP address from which the request was made
- userAgent: User agent string of the requester
- errorCode: Error code if the request failed (e.g., AccessDenied, UnauthorizedOperation)
- errorMessage: Human-readable error message
- awsRegion: AWS region where the event occurred
- userIdentitytype: Type of identity (Root, IAMUser, AssumedRole, etc.)
- userIdentityuserName: Username or role name
- userIdentityarn: ARN of the identity
- userIdentityaccountId: AWS account ID
- requestParametersinstanceType: EC2 instance type for RunInstances events
- requestParametersbucketName: S3 bucket name for S3 operations
- responseElementsaccessKeyId: Access key ID created in CreateAccessKey events

Common Event Names:
- ConsoleLogin: User logging into AWS console
- GetCallerIdentity: STS API call to get identity information
- StopLogging/DeleteTrail: CloudTrail disruption attempts
- RunInstances: EC2 instance creation
- GetSecretValue: Secrets Manager access
- CreateAccessKey: IAM access key creation
- GetBucketAcl: S3 bucket ACL retrieval

Query Guidelines:
- Use DuckDB SQL syntax
- Table name is 'cloudtrail_logs'
- For console login failures, check eventName='ConsoleLogin' AND errorMessage IS NOT NULL
- For root access, check userIdentitytype='Root'
- For unauthorized access, check errorCode IN ('AccessDenied', 'UnauthorizedOperation')
- User agent checks are case-insensitive (use LOWER())
- Instance type patterns like '10xlarge' or bigger should use LIKE '%xlarge%' and size filtering
"""

    def _build_system_prompt(self) -> str:
        """Build the system prompt for the LLM"""
        return f"""You are an expert AWS security analyst specializing in threat hunting using CloudTrail logs.
Your task is to generate precise DuckDB SQL queries that identify security threats from CloudTrail data.

{self.schema_info}

When generating queries, follow this structured approach:

1. INTERPRET THE HYPOTHESIS
   - What specific threat or behavior is being detected?
   - What are the key indicators?

2. IDENTIFY RELEVANT FIELDS
   - Which CloudTrail fields are needed?
   - What filters or conditions apply?

3. GENERATE THE QUERY
   - Write clean, efficient DuckDB SQL
   - Include appropriate WHERE clauses
   - Order results by eventTime when relevant
   - Limit results if appropriate

4. EXPLAIN YOUR REASONING
   - Why did you structure the query this way?
   - What assumptions did you make?
   - How confident are you (0.0-1.0)?

5. OUTPUT FORMAT
   Return a JSON object with this structure:
   {{
     "interpretation": "What this hypothesis is looking for...",
     "reasoning": "I structured the query this way because...",
     "assumptions": ["assumption 1", "assumption 2"],
     "confidence": 0.85,
     "key_fields": ["field1", "field2"],
     "sql_query": "SELECT ... FROM cloudtrail_logs WHERE ..."
   }}

IMPORTANT:
- Use DuckDB SQL syntax (standard SQL with some extensions)
- Table name is always 'cloudtrail_logs'
- Return ONLY valid JSON, no markdown formatting
- Ensure SQL is syntactically correct
- Be specific with conditions (avoid overly broad queries)
"""

    def _build_user_prompt(self, hypothesis: Dict[str, str]) -> str:
        """Build the user prompt with the hypothesis"""
        return f"""Generate a SQL query for this threat hunting hypothesis:

ID: {hypothesis['id']}
Name: {hypothesis['name']}
Hypothesis: {hypothesis['hypothesis']}

Analyze the hypothesis and generate an appropriate SQL query following the structured approach.
Return only the JSON object with your analysis and query.
"""

    def generate_query(self, hypothesis: Dict[str, str]) -> GeneratedQuery:
        """
        Generate a SQL query from a hypothesis.
        
        Args:
            hypothesis: Dictionary with 'id', 'name', and 'hypothesis' keys
            
        Returns:
            GeneratedQuery object with query and explanation
        """
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": self._build_user_prompt(hypothesis)}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,  # Low temperature for consistency
                max_tokens=2000
            )
            
            raw_response = response.choices[0].message.content
            
            # Parse JSON response
            # Remove markdown code blocks if present
            cleaned_response = raw_response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            result = json.loads(cleaned_response)
            
            explanation = QueryExplanation(
                hypothesis_interpretation=result.get("interpretation", ""),
                query_reasoning=result.get("reasoning", ""),
                assumptions=result.get("assumptions", []),
                confidence_score=result.get("confidence", 0.0),
                key_fields_used=result.get("key_fields", [])
            )
            
            return GeneratedQuery(
                hypothesis_id=hypothesis['id'],
                hypothesis_name=hypothesis['name'],
                hypothesis_text=hypothesis['hypothesis'],
                sql_query=result.get("sql_query", ""),
                explanation=explanation,
                raw_response=raw_response
            )
            
        except json.JSONDecodeError as e:
            # Fallback: try to extract SQL from response
            print(f"JSON parsing failed for hypothesis {hypothesis['id']}: {e}")
            print(f"Raw response: {raw_response[:200]}...")
            
            # Return a minimal valid response
            return GeneratedQuery(
                hypothesis_id=hypothesis['id'],
                hypothesis_name=hypothesis['name'],
                hypothesis_text=hypothesis['hypothesis'],
                sql_query="SELECT * FROM cloudtrail_logs LIMIT 10",  # Fallback query
                explanation=QueryExplanation(
                    hypothesis_interpretation="Failed to parse LLM response",
                    query_reasoning="Error occurred during generation",
                    assumptions=[],
                    confidence_score=0.0,
                    key_fields_used=[]
                ),
                raw_response=raw_response
            )
            
        except Exception as e:
            print(f"Error generating query for hypothesis {hypothesis['id']}: {e}")
            raise

    def generate_batch(self, hypotheses: List[Dict[str, str]]) -> List[GeneratedQuery]:
        """
        Generate queries for multiple hypotheses.
        
        Args:
            hypotheses: List of hypothesis dictionaries
            
        Returns:
            List of GeneratedQuery objects
        """
        results = []
        for i, hypothesis in enumerate(hypotheses):
            print(f"Generating query {i+1}/{len(hypotheses)}: {hypothesis['name']}")
            try:
                query = self.generate_query(hypothesis)
                results.append(query)
            except Exception as e:
                print(f"Failed to generate query for {hypothesis['id']}: {e}")
                # Continue with next hypothesis
                
        return results

    def save_queries(self, queries: List[GeneratedQuery], output_path: str):
        """
        Save generated queries to a JSON file.
        
        Args:
            queries: List of GeneratedQuery objects
            output_path: Path to output file
        """
        output = []
        for query in queries:
            output.append({
                "hypothesis_id": query.hypothesis_id,
                "hypothesis_name": query.hypothesis_name,
                "hypothesis_text": query.hypothesis_text,
                "sql_query": query.sql_query,
                "explanation": asdict(query.explanation)
            })
        
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"Saved {len(queries)} queries to {output_path}")


def load_hypotheses(file_path: str) -> List[Dict[str, str]]:
    """Load hypotheses from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)


if __name__ == "__main__":
    # Example usage
    hypotheses = load_hypotheses("../assignment/hypotheses.json")
    
    generator = QueryGenerator()
    queries = generator.generate_batch(hypotheses)
    generator.save_queries(queries, "generated_queries.json")
    
    # Print first query as example
    if queries:
        q = queries[0]
        print(f"\n{'='*80}")
        print(f"Example Query for: {q.hypothesis_name}")
        print(f"{'='*80}")
        print(f"\nInterpretation: {q.explanation.hypothesis_interpretation}")
        print(f"\nSQL Query:\n{q.sql_query}")
        print(f"\nConfidence: {q.explanation.confidence_score}")

