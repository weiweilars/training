#!/usr/bin/env python3
"""
Assessment Agent - Results Analysis MCP Server
Focused on scoring analysis, performance metrics, and assessment reporting
Port: 8103
"""

try:
    from fastmcp import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    class FastMCP:
        def __init__(self, name):
            self.name = name
        def tool(self):
            def decorator(func):
                return func
            return decorator
        def run(self, **kwargs):
            print("FastMCP fallback - demo mode")

import json
import uuid
from datetime import datetime
import random
import statistics

mcp = FastMCP(name="results-analysis")

# Results database
assessment_results_db = {}
scoring_analytics_db = {}

@mcp.tool()
def analyze_assessment_results(
    assessment_id: str,
    candidate_responses: str,
    time_spent_minutes: int,
    submission_timestamp: str = ""
) -> str:
    """
    Perform comprehensive analysis of assessment results
    
    Args:
        assessment_id: Assessment instance ID
        candidate_responses: JSON with candidate's answers
        time_spent_minutes: Total time spent on assessment
        submission_timestamp: When assessment was submitted (ISO format)
    """
    
    try:
        responses = json.loads(candidate_responses)
    except json.JSONDecodeError:
        return json.dumps({"success": False, "error": "Invalid JSON in candidate responses"})
    
    analysis_id = str(uuid.uuid4())[:8]
    
    if not submission_timestamp:
        submission_timestamp = datetime.now().isoformat()
    
    # Mock assessment data (in real implementation, retrieve from assessment_library)
    mock_assessment = {
        "total_questions": len(responses),
        "total_points": len(responses) * 10,
        "passing_score": 70,
        "categories": ["technical_skills", "problem_solving", "code_quality"]
    }
    
    # Calculate scores
    correct_answers = 0
    category_scores = {}
    question_analysis = []
    
    for i, (question_id, response) in enumerate(responses.items()):
        # Mock scoring logic
        is_correct = random.random() > 0.3  # 70% correct rate
        if is_correct:
            correct_answers += 1
        
        points_earned = 10 if is_correct else random.randint(2, 6)
        category = random.choice(mock_assessment["categories"])
        
        question_analysis.append({
            "question_id": question_id,
            "question_number": i + 1,
            "candidate_response": response,
            "correct": is_correct,
            "points_earned": points_earned,
            "max_points": 10,
            "category": category,
            "time_spent": random.randint(2, 8),
            "difficulty_level": random.choice(["junior", "mid", "senior"])
        })
        
        # Update category scores
        if category not in category_scores:
            category_scores[category] = {"earned": 0, "total": 0, "questions": 0}
        
        category_scores[category]["earned"] += points_earned
        category_scores[category]["total"] += 10
        category_scores[category]["questions"] += 1
    
    # Calculate overall metrics
    total_points_earned = sum(q["points_earned"] for q in question_analysis)
    overall_percentage = (total_points_earned / mock_assessment["total_points"]) * 100
    
    # Performance analysis
    performance_metrics = {
        "overall_score": round(overall_percentage, 2),
        "points_earned": total_points_earned,
        "points_possible": mock_assessment["total_points"],
        "questions_correct": correct_answers,
        "questions_total": mock_assessment["total_questions"],
        "accuracy_rate": round((correct_answers / mock_assessment["total_questions"]) * 100, 2),
        "time_efficiency": calculate_time_efficiency(time_spent_minutes, mock_assessment["total_questions"]),
        "passed": overall_percentage >= mock_assessment["passing_score"]
    }
    
    # Category breakdown
    category_breakdown = {}
    for category, scores in category_scores.items():
        category_percentage = (scores["earned"] / scores["total"]) * 100
        category_breakdown[category] = {
            "score_percentage": round(category_percentage, 2),
            "points_earned": scores["earned"],
            "points_possible": scores["total"],
            "questions_count": scores["questions"],
            "performance_level": get_performance_level(category_percentage)
        }
    
    # Strengths and weaknesses
    strengths = []
    weaknesses = []
    
    for category, data in category_breakdown.items():
        if data["score_percentage"] >= 80:
            strengths.append(category)
        elif data["score_percentage"] < 60:
            weaknesses.append(category)
    
    analysis_result = {
        "analysis_id": analysis_id,
        "assessment_id": assessment_id,
        "candidate_performance": performance_metrics,
        "category_breakdown": category_breakdown,
        "question_by_question": question_analysis,
        "strengths": strengths,
        "areas_for_improvement": weaknesses,
        "time_analysis": {
            "total_time_minutes": time_spent_minutes,
            "average_time_per_question": round(time_spent_minutes / mock_assessment["total_questions"], 2),
            "time_efficiency_rating": performance_metrics["time_efficiency"]
        },
        "recommendations": generate_recommendations(category_breakdown, performance_metrics),
        "analyzed_at": datetime.now().isoformat(),
        "submission_timestamp": submission_timestamp
    }
    
    assessment_results_db[analysis_id] = analysis_result
    
    return json.dumps({
        "success": True,
        "analysis_id": analysis_id,
        "overall_result": "PASS" if performance_metrics["passed"] else "FAIL",
        "score": f"{performance_metrics['overall_score']}%",
        "detailed_analysis": analysis_result
    }, indent=2)

def calculate_time_efficiency(time_spent: int, total_questions: int) -> str:
    """Calculate time efficiency rating"""
    avg_time_per_question = time_spent / total_questions
    
    if avg_time_per_question < 2:
        return "Very Fast"
    elif avg_time_per_question < 4:
        return "Efficient"
    elif avg_time_per_question < 6:
        return "Adequate"
    elif avg_time_per_question < 8:
        return "Slow"
    else:
        return "Very Slow"

def get_performance_level(percentage: float) -> str:
    """Get performance level based on percentage"""
    if percentage >= 90:
        return "Excellent"
    elif percentage >= 80:
        return "Good"
    elif percentage >= 70:
        return "Satisfactory"
    elif percentage >= 60:
        return "Needs Improvement"
    else:
        return "Poor"

def generate_recommendations(category_breakdown: dict, performance_metrics: dict) -> list:
    """Generate recommendations based on performance"""
    recommendations = []
    
    if performance_metrics["overall_score"] >= 80:
        recommendations.append("Excellent performance - candidate demonstrates strong competency")
    elif performance_metrics["overall_score"] >= 70:
        recommendations.append("Good performance - candidate meets requirements with room for growth")
    else:
        recommendations.append("Performance below expectations - additional training may be needed")
    
    # Category-specific recommendations
    for category, data in category_breakdown.items():
        if data["score_percentage"] < 60:
            recommendations.append(f"Focus on improving {category.replace('_', ' ')} skills")
        elif data["score_percentage"] >= 90:
            recommendations.append(f"Strong expertise demonstrated in {category.replace('_', ' ')}")
    
    # Time-based recommendations
    if performance_metrics.get("time_efficiency") == "Very Fast":
        recommendations.append("Consider reviewing answers for accuracy - very fast completion time")
    elif performance_metrics.get("time_efficiency") == "Very Slow":
        recommendations.append("Work on time management and problem-solving efficiency")
    
    return recommendations

@mcp.tool()
def generate_comparative_analysis(
    candidate_results: str,
    comparison_group: str = "all_candidates",
    job_level: str = "mid"
) -> str:
    """
    Generate comparative analysis against peer group
    
    Args:
        candidate_results: JSON array of candidate result IDs to analyze
        comparison_group: Group to compare against (all_candidates, same_role, same_level)
        job_level: Job level for comparison (junior, mid, senior)
    """
    
    try:
        result_ids = json.loads(candidate_results)
    except json.JSONDecodeError:
        return json.dumps({"success": False, "error": "Invalid JSON in candidate results"})
    
    comparison_id = str(uuid.uuid4())[:8]
    
    # Mock comparative data
    comparison_stats = generate_mock_comparison_data(comparison_group, job_level)
    
    candidate_comparisons = []
    
    for result_id in result_ids:
        if result_id in assessment_results_db:
            result = assessment_results_db[result_id]
            candidate_score = result["candidate_performance"]["overall_score"]
            
            percentile = calculate_percentile(candidate_score, comparison_stats["score_distribution"])
            
            candidate_comparison = {
                "analysis_id": result_id,
                "candidate_score": candidate_score,
                "percentile": percentile,
                "performance_ranking": get_performance_ranking(percentile),
                "comparison_insights": generate_comparison_insights(candidate_score, comparison_stats),
                "category_comparisons": compare_categories(result["category_breakdown"], comparison_stats["category_averages"])
            }
            
            candidate_comparisons.append(candidate_comparison)
    
    comparative_analysis = {
        "comparison_id": comparison_id,
        "comparison_group": comparison_group,
        "job_level": job_level,
        "benchmark_data": comparison_stats,
        "candidate_comparisons": candidate_comparisons,
        "generated_at": datetime.now().isoformat()
    }
    
    return json.dumps({
        "success": True,
        "comparative_analysis": comparative_analysis
    }, indent=2)

def generate_mock_comparison_data(group: str, level: str) -> dict:
    """Generate mock comparison data for peer group"""
    base_scores = {
        "junior": list(range(60, 85)),
        "mid": list(range(70, 90)),
        "senior": list(range(75, 95))
    }
    
    scores = base_scores.get(level, base_scores["mid"])
    
    return {
        "total_candidates": random.randint(100, 500),
        "score_distribution": {
            "mean": statistics.mean(scores),
            "median": statistics.median(scores),
            "std_dev": statistics.stdev(scores),
            "min": min(scores),
            "max": max(scores)
        },
        "category_averages": {
            "technical_skills": random.randint(70, 85),
            "problem_solving": random.randint(65, 80),
            "code_quality": random.randint(68, 82)
        },
        "pass_rate": random.randint(60, 80),
        "average_completion_time": random.randint(45, 75)
    }

def calculate_percentile(score: float, distribution: dict) -> int:
    """Calculate percentile ranking for a score"""
    # Simplified percentile calculation
    mean = distribution["mean"]
    std_dev = distribution["std_dev"]
    
    z_score = (score - mean) / std_dev
    
    if z_score >= 2:
        return 95
    elif z_score >= 1:
        return 85
    elif z_score >= 0:
        return 70
    elif z_score >= -1:
        return 40
    else:
        return 15

def get_performance_ranking(percentile: int) -> str:
    """Convert percentile to performance ranking"""
    if percentile >= 90:
        return "Top 10%"
    elif percentile >= 75:
        return "Top 25%"
    elif percentile >= 50:
        return "Above Average"
    elif percentile >= 25:
        return "Below Average"
    else:
        return "Bottom 25%"

def generate_comparison_insights(candidate_score: float, comparison_stats: dict) -> list:
    """Generate insights based on comparison"""
    insights = []
    mean_score = comparison_stats["score_distribution"]["mean"]
    
    if candidate_score > mean_score + 10:
        insights.append("Significantly above average performance")
    elif candidate_score > mean_score:
        insights.append("Above average performance")
    elif candidate_score < mean_score - 10:
        insights.append("Significantly below average performance")
    else:
        insights.append("Average performance for this role level")
    
    pass_rate = comparison_stats["pass_rate"]
    if candidate_score >= 70:  # Assuming 70 is passing
        insights.append(f"Passed assessment (pass rate for group: {pass_rate}%)")
    
    return insights

def compare_categories(candidate_categories: dict, group_averages: dict) -> dict:
    """Compare candidate category performance to group averages"""
    comparisons = {}
    
    for category, candidate_data in candidate_categories.items():
        if category in group_averages:
            candidate_score = candidate_data["score_percentage"]
            group_average = group_averages[category]
            
            comparisons[category] = {
                "candidate_score": candidate_score,
                "group_average": group_average,
                "difference": round(candidate_score - group_average, 2),
                "relative_performance": "Above Average" if candidate_score > group_average else "Below Average"
            }
    
    return comparisons

@mcp.tool()
def create_assessment_report(
    analysis_ids: str,
    report_format: str = "detailed",
    include_recommendations: bool = True,
    include_comparisons: bool = False
) -> str:
    """
    Create comprehensive assessment report
    
    Args:
        analysis_ids: Comma-separated list of analysis IDs to include
        report_format: Format type (summary, detailed, executive)
        include_recommendations: Whether to include recommendations
        include_comparisons: Whether to include peer comparisons
    """
    
    ids = [id.strip() for id in analysis_ids.split(",")]
    report_id = str(uuid.uuid4())[:8]
    
    report_data = {
        "report_id": report_id,
        "report_format": report_format,
        "generated_at": datetime.now().isoformat(),
        "candidate_results": [],
        "summary_statistics": {},
        "recommendations_included": include_recommendations,
        "comparisons_included": include_comparisons
    }
    
    valid_results = []
    
    for analysis_id in ids:
        if analysis_id in assessment_results_db:
            result = assessment_results_db[analysis_id]
            valid_results.append(result)
            
            # Format result based on report type
            if report_format == "executive":
                formatted_result = {
                    "analysis_id": analysis_id,
                    "overall_score": result["candidate_performance"]["overall_score"],
                    "result": "PASS" if result["candidate_performance"]["passed"] else "FAIL",
                    "key_strengths": result["strengths"],
                    "key_weaknesses": result["areas_for_improvement"]
                }
            elif report_format == "summary":
                formatted_result = {
                    "analysis_id": analysis_id,
                    "overall_score": result["candidate_performance"]["overall_score"],
                    "category_scores": {k: v["score_percentage"] for k, v in result["category_breakdown"].items()},
                    "time_spent": result["time_analysis"]["total_time_minutes"],
                    "passed": result["candidate_performance"]["passed"]
                }
            else:  # detailed
                formatted_result = result
            
            report_data["candidate_results"].append(formatted_result)
    
    # Calculate summary statistics
    if valid_results:
        scores = [r["candidate_performance"]["overall_score"] for r in valid_results]
        report_data["summary_statistics"] = {
            "total_candidates": len(valid_results),
            "average_score": round(statistics.mean(scores), 2),
            "median_score": round(statistics.median(scores), 2),
            "pass_rate": round((sum(1 for r in valid_results if r["candidate_performance"]["passed"]) / len(valid_results)) * 100, 2),
            "score_range": {"min": min(scores), "max": max(scores)}
        }
    
    # Add report metadata
    report_data["report_metadata"] = {
        "total_pages": estimate_report_pages(report_format, len(valid_results)),
        "export_formats": ["PDF", "Excel", "JSON"],
        "confidentiality": "Internal Use Only",
        "retention_period": "7 years"
    }
    
    return json.dumps({
        "success": True,
        "report_id": report_id,
        "message": f"Assessment report generated for {len(valid_results)} candidates",
        "report": report_data
    }, indent=2)

def estimate_report_pages(format_type: str, candidate_count: int) -> int:
    """Estimate number of pages in report"""
    if format_type == "executive":
        return max(2, candidate_count // 3)
    elif format_type == "summary":
        return max(3, candidate_count // 2)
    else:  # detailed
        return max(5, candidate_count * 2)

@mcp.tool()
def track_assessment_trends(
    time_period: str = "last_30_days",
    assessment_type: str = "all",
    group_by: str = "week"
) -> str:
    """
    Track assessment performance trends over time
    
    Args:
        time_period: Time period to analyze (last_7_days, last_30_days, last_90_days)
        assessment_type: Filter by assessment type (all, python_developer, frontend_developer)
        group_by: Grouping interval (day, week, month)
    """
    
    trends_id = str(uuid.uuid4())[:8]
    
    # Generate mock trend data
    periods = get_time_periods(time_period, group_by)
    trend_data = []
    
    for period in periods:
        trend_data.append({
            "period": period,
            "assessments_taken": random.randint(5, 25),
            "average_score": round(random.uniform(65, 85), 2),
            "pass_rate": round(random.uniform(60, 85), 2),
            "average_completion_time": random.randint(45, 80)
        })
    
    trends_analysis = {
        "trends_id": trends_id,
        "time_period": time_period,
        "assessment_type": assessment_type,
        "group_by": group_by,
        "trend_data": trend_data,
        "insights": generate_trend_insights(trend_data),
        "generated_at": datetime.now().isoformat()
    }
    
    return json.dumps({
        "success": True,
        "trends_analysis": trends_analysis
    }, indent=2)

def get_time_periods(time_period: str, group_by: str) -> list:
    """Generate time period labels"""
    if group_by == "week":
        return ["Week 1", "Week 2", "Week 3", "Week 4"]
    elif group_by == "month":
        return ["Jan", "Feb", "Mar"]
    else:  # day
        return [f"Day {i+1}" for i in range(7)]

def generate_trend_insights(trend_data: list) -> list:
    """Generate insights from trend data"""
    insights = []
    
    scores = [item["average_score"] for item in trend_data]
    if len(scores) >= 2:
        if scores[-1] > scores[0]:
            insights.append("Average scores are trending upward")
        elif scores[-1] < scores[0]:
            insights.append("Average scores are declining")
        else:
            insights.append("Average scores remain stable")
    
    pass_rates = [item["pass_rate"] for item in trend_data]
    if len(pass_rates) >= 2:
        if pass_rates[-1] > pass_rates[0]:
            insights.append("Pass rates are improving")
        else:
            insights.append("Pass rates need attention")
    
    return insights

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8103)