from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.dependencies import get_db
from app.crud.student import student_crud
from app.schemas import AnalyticsResponse

router = APIRouter()

@router.get("", response_model=AnalyticsResponse)
def get_analytics(db: Session = Depends(get_db)):
    """Get student analytics and statistics"""
    
    analytics_data = student_crud.get_analytics(db=db)
    
    return AnalyticsResponse(**analytics_data)

@router.get("/summary")
def get_analytics_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get comprehensive analytics summary"""
    
    analytics_data = student_crud.get_analytics(db=db)
    
    return {
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
            "strongest_subject": _get_strongest_subject(analytics_data.get("average_scores", {})),
            "weakest_subject": _get_weakest_subject(analytics_data.get("average_scores", {})),
            "excellence_rate": _calculate_excellence_rate(analytics_data.get("grade_distribution", {})),
            "pass_rate": _calculate_pass_rate(analytics_data.get("score_distribution", {})),
            "most_common_hometown": _get_most_common_hometown(analytics_data.get("hometown_distribution", {}))
        }
    }

@router.get("/score-comparison")
def get_score_comparison(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get detailed score comparison analysis"""
    
    analytics_data = student_crud.get_analytics(db=db)
    
    # Extract and format subject comparison data
    subject_comparison = analytics_data.get("subject_comparison", {})
    
    return {
        "comparisons": subject_comparison,
        "insights": {
            "strongest_subject": _get_strongest_subject(analytics_data.get("average_scores", {})),
            "weakest_subject": _get_weakest_subject(analytics_data.get("average_scores", {})),
            "most_balanced_students": _count_balanced_students(subject_comparison),
            "improvement_areas": _get_improvement_areas(analytics_data.get("average_scores", {}))
        }
    }

@router.get("/hometown-analysis")  
def get_hometown_analysis(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get hometown-based academic performance analysis"""
    
    # This would require more complex queries in a real implementation
    # For now, return basic hometown distribution
    analytics_data = student_crud.get_analytics(db=db)
    
    return {
        "hometown_distribution": analytics_data.get("hometown_distribution", {}),
        "top_performing_hometowns": [],  # Placeholder for future implementation
        "insights": {
            "most_common_hometown": _get_most_common_hometown(analytics_data.get("hometown_distribution", {})),
            "total_hometowns": len(analytics_data.get("hometown_distribution", {}))
        }
    }

@router.get("/performance-trends")
def get_performance_trends(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get performance trends and patterns"""
    
    analytics_data = student_crud.get_analytics(db=db)
    
    return {
        "grade_distribution": analytics_data.get("grade_distribution", {}),
        "score_distribution": analytics_data.get("score_distribution", {}),
        "insights": {
            "excellence_rate": _calculate_excellence_rate(analytics_data.get("grade_distribution", {})),
            "pass_rate": _calculate_pass_rate(analytics_data.get("score_distribution", {})),
            "average_performance": _get_average_performance_level(analytics_data.get("grade_distribution", {}))
        }
    }

def _get_strongest_subject(average_scores: Dict[str, float]) -> str:
    """Determine the strongest subject based on average scores"""
    if not average_scores:
        return "N/A"
    
    valid_scores = {k: v for k, v in average_scores.items() if v is not None}
    if not valid_scores:
        return "N/A"
    
    return max(valid_scores, key=valid_scores.get)

def _get_weakest_subject(average_scores: Dict[str, float]) -> str:
    """Determine the weakest subject based on average scores"""
    if not average_scores:
        return "N/A"
    
    valid_scores = {k: v for k, v in average_scores.items() if v is not None}
    if not valid_scores:
        return "N/A"
    
    return min(valid_scores, key=valid_scores.get)

def _count_balanced_students(subject_comparison: Dict[str, Any]) -> int:
    """Count students with balanced performance across subjects"""
    # This is a simplified calculation
    total_equal = 0
    for comparison_key, data in subject_comparison.items():
        if isinstance(data, dict) and "equal" in data:
            total_equal += data["equal"]
    
    return total_equal

def _get_improvement_areas(average_scores: Dict[str, float]) -> list:
    """Identify areas needing improvement"""
    if not average_scores:
        return []
    
    improvement_areas = []
    for subject, score in average_scores.items():
        if score is not None and score < 6.0:  # Below average threshold
            improvement_areas.append(subject)
    
    return improvement_areas

def _get_most_common_hometown(hometown_distribution: Dict[str, int]) -> str:
    """Get the most common hometown"""
    if not hometown_distribution:
        return "N/A"
    
    return max(hometown_distribution, key=hometown_distribution.get)

def _calculate_excellence_rate(grade_distribution: Dict[str, int]) -> float:
    """Calculate percentage of excellent students"""
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