"""
Utility functions for pandas and numpy data serialization
"""
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Union


def convert_numpy_types(obj: Any) -> Any:
    """
    Recursively convert numpy types to Python native types for JSON serialization
    
    Args:
        obj: Object that may contain numpy types
        
    Returns:
        Object with numpy types converted to Python native types
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {str(k): convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(v) for v in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(v) for v in obj)
    elif pd.isna(obj):
        return None
    else:
        return obj


def safe_dataframe_to_dict(df: pd.DataFrame, orient: str = 'records') -> List[Dict[str, Any]]:
    """
    Convert DataFrame to dictionary with numpy types converted to Python native types
    
    Args:
        df: pandas DataFrame
        orient: Orientation for conversion ('records', 'dict', etc.)
        
    Returns:
        Dictionary with Python native types
    """
    # Convert DataFrame to dict
    data = df.to_dict(orient=orient)
    
    # Convert numpy types recursively
    return convert_numpy_types(data)


def safe_series_to_dict(series: pd.Series) -> Dict[str, Any]:
    """
    Convert pandas Series to dictionary with numpy types converted
    
    Args:
        series: pandas Series
        
    Returns:
        Dictionary with Python native types
    """
    data = series.to_dict()
    return convert_numpy_types(data)