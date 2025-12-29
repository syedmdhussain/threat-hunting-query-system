"""
Main Entry Point for AI Threat Hunting Query Generation & Evaluation System

This script orchestrates the complete pipeline:
1. Load hypotheses
2. Generate SQL queries using LLM
3. Evaluate queries against expected outcomes
4. Generate comprehensive reports
"""

import os
import sys
import argparse
import json
from pathlib import Path

from query_generator import QueryGenerator, load_hypotheses
from evaluator import QueryEvaluator
from utils import load_hypotheses_outcomes


def main():
    parser = argparse.ArgumentParser(
        description="AI Threat Hunting Query Generation & Evaluation System"
    )
    
    parser.add_argument(
        '--hypotheses',
        type=str,
        default='../assignment/hypotheses.json',
        help='Path to hypotheses JSON file'
    )
    
    parser.add_argument(
        '--outcomes',
        type=str,
        default='../assignment/hypotheses_outcomes.json',
        help='Path to expected outcomes JSON file'
    )
    
    parser.add_argument(
        '--data',
        type=str,
        required=True,
        help='Path to CloudTrail CSV file (nineteenFeaturesDf.csv)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./output',
        help='Directory for output files'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='gpt-4o',
        help='OpenAI model to use (default: gpt-4o)'
    )
    
    parser.add_argument(
        '--skip-generation',
        action='store_true',
        help='Skip query generation and use existing generated_queries.json'
    )
    
    parser.add_argument(
        '--iteration',
        type=int,
        default=1,
        help='Iteration number for tracking improvements'
    )
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Check API key
    if not args.skip_generation and not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Set it with: export OPENAI_API_KEY='your-api-key'")
        sys.exit(1)
    
    print("="*80)
    print("AI THREAT HUNTING QUERY GENERATION & EVALUATION SYSTEM")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  Hypotheses: {args.hypotheses}")
    print(f"  Expected Outcomes: {args.outcomes}")
    print(f"  CloudTrail Data: {args.data}")
    print(f"  Output Directory: {args.output_dir}")
    print(f"  Model: {args.model}")
    print(f"  Iteration: {args.iteration}")
    print()
    
    # Step 1: Load hypotheses
    print("\n[STEP 1] Loading hypotheses...")
    hypotheses = load_hypotheses(args.hypotheses)
    print(f"Loaded {len(hypotheses)} hypotheses")
    
    # Step 2: Generate queries (or load existing)
    queries_file = output_dir / "generated_queries.json"
    
    if args.skip_generation and queries_file.exists():
        print("\n[STEP 2] Loading existing generated queries...")
        with open(queries_file, 'r') as f:
            generated_queries = json.load(f)
        print(f"Loaded {len(generated_queries)} queries from {queries_file}")
    else:
        print("\n[STEP 2] Generating SQL queries from hypotheses...")
        generator = QueryGenerator(model=args.model, data_path=args.data)
        query_objects = generator.generate_batch(hypotheses)
        
        # Save queries
        generator.save_queries(query_objects, str(queries_file))
        
        # Load back as JSON for evaluation
        with open(queries_file, 'r') as f:
            generated_queries = json.load(f)
    
    # Step 3: Load expected outcomes
    print("\n[STEP 3] Loading expected outcomes...")
    expected_outcomes = load_hypotheses_outcomes(args.outcomes)
    print(f"Loaded expected outcomes for {len(expected_outcomes)} hypotheses")
    
    # Step 4: Evaluate queries
    print("\n[STEP 4] Evaluating generated queries...")
    evaluator = QueryEvaluator(args.data)
    report = evaluator.evaluate_batch(generated_queries, expected_outcomes)
    report.iteration = args.iteration
    
    # Step 5: Generate and save reports
    print("\n[STEP 5] Generating evaluation report...")
    
    # Save JSON report
    eval_file = output_dir / f"evaluation_results_iter{args.iteration}.json"
    evaluator.save_evaluation(report, str(eval_file))
    
    # Print summary
    evaluator.print_summary(report)
    
    # Generate markdown report
    generate_markdown_report(report, output_dir / f"EVALUATION_REPORT_ITER{args.iteration}.md")
    
    # Cleanup
    evaluator.close()
    
    print("\n" + "="*80)
    print("PIPELINE COMPLETE!")
    print("="*80)
    print(f"\nGenerated files:")
    print(f"  - {queries_file}")
    print(f"  - {eval_file}")
    print(f"  - {output_dir}/EVALUATION_REPORT_ITER{args.iteration}.md")
    print()
    
    # Return exit code based on success
    success_rate = report.successful_queries / report.total_hypotheses
    if success_rate >= 0.8:
        print("✓ Success rate >= 80%")
        return 0
    else:
        print(f"⚠ Success rate {success_rate:.1%} is below 80%")
        return 1


def generate_markdown_report(report, output_path: Path):
    """Generate a detailed markdown evaluation report"""
    
    with open(output_path, 'w') as f:
        f.write("# Evaluation Report - AI Threat Hunting Query Generation\n\n")
        
        # Summary section
        f.write("## Summary\n\n")
        f.write(f"**Iteration:** {report.iteration}\n\n")
        f.write(f"- **Total Hypotheses:** {report.total_hypotheses}\n")
        f.write(f"- **Successful Queries:** {report.successful_queries}\n")
        f.write(f"- **Failed Queries:** {report.failed_queries}\n")
        f.write(f"- **Success Rate:** {report.successful_queries/report.total_hypotheses*100:.1f}%\n\n")
        
        # Metrics table
        f.write("### Overall Metrics\n\n")
        f.write("| Metric | Score |\n")
        f.write("|--------|-------|\n")
        f.write(f"| Precision | {report.avg_precision:.3f} |\n")
        f.write(f"| Recall | {report.avg_recall:.3f} |\n")
        f.write(f"| F1 Score | {report.avg_f1:.3f} |\n")
        f.write(f"| Overall Score | {report.avg_overall_score:.3f} |\n\n")
        
        # Per-hypothesis results
        f.write("## Per-Hypothesis Results\n\n")
        
        for result in report.hypothesis_results:
            status_emoji = "✅" if result.query_valid else "❌"
            f.write(f"### {status_emoji} [{result.hypothesis_id}] {result.hypothesis_name}\n\n")
            
            if result.query_valid:
                f.write("**Metrics:**\n")
                f.write(f"- Expected Records: {result.expected_count}\n")
                f.write(f"- Actual Records: {result.actual_count}\n")
                f.write(f"- Precision: {result.precision:.3f}\n")
                f.write(f"- Recall: {result.recall:.3f}\n")
                f.write(f"- F1 Score: {result.f1_score:.3f}\n")
                f.write(f"- Overall Score: {result.overall_score:.3f}\n\n")
                
                if result.missing_records > 0 or result.extra_records > 0:
                    f.write("**Discrepancies:**\n")
                    f.write(f"- Missing Records: {result.missing_records}\n")
                    f.write(f"- Extra Records: {result.extra_records}\n\n")
                
                # Performance assessment
                if result.f1_score >= 0.9:
                    f.write("**Assessment:** Excellent performance ✨\n\n")
                elif result.f1_score >= 0.7:
                    f.write("**Assessment:** Good performance ✓\n\n")
                elif result.f1_score >= 0.5:
                    f.write("**Assessment:** Moderate performance ⚠️\n\n")
                else:
                    f.write("**Assessment:** Needs improvement ⚠️⚠️\n\n")
            else:
                f.write(f"**Error:** Query execution failed\n\n")
                f.write(f"```\n{result.query_error}\n```\n\n")
        
        # Failure analysis
        failed = [r for r in report.hypothesis_results if not r.query_valid]
        if failed:
            f.write("## Failure Analysis\n\n")
            f.write(f"The following {len(failed)} queries failed to execute:\n\n")
            for result in failed:
                f.write(f"- **{result.hypothesis_id}**: {result.hypothesis_name}\n")
                f.write(f"  - Error: {result.query_error[:200]}\n\n")
        
        # Recommendations
        f.write("## Recommendations\n\n")
        
        low_performers = [r for r in report.hypothesis_results if r.query_valid and r.f1_score < 0.7]
        if low_performers:
            f.write("### Queries Needing Improvement\n\n")
            for result in low_performers:
                f.write(f"- **{result.hypothesis_id}**: {result.hypothesis_name} (F1={result.f1_score:.2f})\n")
            f.write("\n")
        
        if report.avg_f1 < 0.8:
            f.write("### General Improvements\n\n")
            f.write("- Review and refine prompt engineering strategies\n")
            f.write("- Add more examples for low-performing hypothesis types\n")
            f.write("- Implement query validation before execution\n")
            f.write("- Consider multi-step reasoning for complex hypotheses\n\n")
    
    print(f"Generated markdown report: {output_path}")


if __name__ == "__main__":
    sys.exit(main())

