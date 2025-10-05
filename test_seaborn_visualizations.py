#!/usr/bin/env python3
"""
Test script for Seaborn visualization endpoints
"""
import requests
import json
import base64
from pathlib import Path
from typing import Dict, Any


def save_base64_image(base64_string: str, filename: str):
    """Save base64 encoded image to file"""
    output_dir = Path("visualization_outputs")
    output_dir.mkdir(exist_ok=True)
    
    image_data = base64.b64decode(base64_string)
    output_path = output_dir / filename
    
    with open(output_path, 'wb') as f:
        f.write(image_data)
    
    print(f"   💾 Saved: {output_path}")
    return output_path


def test_visualization_endpoint(endpoint: str, filename: str):
    """Test a visualization endpoint and save the result"""
    url = f"http://127.0.0.1:8001/api/v1/visualizations/{endpoint}"
    
    try:
        print(f"\n📊 Testing: {endpoint}")
        print(f"   🔗 URL: {url}")
        
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if "image" in data:
                save_base64_image(data["image"], filename)
                print("   ✅ SUCCESS!")
                
                # Print statistics if available
                if "statistics" in data:
                    print(f"   📈 Statistics: {json.dumps(data['statistics'], indent=2)}")
                
                return True
            else:
                print(f"   ⚠️  No image data in response")
                return False
        else:
            print(f"   ❌ FAILED! Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False


def test_comprehensive_report():
    """Test comprehensive report endpoint"""
    url = "http://127.0.0.1:8001/api/v1/visualizations/comprehensive-report"
    
    try:
        print(f"\n📊 Testing: comprehensive-report")
        print(f"   🔗 URL: {url}")
        
        response = requests.get(url, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            
            print("   ✅ SUCCESS! Saving all charts...")
            
            # Save each chart
            charts_saved = 0
            for chart_type, chart_data in data.items():
                if isinstance(chart_data, dict) and "image" in chart_data:
                    filename = f"comprehensive_{chart_type}.png"
                    save_base64_image(chart_data["image"], filename)
                    charts_saved += 1
            
            print(f"   📊 Saved {charts_saved} charts")
            return True
        else:
            print(f"   ❌ FAILED! Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False


def test_visualization_info():
    """Test visualization info endpoint"""
    url = "http://127.0.0.1:8001/api/v1/visualizations/info"
    
    try:
        print(f"\n📋 Getting Visualization Info...")
        print(f"   🔗 URL: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ SUCCESS!")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return True
        else:
            print(f"   ❌ FAILED! Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False


def main():
    """Run all visualization tests"""
    print("=" * 70)
    print("🎨 SEABORN VISUALIZATION TESTING")
    print("=" * 70)
    
    # Test info endpoint first
    test_visualization_info()
    
    print("\n" + "=" * 70)
    print("📊 TESTING INDIVIDUAL VISUALIZATIONS")
    print("=" * 70)
    
    # Test individual endpoints
    tests = [
        ("score-distribution", "score_distribution.png"),
        ("correlation-heatmap", "correlation_heatmap.png"),
        ("hometown-analysis", "hometown_analysis.png"),
        ("age-performance", "age_performance.png"),
        ("performance-categories", "performance_categories.png"),
    ]
    
    results = []
    for endpoint, filename in tests:
        success = test_visualization_endpoint(endpoint, filename)
        results.append((endpoint, success))
    
    # Test comprehensive report
    print("\n" + "=" * 70)
    print("📊 TESTING COMPREHENSIVE REPORT")
    print("=" * 70)
    comprehensive_success = test_comprehensive_report()
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 TEST SUMMARY")
    print("=" * 70)
    
    for endpoint, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {endpoint}")
    
    status = "✅" if comprehensive_success else "❌"
    print(f"{status} comprehensive-report")
    
    total_tests = len(results) + 1
    passed_tests = sum(1 for _, s in results if s) + (1 if comprehensive_success else 0)
    
    print("\n" + "=" * 70)
    print(f"📊 Results: {passed_tests}/{total_tests} tests passed")
    print("=" * 70)
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    main()
