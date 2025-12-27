"""
Evaluation Framework for Query Generation System

This module provides comprehensive evaluation metrics to assess the quality
of generated queries and their results against expected outcomes.
"""

import json
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
import pandas as pd
import duckdb
from sklearn.metrics import precision_score, recall_score, f1_score
import numpy as np


@dataclass
class HypothesisEvaluation:
    """Evaluation results for a single hypothesis"""
    hypothesis_id: str
    hypothesis_name: str
    
    # Syntactic metrics
    query_valid: bool
    query_error: str = ""
    
    # Result metrics
    expected_count: int = 0
    actual_count: int = 0
    
    # Set-based metrics
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    
    # Overlap metrics
    exact_match_rate: float = 0.0
    partial_match_rate: float = 0.0
    
    # Completeness
    missing_records: int = 0
    extra_records: int = 0
    
    # Overall score
    overall_score: float = 0.0
    
    # Additional info
    notes: str = ""


@dataclass
class EvaluationReport:
    """Complete evaluation report"""
    total_hypotheses: int
    successful_queries: int
    failed_queries: int
    
    avg_precision: float
    avg_recall: float
    avg_f1: float
    avg_overall_score: float
    
    hypothesis_results: List[HypothesisEvaluation]
    
    # Before/after tracking
    iteration: int = 1
    improvements: str = ""


class QueryEvaluator:
    """
    Evaluates generated queries against expected outcomes.
    
    Metrics:
    1. Query Validity: Does the query execute without errors?
    2. Result Count: How many records are returned?
    3. Precision: What fraction of returned records are correct?
    4. Recall: What fraction of expected records are found?
    5. F1 Score: Harmonic mean of precision and recall
    """
    
    def __init__(self, data_path: str):
        """
        Initialize evaluator with CloudTrail data.
        
        Args:
            data_path: Path to CloudTrail CSV file
        """
        self.data_path = data_path
        self.conn = None
        self._setup_database()
        
    def _setup_database(self):
        """Setup DuckDB with CloudTrail data"""
        print(f"Loading CloudTrail data from {self.data_path}...")
        self.conn = duckdb.connect(':memory:')
        
        # Load data and create table with explicit type handling
        # Some fields like userIdentityaccountId can be both numeric and string (e.g., ANONYMOUS_PRINCIPAL)
        self.conn.execute(f"""
            CREATE TABLE cloudtrail_logs AS 
            SELECT * FROM read_csv_auto('{self.data_path}', 
                sample_size=-1,
                all_varchar=1)
        """)
        
        # Get record count
        count = self.conn.execute("SELECT COUNT(*) FROM cloudtrail_logs").fetchone()[0]
        print(f"Loaded {count:,} CloudTrail records")
        
    def execute_query(self, sql_query: str) -> Tuple[bool, pd.DataFrame, str]:
        """
        Execute a SQL query and return results.
        
        Args:
            sql_query: SQL query to execute
            
        Returns:
            Tuple of (success, results_df, error_message)
        """
        try:
            result = self.conn.execute(sql_query).fetchdf()
            return True, result, ""
        except Exception as e:
            return False, pd.DataFrame(), str(e)
    
    def _normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize dataframe for comparison"""
        if df.empty:
            return df
        
        # Sort columns alphabetically
        df = df.reindex(sorted(df.columns), axis=1)
        
        # Reset index
        df = df.reset_index(drop=True)
        
        # Sort by all columns to ensure consistent ordering
        if not df.empty:
            try:
                df = df.sort_values(by=list(df.columns)).reset_index(drop=True)
            except:
                pass  # Skip if sorting fails
        
        return df
    
    def _create_record_key(self, row: pd.Series) -> str:
        """Create a unique key from a dataframe row"""
        # Use first few columns or primary key fields
        key_fields = []
        
        # Prioritize key CloudTrail fields
        priority_fields = ['eventID', 'eventTime', 'eventName', 'sourceIPAddress', 'userIdentityuserName']
        
        for field in priority_fields:
            if field in row.index and pd.notna(row[field]):
                key_fields.append(f"{field}:{row[field]}")
        
        # If no priority fields, use all fields
        if not key_fields:
            for col, val in row.items():
                if pd.notna(val):
                    key_fields.append(f"{col}:{val}")
        
        return "|".join(key_fields)
    
    def _compare_results(self, expected: pd.DataFrame, actual: pd.DataFrame) -> Dict[str, float]:
        """
        Compare expected and actual results using set-based metrics.
        
        Args:
            expected: Expected results from hypotheses_outcomes.json
            actual: Actual query results
            
        Returns:
            Dictionary with precision, recall, f1, and other metrics
        """
        if expected.empty and actual.empty:
            return {
                'precision': 1.0,
                'recall': 1.0,
                'f1': 1.0,
                'exact_match_rate': 1.0,
                'missing': 0,
                'extra': 0
            }
        
        if expected.empty:
            return {
                'precision': 0.0,
                'recall': 0.0 if actual.empty else 1.0,  # No expected records, so recall is perfect if no results
                'f1': 0.0,
                'exact_match_rate': 0.0,
                'missing': 0,
                'extra': len(actual)
            }
        
        if actual.empty:
            return {
                'precision': 0.0,
                'recall': 0.0,
                'f1': 0.0,
                'exact_match_rate': 0.0,
                'missing': len(expected),
                'extra': 0
            }
        
        # Create sets of record keys for comparison
        expected_keys = set(expected.apply(self._create_record_key, axis=1))
        actual_keys = set(actual.apply(self._create_record_key, axis=1))
        
        # Calculate set-based metrics
        true_positives = len(expected_keys & actual_keys)
        false_positives = len(actual_keys - expected_keys)
        false_negatives = len(expected_keys - actual_keys)
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        exact_match_rate = true_positives / len(expected_keys) if len(expected_keys) > 0 else 0.0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'exact_match_rate': exact_match_rate,
            'missing': false_negatives,
            'extra': false_positives
        }
    
    def evaluate_hypothesis(
        self, 
        hypothesis_id: str, 
        hypothesis_name: str,
        sql_query: str, 
        expected_results: pd.DataFrame
    ) -> HypothesisEvaluation:
        """
        Evaluate a single hypothesis query.
        
        Args:
            hypothesis_id: Hypothesis ID
            hypothesis_name: Hypothesis name
            sql_query: Generated SQL query
            expected_results: Expected results from outcomes file
            
        Returns:
            HypothesisEvaluation object
        """
        # Execute query
        success, actual_results, error = self.execute_query(sql_query)
        
        if not success:
            return HypothesisEvaluation(
                hypothesis_id=hypothesis_id,
                hypothesis_name=hypothesis_name,
                query_valid=False,
                query_error=error,
                expected_count=len(expected_results) if not expected_results.empty else 0,
                actual_count=0,
                overall_score=0.0,
                notes="Query execution failed"
            )
        
        # Compare results
        metrics = self._compare_results(expected_results, actual_results)
        
        # Calculate overall score (weighted average)
        overall_score = (
            0.3 * metrics['precision'] + 
            0.3 * metrics['recall'] + 
            0.4 * metrics['f1']
        )
        
        return HypothesisEvaluation(
            hypothesis_id=hypothesis_id,
            hypothesis_name=hypothesis_name,
            query_valid=True,
            expected_count=len(expected_results),
            actual_count=len(actual_results),
            precision=metrics['precision'],
            recall=metrics['recall'],
            f1_score=metrics['f1'],
            exact_match_rate=metrics['exact_match_rate'],
            missing_records=metrics['missing'],
            extra_records=metrics['extra'],
            overall_score=overall_score,
            notes=f"Found {len(actual_results)} records, expected {len(expected_results)}"
        )
    
    def evaluate_batch(
        self, 
        generated_queries: List[Dict[str, Any]], 
        expected_outcomes: Dict[str, pd.DataFrame]
    ) -> EvaluationReport:
        """
        Evaluate multiple queries.
        
        Args:
            generated_queries: List of generated query dicts
            expected_outcomes: Dict mapping hypothesis_id to expected results DataFrame
            
        Returns:
            EvaluationReport object
        """
        results = []
        successful = 0
        failed = 0
        
        for query_data in generated_queries:
            hypothesis_id = query_data['hypothesis_id']
            hypothesis_name = query_data['hypothesis_name']
            sql_query = query_data['sql_query']
            
            # Get expected results
            expected = expected_outcomes.get(hypothesis_id, pd.DataFrame())
            
            print(f"Evaluating hypothesis {hypothesis_id}: {hypothesis_name}")
            
            eval_result = self.evaluate_hypothesis(
                hypothesis_id, 
                hypothesis_name,
                sql_query, 
                expected
            )
            
            results.append(eval_result)
            
            if eval_result.query_valid:
                successful += 1
            else:
                failed += 1
        
        # Calculate aggregate metrics
        valid_results = [r for r in results if r.query_valid]
        
        avg_precision = np.mean([r.precision for r in valid_results]) if valid_results else 0.0
        avg_recall = np.mean([r.recall for r in valid_results]) if valid_results else 0.0
        avg_f1 = np.mean([r.f1_score for r in valid_results]) if valid_results else 0.0
        avg_overall = np.mean([r.overall_score for r in results])
        
        return EvaluationReport(
            total_hypotheses=len(results),
            successful_queries=successful,
            failed_queries=failed,
            avg_precision=avg_precision,
            avg_recall=avg_recall,
            avg_f1=avg_f1,
            avg_overall_score=avg_overall,
            hypothesis_results=results
        )
    
    def save_evaluation(self, report: EvaluationReport, output_path: str):
        """Save evaluation report to JSON file"""
        output = {
            'summary': {
                'total_hypotheses': report.total_hypotheses,
                'successful_queries': report.successful_queries,
                'failed_queries': report.failed_queries,
                'avg_precision': report.avg_precision,
                'avg_recall': report.avg_recall,
                'avg_f1': report.avg_f1,
                'avg_overall_score': report.avg_overall_score,
                'iteration': report.iteration,
                'improvements': report.improvements
            },
            'results': [asdict(r) for r in report.hypothesis_results]
        }
        
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\nSaved evaluation report to {output_path}")
    
    def print_summary(self, report: EvaluationReport):
        """Print evaluation summary to console"""
        print("\n" + "="*80)
        print("EVALUATION SUMMARY")
        print("="*80)
        print(f"\nTotal Hypotheses: {report.total_hypotheses}")
        print(f"Successful Queries: {report.successful_queries}")
        print(f"Failed Queries: {report.failed_queries}")
        print(f"\nAverage Metrics:")
        print(f"  Precision: {report.avg_precision:.3f}")
        print(f"  Recall:    {report.avg_recall:.3f}")
        print(f"  F1 Score:  {report.avg_f1:.3f}")
        print(f"  Overall:   {report.avg_overall_score:.3f}")
        
        print(f"\n{'='*80}")
        print("PER-HYPOTHESIS RESULTS")
        print("="*80)
        
        for result in report.hypothesis_results:
            status = "✓" if result.query_valid else "✗"
            print(f"\n{status} [{result.hypothesis_id}] {result.hypothesis_name}")
            
            if result.query_valid:
                print(f"   Expected: {result.expected_count}, Actual: {result.actual_count}")
                print(f"   P={result.precision:.2f} R={result.recall:.2f} F1={result.f1_score:.2f} Score={result.overall_score:.2f}")
                if result.missing_records > 0 or result.extra_records > 0:
                    print(f"   Missing: {result.missing_records}, Extra: {result.extra_records}")
            else:
                print(f"   Error: {result.query_error[:100]}")
        
        print("\n" + "="*80)
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    # Example usage
    from utils import load_hypotheses_outcomes
    
    # Load data
    evaluator = QueryEvaluator("data/nineteenFeaturesDf.csv")
    
    # Load generated queries
    with open("generated_queries.json", 'r') as f:
        generated_queries = json.load(f)
    
    # Load expected outcomes
    expected_outcomes = load_hypotheses_outcomes("../assignment/hypotheses_outcomes.json")
    
    # Run evaluation
    report = evaluator.evaluate_batch(generated_queries, expected_outcomes)
    evaluator.print_summary(report)
    evaluator.save_evaluation(report, "evaluation_results.json")
    
    evaluator.close()

