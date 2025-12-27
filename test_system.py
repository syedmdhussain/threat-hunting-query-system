"""
Basic unit tests for the threat hunting query system
Run with: pytest test_system.py
"""

import pytest
import pandas as pd
import json
from pathlib import Path


def test_imports():
    """Test that all modules can be imported"""
    try:
        from query_generator import QueryGenerator, load_hypotheses
        from evaluator import QueryEvaluator
        from utils import load_hypotheses_outcomes
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


def test_load_hypotheses():
    """Test loading hypotheses from JSON"""
    from query_generator import load_hypotheses
    
    # Create a test hypothesis file
    test_data = [
        {
            "id": "test1",
            "name": "Test Hypothesis",
            "hypothesis": "This is a test hypothesis"
        }
    ]
    
    test_file = "test_hypotheses.json"
    with open(test_file, 'w') as f:
        json.dump(test_data, f)
    
    try:
        hypotheses = load_hypotheses(test_file)
        assert len(hypotheses) == 1
        assert hypotheses[0]['id'] == 'test1'
        assert hypotheses[0]['name'] == 'Test Hypothesis'
    finally:
        Path(test_file).unlink(missing_ok=True)


def test_query_generator_initialization():
    """Test QueryGenerator can be initialized"""
    from query_generator import QueryGenerator
    
    # This should work even without API key (won't make requests)
    try:
        generator = QueryGenerator(api_key="test-key")
        assert generator.model == "gpt-4o"
    except ValueError:
        # Expected if no API key provided
        pass


def test_query_explanation_dataclass():
    """Test QueryExplanation dataclass"""
    from query_generator import QueryExplanation
    
    explanation = QueryExplanation(
        hypothesis_interpretation="Test interpretation",
        query_reasoning="Test reasoning",
        assumptions=["assumption1", "assumption2"],
        confidence_score=0.85,
        key_fields_used=["field1", "field2"]
    )
    
    assert explanation.confidence_score == 0.85
    assert len(explanation.assumptions) == 2
    assert "field1" in explanation.key_fields_used


def test_evaluator_initialization():
    """Test evaluator initialization with mock data"""
    from evaluator import QueryEvaluator
    
    # Create a minimal test CSV
    test_csv = "test_data.csv"
    df = pd.DataFrame({
        'eventTime': ['2023-01-01T00:00:00Z'],
        'eventName': ['TestEvent'],
        'sourceIPAddress': ['1.2.3.4']
    })
    df.to_csv(test_csv, index=False)
    
    try:
        evaluator = QueryEvaluator(test_csv)
        assert evaluator.conn is not None
        evaluator.close()
    finally:
        Path(test_csv).unlink(missing_ok=True)


def test_evaluator_query_execution():
    """Test query execution"""
    from evaluator import QueryEvaluator
    
    # Create test data
    test_csv = "test_data.csv"
    df = pd.DataFrame({
        'eventTime': ['2023-01-01T00:00:00Z', '2023-01-02T00:00:00Z'],
        'eventName': ['ConsoleLogin', 'GetCallerIdentity'],
        'sourceIPAddress': ['1.2.3.4', '5.6.7.8']
    })
    df.to_csv(test_csv, index=False)
    
    try:
        evaluator = QueryEvaluator(test_csv)
        
        # Test valid query
        success, results, error = evaluator.execute_query(
            "SELECT * FROM cloudtrail_logs WHERE eventName = 'ConsoleLogin'"
        )
        
        assert success is True
        assert len(results) == 1
        assert results.iloc[0]['eventName'] == 'ConsoleLogin'
        
        # Test invalid query
        success, results, error = evaluator.execute_query(
            "SELECT * FROM nonexistent_table"
        )
        
        assert success is False
        assert error != ""
        
        evaluator.close()
    finally:
        Path(test_csv).unlink(missing_ok=True)


def test_hypothesis_evaluation_dataclass():
    """Test HypothesisEvaluation dataclass"""
    from evaluator import HypothesisEvaluation
    
    eval_result = HypothesisEvaluation(
        hypothesis_id="1",
        hypothesis_name="Test",
        query_valid=True,
        expected_count=10,
        actual_count=8,
        precision=0.9,
        recall=0.8,
        f1_score=0.85,
        overall_score=0.85
    )
    
    assert eval_result.query_valid is True
    assert eval_result.f1_score == 0.85


def test_record_comparison():
    """Test record comparison logic"""
    from evaluator import QueryEvaluator
    
    # Create test data
    test_csv = "test_data.csv"
    df = pd.DataFrame({
        'eventTime': ['2023-01-01T00:00:00Z'],
        'eventName': ['TestEvent']
    })
    df.to_csv(test_csv, index=False)
    
    try:
        evaluator = QueryEvaluator(test_csv)
        
        # Test with matching DataFrames
        df1 = pd.DataFrame({'a': [1, 2, 3], 'b': ['x', 'y', 'z']})
        df2 = pd.DataFrame({'a': [1, 2, 3], 'b': ['x', 'y', 'z']})
        
        metrics = evaluator._compare_results(df1, df2)
        
        # Perfect match should have high scores
        assert metrics['precision'] >= 0.8
        assert metrics['recall'] >= 0.8
        
        # Test with partial match
        df3 = pd.DataFrame({'a': [1, 2], 'b': ['x', 'y']})
        metrics = evaluator._compare_results(df1, df3)
        
        # Should have lower recall (missing records)
        assert metrics['recall'] < 1.0
        
        evaluator.close()
    finally:
        Path(test_csv).unlink(missing_ok=True)


def test_cloudtrail_schema():
    """Test that schema information is available"""
    from query_generator import QueryGenerator
    
    generator = QueryGenerator(api_key="test-key")
    schema = generator._get_cloudtrail_schema()
    
    # Check that key fields are mentioned
    assert "eventTime" in schema
    assert "eventName" in schema
    assert "sourceIPAddress" in schema
    assert "ConsoleLogin" in schema


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

