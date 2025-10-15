from typing import Dict, Any
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlmodel import Session

from app.core.dependencies import get_db  # Database session dependency
from app.crud.student import student_crud  # Student CRUD operations
from app.schemas import AnalyticsResponse  # Analytics response schema
from app.utils.xml_response import XMLBuilder  # XML converter utility

router = APIRouter()

@router.get("/summary")
def get_analytics_summary(db: Session = Depends(get_db)):
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

# ============================================================================
# Helper Functions for Analytics Calculations
# ============================================================================

def _get_strongest_subject(average_scores: Dict[str, float]) -> str:
    if not average_scores:
        return "N/A"
    
    # Filter out None values
    valid_scores = {k: v for k, v in average_scores.items() if v is not None}
    if not valid_scores:
        return "N/A"
    
    # Return subject with maximum score
    return max(valid_scores, key=valid_scores.get)

def _get_weakest_subject(average_scores: Dict[str, float]) -> str:
    if not average_scores:
        return "N/A"
    
    # Filter out None values
    valid_scores = {k: v for k, v in average_scores.items() if v is not None}
    if not valid_scores:
        return "N/A"
    
    # Return subject with minimum score
    return min(valid_scores, key=valid_scores.get)

def _count_balanced_students(subject_comparison: Dict[str, Any]) -> int:
    total_equal = 0
    # Iterate through all subject pair comparisons
    for comparison_key, data in subject_comparison.items():
        if isinstance(data, dict) and "equal" in data:
            total_equal += data["equal"]
    
    return total_equal

def _get_improvement_areas(average_scores: Dict[str, float]) -> list:
    if not average_scores:
        return []
    
    improvement_areas = []
    # Check each subject against improvement threshold
    for subject, score in average_scores.items():
        if score is not None and score < 6.0:  # Below acceptable threshold
            improvement_areas.append(subject)
    
    return improvement_areas

def _get_most_common_hometown(hometown_distribution: Dict[str, int]) -> str:
    if not hometown_distribution:
        return "N/A"
    
    # Return hometown key with maximum count value
    return max(hometown_distribution, key=hometown_distribution.get)

def _calculate_excellence_rate(grade_distribution: Dict[str, int]) -> float:
    if not grade_distribution:
        return 0.0
    
    total_students = sum(grade_distribution.values())
    excellent_students = grade_distribution.get("Excellent", 0)
    
    return (excellent_students / total_students * 100) if total_students > 0 else 0.0

def _calculate_pass_rate(score_distribution: Dict[str, int]) -> float:
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
    if not grade_distribution:
        return "N/A"
    
    most_common_grade = max(grade_distribution, key=grade_distribution.get)
    return most_common_grade