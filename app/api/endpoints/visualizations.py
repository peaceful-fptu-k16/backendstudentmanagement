"""
Visualization endpoints for Seaborn-based charts
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.core.dependencies import get_db
from app.services.visualization_service import visualization_service

router = APIRouter()


@router.get("/score-distribution")
def get_score_distribution_chart(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate score distribution visualization using Seaborn
    
    Returns:
        Base64 encoded PNG image with score distribution plots
    """
    return visualization_service.generate_score_distribution_plot(db)


@router.get("/correlation-heatmap")
def get_correlation_heatmap(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate correlation heatmap between subjects
    
    Returns:
        Base64 encoded PNG image with correlation heatmap
    """
    return visualization_service.generate_correlation_heatmap(db)


@router.get("/hometown-analysis")
def get_hometown_analysis_chart(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate hometown-based analysis visualization
    
    Returns:
        Base64 encoded PNG image with hometown analysis
    """
    return visualization_service.generate_hometown_analysis(db)


@router.get("/age-performance")
def get_age_performance_chart(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate age vs performance analysis visualization
    
    Returns:
        Base64 encoded PNG image with age-performance analysis
    """
    return visualization_service.generate_age_performance_plot(db)


@router.get("/performance-categories")
def get_performance_categories_chart(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate performance category distribution visualization
    
    Returns:
        Base64 encoded PNG image with performance categories
    """
    return visualization_service.generate_performance_categories(db)


@router.get("/comprehensive-report")
def get_comprehensive_visualization_report(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generate comprehensive visualization report with all charts
    
    Returns:
        Dictionary containing all visualization charts in base64 format
    """
    return visualization_service.generate_comprehensive_report(db)


@router.get("/info")
def get_visualization_info() -> Dict[str, Any]:
    """
    Get information about available visualizations
    """
    return {
        "service": "Seaborn Visualization Service",
        "description": "Advanced data visualization using Seaborn and Matplotlib",
        "available_endpoints": [
            {
                "path": "/score-distribution",
                "description": "Score distribution across subjects with histogram, boxplot, violin plot, and bar chart"
            },
            {
                "path": "/correlation-heatmap",
                "description": "Correlation matrix heatmap showing relationships between subject scores"
            },
            {
                "path": "/hometown-analysis",
                "description": "Analysis of student performance by hometown"
            },
            {
                "path": "/age-performance",
                "description": "Age vs performance correlation and distribution analysis"
            },
            {
                "path": "/performance-categories",
                "description": "Student distribution across performance categories (Excellent, Good, Average, Below Average)"
            },
            {
                "path": "/comprehensive-report",
                "description": "Complete visualization report containing all charts"
            }
        ],
        "output_format": {
            "encoding": "base64",
            "format": "PNG",
            "dpi": 300,
            "usage": "Decode base64 string to display image"
        },
        "libraries": {
            "seaborn": "Data visualization library",
            "matplotlib": "Plotting backend",
            "pandas": "Data manipulation"
        }
    }
