"""
Analytics API Endpoints

This module provides statistical analytics endpoints for student data analysis.
Returns comprehensive statistics, grade distributions, and performance insights.
All responses are returned in XML format.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlmodel import Session

from app.core.dependencies import get_db  # Database session dependency
from app.crud.student import student_crud  # Student CRUD operations
from app.schemas import AnalyticsResponse  # Analytics response schema
from app.utils.xml_response import XMLBuilder  # XML converter utility

router = APIRouter()

@router.get("")
def get_analytics(db: Session = Depends(get_db)):
    """
    Get comprehensive student analytics and statistics
    
    Returns:
        XML response containing:
            - total_students: Total count of students
            - average_age: Average age of all students
            - average_scores: Mean scores for Math, Literature, English
            - grade_distribution: Count of students by grade (A, B, C, D, F)
            - score_distribution: Count of students by score ranges
            - hometown_distribution: Count of students by hometown
            - age_distribution: Count of students by age groups
            - subject_comparison: Score comparisons between subjects
    """
    
    # Retrieve all analytics from database (computed by CRUD layer)
    analytics_data = student_crud.get_analytics(db=db)
    
    # Convert analytics dictionary to XML format
    xml_content = XMLBuilder.dict_to_xml(analytics_data, "analytics")
    return Response(content=xml_content, media_type="application/xml")

@router.get("/summary")
def get_analytics_summary(db: Session = Depends(get_db)):
    """
    Get condensed analytics summary with key insights
    
    Returns:
        XML response with structured summary:
            - overview: Basic statistics (total students, average age, hometown count)
            - academic_performance: Score averages, grade distribution, score ranges
            - demographics: Hometown and age distribution
            - insights: Derived insights (strongest/weakest subject, excellence rate, etc.)
    """
    
    # Retrieve full analytics data
    analytics_data = student_crud.get_analytics(db=db)
    
    # Structure summary with organized sections
    summary = {
        "overview": {
            "total_students": analytics_data.get("total_students", 0),
            "average_age": analytics_data.get("average_age", 0),
            "total_hometowns": len(analytics_data.get("hometown_distribution", {}))
        },
        "academic_performance": {
            "average_scores": analytics_data.get("average_scores", {}),
            "grade_distribution": analytics_data.get("grade_distribution", {}),
            "score_distribution": analytics_data.get("score_distribution", {})
        },
        "demographics": {
            "hometown_distribution": analytics_data.get("hometown_distribution", {}),
            "age_distribution": analytics_data.get("age_distribution", {})
        },
        "insights": {
            # Calculate derived insights from raw analytics
            "strongest_subject": _get_strongest_subject(analytics_data.get("average_scores", {})),
            "weakest_subject": _get_weakest_subject(analytics_data.get("average_scores", {})),
            "excellence_rate": _calculate_excellence_rate(analytics_data.get("grade_distribution", {})),
            "pass_rate": _calculate_pass_rate(analytics_data.get("score_distribution", {})),
            "most_common_hometown": _get_most_common_hometown(analytics_data.get("hometown_distribution", {}))
        }
    }
    
    # Convert summary to XML and return
    xml_content = XMLBuilder.dict_to_xml(summary, "analytics_summary")
    return Response(content=xml_content, media_type="application/xml")

@router.get("/score-comparison")
def get_score_comparison(db: Session = Depends(get_db)):
    """
    Get detailed score comparison analysis across subjects
    
    Returns:
        XML response with subject comparisons:
            - comparisons: Raw comparison data between Math, Literature, English
            - insights: Analysis of strongest/weakest subjects, balanced students,
                       and areas needing improvement
    """
    
    # Retrieve analytics with subject comparison data
    analytics_data = student_crud.get_analytics(db=db)
    
    # Extract subject comparison section
    subject_comparison = analytics_data.get("subject_comparison", {})
    
    # Build comparison analysis with insights
    comparison = {
        "comparisons": subject_comparison,
        "insights": {
            # Identify strongest subject by average score
            "strongest_subject": _get_strongest_subject(analytics_data.get("average_scores", {})),
            # Identify weakest subject by average score
            "weakest_subject": _get_weakest_subject(analytics_data.get("average_scores", {})),
            # Count students with balanced scores across subjects
            "most_balanced_students": _count_balanced_students(subject_comparison),
            # Identify subjects below acceptable thresholds
            "improvement_areas": _get_improvement_areas(analytics_data.get("average_scores", {}))
        }
    }
    
    # Convert to XML and return
    xml_content = XMLBuilder.dict_to_xml(comparison, "score_comparison")
    return Response(content=xml_content, media_type="application/xml")

@router.get("/hometown-analysis")  
def get_hometown_analysis(db: Session = Depends(get_db)):
    """
    Get hometown-based academic performance analysis
    
    Returns:
        XML response with hometown analysis:
            - hometown_distribution: Count of students per hometown
            - top_performing_hometowns: List of hometowns with highest avg scores (placeholder)
            - insights: Most common hometown and total hometown count
    
    Note:
        This is a basic implementation. Advanced analysis (avg scores per hometown)
        would require additional database queries for full implementation.
    """
    
    # Retrieve analytics with hometown distribution data
    analytics_data = student_crud.get_analytics(db=db)
    
    # Build hometown analysis structure
    analysis = {
        "hometown_distribution": analytics_data.get("hometown_distribution", {}),
        "top_performing_hometowns": [],  # Placeholder for future enhancement
        "insights": {
            # Identify most populous hometown
            "most_common_hometown": _get_most_common_hometown(analytics_data.get("hometown_distribution", {})),
            # Count unique hometowns
            "total_hometowns": len(analytics_data.get("hometown_distribution", {}))
        }
    }
    
    # Convert to XML and return
    xml_content = XMLBuilder.dict_to_xml(analysis, "hometown_analysis")
    return Response(content=xml_content, media_type="application/xml")

@router.get("/performance-trends")
def get_performance_trends(db: Session = Depends(get_db)):
    """
    Get performance trends and patterns across student population
    
    Returns:
        XML response with performance trends:
            - grade_distribution: Count of students by grade (A, B, C, D, F)
            - score_distribution: Count of students by score ranges
            - insights: Excellence rate (% with grade A), pass rate (% score ≥5),
                       and average performance level
    """
    
    # Retrieve full analytics data
    analytics_data = student_crud.get_analytics(db=db)
    
    # Build trends analysis with calculated rates
    trends = {
        "grade_distribution": analytics_data.get("grade_distribution", {}),
        "score_distribution": analytics_data.get("score_distribution", {}),
        "insights": {
            # Calculate percentage of students with A grade
            "excellence_rate": _calculate_excellence_rate(analytics_data.get("grade_distribution", {})),
            # Calculate percentage of students with passing scores (≥5)
            "pass_rate": _calculate_pass_rate(analytics_data.get("score_distribution", {})),
            # Determine overall performance level (Excellent, Good, Average, etc.)
            "average_performance": _get_average_performance_level(analytics_data.get("grade_distribution", {}))
        }
    }
    
    # Convert to XML and return
    xml_content = XMLBuilder.dict_to_xml(trends, "performance_trends")
    return Response(content=xml_content, media_type="application/xml")

# ============================================================================
# Helper Functions for Analytics Calculations
# ============================================================================

def _get_strongest_subject(average_scores: Dict[str, float]) -> str:
    """
    Determine the strongest subject based on average scores
    
    Args:
        average_scores: Dictionary mapping subject names to average scores
    
    Returns:
        Name of subject with highest average score, or "N/A" if no scores
    """
    if not average_scores:
        return "N/A"
    
    # Filter out None values
    valid_scores = {k: v for k, v in average_scores.items() if v is not None}
    if not valid_scores:
        return "N/A"
    
    # Return subject with maximum score
    return max(valid_scores, key=valid_scores.get)

def _get_weakest_subject(average_scores: Dict[str, float]) -> str:
    """
    Determine the weakest subject based on average scores
    
    Args:
        average_scores: Dictionary mapping subject names to average scores
    
    Returns:
        Name of subject with lowest average score, or "N/A" if no scores
    """
    if not average_scores:
        return "N/A"
    
    # Filter out None values
    valid_scores = {k: v for k, v in average_scores.items() if v is not None}
    if not valid_scores:
        return "N/A"
    
    # Return subject with minimum score
    return min(valid_scores, key=valid_scores.get)

def _count_balanced_students(subject_comparison: Dict[str, Any]) -> int:
    """
    Count students with balanced performance across subjects
    
    Args:
        subject_comparison: Dictionary with comparison data between subjects
    
    Returns:
        Count of students with equal scores across compared subjects
    
    Note:
        Simplified calculation summing 'equal' counts from comparison data
    """
    total_equal = 0
    # Iterate through all subject pair comparisons
    for comparison_key, data in subject_comparison.items():
        if isinstance(data, dict) and "equal" in data:
            total_equal += data["equal"]
    
    return total_equal

def _get_improvement_areas(average_scores: Dict[str, float]) -> list:
    """
    Identify subjects needing improvement based on score thresholds
    
    Args:
        average_scores: Dictionary mapping subject names to average scores
    
    Returns:
        List of subject names with scores below 6.0 (needs improvement)
    """
    if not average_scores:
        return []
    
    improvement_areas = []
    # Check each subject against improvement threshold
    for subject, score in average_scores.items():
        if score is not None and score < 6.0:  # Below acceptable threshold
            improvement_areas.append(subject)
    
    return improvement_areas

def _get_most_common_hometown(hometown_distribution: Dict[str, int]) -> str:
    """
    Get the most frequently occurring hometown
    
    Args:
        hometown_distribution: Dictionary mapping hometown names to student counts
    
    Returns:
        Name of hometown with most students, or "N/A" if no data
    """
    if not hometown_distribution:
        return "N/A"
    
    # Return hometown key with maximum count value
    return max(hometown_distribution, key=hometown_distribution.get)

def _calculate_excellence_rate(grade_distribution: Dict[str, int]) -> float:
    """
    Calculate percentage of students with excellent grades (A)
    
    Args:
        grade_distribution: Dictionary mapping grade levels to student counts
    
    Returns:
        Percentage of students with "Excellent" grade (0-100)
    """
    if not grade_distribution:
        return 0.0
    
    total_students = sum(grade_distribution.values())
    excellent_students = grade_distribution.get("Excellent", 0)
    
    return (excellent_students / total_students * 100) if total_students > 0 else 0.0

def _calculate_pass_rate(score_distribution: Dict[str, int]) -> float:
    """Calculate overall pass rate (>=5.5 average)"""
    if not score_distribution:
        return 0.0
    
    total_students = sum(score_distribution.values())
    passing_students = (
        score_distribution.get("5.5-7", 0) + 
        score_distribution.get("7-8.5", 0) + 
        score_distribution.get("8.5-10", 0)
    )
    
    return (passing_students / total_students * 100) if total_students > 0 else 0.0

def _get_average_performance_level(grade_distribution: Dict[str, int]) -> str:
    """Determine the most common performance level"""
    if not grade_distribution:
        return "N/A"
    
    most_common_grade = max(grade_distribution, key=grade_distribution.get)
    return most_common_grade