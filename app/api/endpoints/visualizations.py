"""
Visualization endpoints for Seaborn-based charts
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlmodel import Session

from app.core.dependencies import get_db
from app.services.visualization_service import visualization_service
from app.utils.xml_response import XMLBuilder

router = APIRouter()


@router.get("/score-distribution")
def get_score_distribution_chart(
    db: Session = Depends(get_db)
):
    """
    Generate score distribution visualization using Seaborn - Returns XML
    
    Returns:
        XML with Base64 encoded PNG image with score distribution plots
    """
    result = visualization_service.generate_score_distribution_plot(db)
    xml_content = XMLBuilder.dict_to_xml(result, "visualization")
    return Response(content=xml_content, media_type="application/xml")


@router.get("/correlation-heatmap")
def get_correlation_heatmap(
    db: Session = Depends(get_db)
):
    """
    Generate correlation heatmap between subjects - Returns XML
    
    Returns:
        XML with Base64 encoded PNG image with correlation heatmap
    """
    result = visualization_service.generate_correlation_heatmap(db)
    xml_content = XMLBuilder.dict_to_xml(result, "visualization")
    return Response(content=xml_content, media_type="application/xml")


@router.get("/hometown-analysis")
def get_hometown_analysis_chart(
    db: Session = Depends(get_db)
):
    """
    Generate hometown-based analysis visualization - Returns XML
    
    Returns:
        XML with Base64 encoded PNG image with hometown analysis
    """
    result = visualization_service.generate_hometown_analysis(db)
    xml_content = XMLBuilder.dict_to_xml(result, "visualization")
    return Response(content=xml_content, media_type="application/xml")


@router.get("/age-performance")
def get_age_performance_chart(
    db: Session = Depends(get_db)
):
    """
    Generate age vs performance analysis visualization - Returns XML
    
    Returns:
        XML with Base64 encoded PNG image with age-performance analysis
    """
    result = visualization_service.generate_age_performance_plot(db)
    xml_content = XMLBuilder.dict_to_xml(result, "visualization")
    return Response(content=xml_content, media_type="application/xml")


@router.get("/performance-categories")
def get_performance_categories_chart(
    db: Session = Depends(get_db)
):
    """
    Generate performance category distribution visualization - Returns XML
    
    Returns:
        XML with Base64 encoded PNG image with performance categories
    """
    result = visualization_service.generate_performance_categories(db)
    xml_content = XMLBuilder.dict_to_xml(result, "visualization")
    return Response(content=xml_content, media_type="application/xml")


@router.get("/comprehensive-report")
def get_comprehensive_visualization_report(
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive visualization report with all charts - Returns XML
    
    Returns:
        XML containing all visualization charts in base64 format
    """
    result = visualization_service.generate_comprehensive_report(db)
    xml_content = XMLBuilder.dict_to_xml(result, "comprehensive_report")
    return Response(content=xml_content, media_type="application/xml")


@router.get("/info")
def get_visualization_info():
    """
    Get information about available visualizations - Returns XML
    """
    info = {
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
            "usage": "Decode base64 string to display image",
            "response_format": "XML"
        },
        "libraries": {
            "seaborn": "Data visualization library",
            "matplotlib": "Plotting backend",
            "pandas": "Data manipulation"
        }
    }
    
    xml_content = XMLBuilder.dict_to_xml(info, "visualization_info")
    return Response(content=xml_content, media_type="application/xml")
