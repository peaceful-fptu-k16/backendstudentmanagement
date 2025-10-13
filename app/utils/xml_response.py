"""
XML Response Utilities for API Endpoints
Converts various data structures to XML format
"""

import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from decimal import Decimal


class XMLBuilder:
    """Helper class to build XML responses"""
    
    @staticmethod
    def dict_to_xml(data: Dict[str, Any], root_name: str = "response") -> str:
        """Convert dictionary to XML string"""
        root = ET.Element(root_name)
        XMLBuilder._add_dict_to_element(root, data)
        ET.indent(root, space="  ", level=0)
        return ET.tostring(root, encoding='unicode', xml_declaration=True)
    
    @staticmethod
    def list_to_xml(data: List[Any], root_name: str = "response", item_name: str = "item") -> str:
        """Convert list to XML string"""
        root = ET.Element(root_name)
        for item in data:
            item_elem = ET.SubElement(root, item_name)
            if isinstance(item, dict):
                XMLBuilder._add_dict_to_element(item_elem, item)
            else:
                item_elem.text = XMLBuilder._convert_value(item)
        
        ET.indent(root, space="  ", level=0)
        return ET.tostring(root, encoding='unicode', xml_declaration=True)
    
    @staticmethod
    def _add_dict_to_element(parent: ET.Element, data: Dict[str, Any]):
        """Recursively add dictionary items to XML element"""
        for key, value in data.items():
            # Sanitize key name for XML
            safe_key = XMLBuilder._sanitize_key(key)
            
            if value is None:
                # Add empty element with null attribute
                elem = ET.SubElement(parent, safe_key)
                elem.set("null", "true")
            elif isinstance(value, dict):
                elem = ET.SubElement(parent, safe_key)
                XMLBuilder._add_dict_to_element(elem, value)
            elif isinstance(value, list):
                elem = ET.SubElement(parent, safe_key)
                for item in value:
                    item_elem = ET.SubElement(elem, "item")
                    if isinstance(item, dict):
                        XMLBuilder._add_dict_to_element(item_elem, item)
                    else:
                        item_elem.text = XMLBuilder._convert_value(item)
            else:
                elem = ET.SubElement(parent, safe_key)
                elem.text = XMLBuilder._convert_value(value)
    
    @staticmethod
    def _convert_value(value: Any) -> str:
        """Convert Python value to XML string"""
        if value is None:
            return ""
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, (datetime, date)):
            return value.isoformat()
        elif isinstance(value, (int, float, Decimal)):
            return str(value)
        else:
            return str(value)
    
    @staticmethod
    def _sanitize_key(key: str) -> str:
        """Sanitize key to be valid XML element name"""
        # Replace invalid characters with underscore
        key = key.replace(" ", "_")
        key = key.replace("-", "_")
        
        # Ensure it starts with letter or underscore
        if key and not (key[0].isalpha() or key[0] == '_'):
            key = f"_{key}"
        
        return key or "item"


class StudentXMLBuilder:
    """Specialized XML builder for student data"""
    
    @staticmethod
    def student_to_xml(student_data: Dict[str, Any]) -> str:
        """Convert student response to XML"""
        root = ET.Element("student")
        
        # Basic info
        ET.SubElement(root, "id").text = str(student_data.get("id", ""))
        ET.SubElement(root, "student_id").text = str(student_data.get("student_id", ""))
        
        # Personal info
        personal = ET.SubElement(root, "personal_info")
        ET.SubElement(personal, "first_name").text = student_data.get("first_name", "")
        ET.SubElement(personal, "last_name").text = student_data.get("last_name", "")
        ET.SubElement(personal, "full_name").text = student_data.get("full_name", "")
        
        if student_data.get("email"):
            ET.SubElement(personal, "email").text = student_data.get("email")
        if student_data.get("birth_date"):
            ET.SubElement(personal, "birth_date").text = str(student_data.get("birth_date"))
        if student_data.get("hometown"):
            ET.SubElement(personal, "hometown").text = student_data.get("hometown")
        
        # Academic info
        academic = ET.SubElement(root, "academic_info")
        
        scores = {
            "math_score": student_data.get("math_score"),
            "literature_score": student_data.get("literature_score"),
            "english_score": student_data.get("english_score"),
            "average_score": student_data.get("average_score"),
        }
        
        for score_name, score_value in scores.items():
            if score_value is not None:
                ET.SubElement(academic, score_name).text = str(score_value)
        
        if student_data.get("grade"):
            ET.SubElement(academic, "grade").text = student_data.get("grade")
        
        # System info
        system = ET.SubElement(root, "system_info")
        if student_data.get("created_at"):
            ET.SubElement(system, "created_at").text = str(student_data.get("created_at"))
        if student_data.get("updated_at"):
            ET.SubElement(system, "updated_at").text = str(student_data.get("updated_at"))
        
        ET.indent(root, space="  ", level=0)
        # Return XML as UTF-8 string with proper declaration
        xml_bytes = ET.tostring(root, encoding='utf-8', xml_declaration=True)
        return xml_bytes.decode('utf-8')
    
    @staticmethod
    def students_to_xml(students_data: List[Dict[str, Any]], pagination: Optional[Dict[str, Any]] = None) -> str:
        """Convert list of students with pagination to XML"""
        root = ET.Element("students")
        
        # Add pagination info if provided
        if pagination:
            page_info = ET.SubElement(root, "pagination")
            ET.SubElement(page_info, "total").text = str(pagination.get("total", 0))
            ET.SubElement(page_info, "page").text = str(pagination.get("page", 1))
            ET.SubElement(page_info, "page_size").text = str(pagination.get("page_size", 10))
            ET.SubElement(page_info, "total_pages").text = str(pagination.get("total_pages", 0))
            ET.SubElement(page_info, "has_next").text = "true" if pagination.get("has_next") else "false"
            ET.SubElement(page_info, "has_prev").text = "true" if pagination.get("has_prev") else "false"
        
        # Add student items
        items = ET.SubElement(root, "items")
        for student in students_data:
            student_elem = ET.SubElement(items, "student")
            
            # Basic info
            ET.SubElement(student_elem, "id").text = str(student.get("id", ""))
            ET.SubElement(student_elem, "student_id").text = str(student.get("student_id", ""))
            
            # Personal info
            ET.SubElement(student_elem, "first_name").text = student.get("first_name", "")
            ET.SubElement(student_elem, "last_name").text = student.get("last_name", "")
            ET.SubElement(student_elem, "full_name").text = student.get("full_name", "")
            
            if student.get("email"):
                ET.SubElement(student_elem, "email").text = student.get("email")
            if student.get("birth_date"):
                ET.SubElement(student_elem, "birth_date").text = str(student.get("birth_date"))
            if student.get("hometown"):
                ET.SubElement(student_elem, "hometown").text = student.get("hometown")
            
            # Scores
            if student.get("math_score") is not None:
                ET.SubElement(student_elem, "math_score").text = str(student.get("math_score"))
            if student.get("literature_score") is not None:
                ET.SubElement(student_elem, "literature_score").text = str(student.get("literature_score"))
            if student.get("english_score") is not None:
                ET.SubElement(student_elem, "english_score").text = str(student.get("english_score"))
            if student.get("average_score") is not None:
                ET.SubElement(student_elem, "average_score").text = str(student.get("average_score"))
            if student.get("grade"):
                ET.SubElement(student_elem, "grade").text = student.get("grade")
            
            # System info (optional)
            if student.get("created_at"):
                ET.SubElement(student_elem, "created_at").text = str(student.get("created_at"))
            if student.get("updated_at"):
                ET.SubElement(student_elem, "updated_at").text = str(student.get("updated_at"))
        
        ET.indent(root, space="  ", level=0)
        # Return XML as UTF-8 string with proper declaration
        xml_bytes = ET.tostring(root, encoding='utf-8', xml_declaration=True)
        return xml_bytes.decode('utf-8')
    
    @staticmethod
    def generation_result_to_xml(result: Dict[str, Any]) -> str:
        """Convert sample generation result to XML"""
        root = ET.Element("generation_result")
        
        ET.SubElement(root, "total_generated").text = str(result.get("total_generated", 0))
        ET.SubElement(root, "successful_inserts").text = str(result.get("successful_inserts", 0))
        ET.SubElement(root, "failed_inserts").text = str(result.get("failed_inserts", 0))
        
        # Errors
        if result.get("errors"):
            errors_elem = ET.SubElement(root, "errors")
            for error in result.get("errors", []):
                error_elem = ET.SubElement(errors_elem, "error")
                error_elem.text = str(error)
        
        # Generated student IDs
        if result.get("student_ids"):
            ids_elem = ET.SubElement(root, "student_ids")
            for student_id in result.get("student_ids", []):
                ET.SubElement(ids_elem, "student_id").text = str(student_id)
        
        ET.indent(root, space="  ", level=0)
        return ET.tostring(root, encoding='unicode', xml_declaration=True)


def create_xml_response(data: Any, root_name: str = "response") -> str:
    """
    Main function to create XML response from any data structure
    
    Args:
        data: Data to convert (dict, list, or custom object)
        root_name: Name of root XML element
    
    Returns:
        XML string with declaration
    """
    if isinstance(data, dict):
        return XMLBuilder.dict_to_xml(data, root_name)
    elif isinstance(data, list):
        return XMLBuilder.list_to_xml(data, root_name, "item")
    else:
        # Convert to dict first
        if hasattr(data, "dict"):
            return XMLBuilder.dict_to_xml(data.dict(), root_name)
        elif hasattr(data, "__dict__"):
            return XMLBuilder.dict_to_xml(data.__dict__, root_name)
        else:
            root = ET.Element(root_name)
            root.text = str(data)
            return ET.tostring(root, encoding='unicode', xml_declaration=True)
