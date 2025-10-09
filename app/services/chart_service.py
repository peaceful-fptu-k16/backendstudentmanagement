"""
Chart Generation Service

Creates statistical charts using matplotlib.
Generates PNG images for various analytics visualizations.
"""

import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for server
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict
from datetime import datetime
import os

from app.models.student import Student

class ChartService:
    """
    Service for generating statistical charts with matplotlib
    
    Methods:
        generate_all_charts(): Generate all chart types
        generate_grade_distribution(): Bar chart of grade distribution
        generate_score_comparison(): Bar chart comparing average scores
        generate_hometown_distribution(): Pie chart of hometown distribution
        generate_score_histogram(): Histogram of score ranges
    """
    
    def __init__(self, output_dir: str = "uploads/charts"):
        """
        Initialize chart service
        
        Args:
            output_dir: Directory to save generated charts
        """
        self.output_dir = output_dir
        
        # Create output directory if not exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Set matplotlib style
        plt.style.use('seaborn-v0_8-darkgrid')
        
    def generate_all_charts(self, students: List[Student]) -> Dict[str, str]:
        """
        Generate all chart types and return file paths
        
        Note: Only students with all three scores (math, literature, english)
        are included in grade distribution and score statistics charts.
        
        Args:
            students: List of Student objects
            
        Returns:
            Dictionary mapping chart names to file paths
        """
        chart_paths = {}
        
        # Filter students with complete scores (all 3 subjects)
        students_with_complete_scores = [
            s for s in students 
            if s.math_score is not None 
            and s.literature_score is not None 
            and s.english_score is not None
        ]
        
        # Generate timestamp for unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Grade distribution chart (only students with complete scores)
        grade_path = os.path.join(
            self.output_dir,
            f"grade_distribution_{timestamp}.png"
        )
        self._generate_grade_distribution(students_with_complete_scores, grade_path)
        chart_paths['grade_distribution'] = grade_path
        
        # 2. Score comparison chart (only students with complete scores)
        score_path = os.path.join(
            self.output_dir,
            f"score_comparison_{timestamp}.png"
        )
        self._generate_score_comparison(students_with_complete_scores, score_path)
        chart_paths['score_comparison'] = score_path
        
        # 3. Hometown distribution chart (all students)
        hometown_path = os.path.join(
            self.output_dir,
            f"hometown_distribution_{timestamp}.png"
        )
        self._generate_hometown_distribution(students, hometown_path)
        chart_paths['hometown_distribution'] = hometown_path
        
        # 4. Score histogram (only students with complete scores)
        histogram_path = os.path.join(
            self.output_dir,
            f"score_histogram_{timestamp}.png"
        )
        self._generate_score_histogram(students_with_complete_scores, histogram_path)
        chart_paths['score_histogram'] = histogram_path
        
        return chart_paths
    
    def _generate_grade_distribution(self, students: List[Student], output_path: str):
        """
        Generate bar chart showing grade distribution
        
        Args:
            students: List of Student objects
            output_path: Path to save chart image
        """
        # Calculate grade distribution
        grade_dist = {}
        for student in students:
            grade = student.get_grade()
            if grade:
                grade_dist[grade] = grade_dist.get(grade, 0) + 1
        
        # Sort grades by quality
        grade_order = ['Excellent', 'Good', 'Average', 'Poor']
        grades = [g for g in grade_order if g in grade_dist]
        counts = [grade_dist[g] for g in grades]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Define colors for each grade
        colors = {
            'Excellent': '#4CAF50',  # Green
            'Good': '#FFC107',       # Yellow
            'Average': '#FF9800',    # Orange
            'Poor': '#F44336'        # Red
        }
        bar_colors = [colors[g] for g in grades]
        
        # Create bars
        bars = ax.bar(grades, counts, color=bar_colors, alpha=0.8, edgecolor='black')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2.,
                height,
                f'{int(height)}',
                ha='center',
                va='bottom',
                fontsize=12,
                fontweight='bold'
            )
        
        # Customize chart
        ax.set_xlabel('Xếp loại', fontsize=12, fontweight='bold')
        ax.set_ylabel('Số lượng sinh viên', fontsize=12, fontweight='bold')
        ax.set_title('Phân bố xếp loại sinh viên\n(Chỉ tính sinh viên có đủ điểm 3 môn)', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3)
        
        # Save chart
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _generate_score_comparison(self, students: List[Student], output_path: str):
        """
        Generate bar chart comparing average scores by subject
        
        Note: Only includes students with all three scores
        
        Args:
            students: List of Student objects (should be pre-filtered for complete scores)
            output_path: Path to save chart image
        """
        # Calculate average scores (students already filtered for complete scores)
        math_scores = [s.math_score for s in students]
        lit_scores = [s.literature_score for s in students]
        eng_scores = [s.english_score for s in students]
        
        avg_math = sum(math_scores) / len(math_scores) if math_scores else 0
        avg_lit = sum(lit_scores) / len(lit_scores) if lit_scores else 0
        avg_eng = sum(eng_scores) / len(eng_scores) if eng_scores else 0
        
        # Prepare data
        subjects = ['Toán', 'Văn', 'Anh']
        averages = [avg_math, avg_lit, avg_eng]
        colors = ['#2196F3', '#9C27B0', '#FF5722']
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create bars
        bars = ax.bar(subjects, averages, color=colors, alpha=0.8, edgecolor='black')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2.,
                height,
                f'{height:.2f}',
                ha='center',
                va='bottom',
                fontsize=12,
                fontweight='bold'
            )
        
        # Add horizontal line at 5.0 (average threshold)
        ax.axhline(y=5.0, color='red', linestyle='--', linewidth=2, alpha=0.5, label='Điểm trung bình (5.0)')
        
        # Customize chart
        ax.set_xlabel('Môn học', fontsize=12, fontweight='bold')
        ax.set_ylabel('Điểm trung bình', fontsize=12, fontweight='bold')
        ax.set_title('So sánh điểm trung bình các môn\n(Chỉ tính sinh viên có đủ điểm 3 môn)', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_ylim(0, 10)
        ax.grid(axis='y', alpha=0.3)
        ax.legend()
        
        # Save chart
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _generate_hometown_distribution(self, students: List[Student], output_path: str):
        """
        Generate pie chart showing hometown distribution (top 5)
        
        Args:
            students: List of Student objects
            output_path: Path to save chart image
        """
        # Calculate hometown distribution
        hometown_dist = {}
        for student in students:
            if student.hometown:
                hometown_dist[student.hometown] = hometown_dist.get(student.hometown, 0) + 1
        
        # Get top 5 hometowns
        sorted_hometowns = sorted(hometown_dist.items(), key=lambda x: x[1], reverse=True)
        top_5 = sorted_hometowns[:5]
        
        # Calculate "Others" category
        others_count = sum(count for _, count in sorted_hometowns[5:])
        
        # Prepare data
        labels = [hometown for hometown, _ in top_5]
        sizes = [count for _, count in top_5]
        
        if others_count > 0:
            labels.append('Khác')
            sizes.append(others_count)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create pie chart
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 11}
        )
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        # Equal aspect ratio ensures circular pie
        ax.axis('equal')
        
        # Title
        ax.set_title('Phân bố sinh viên theo quê quán (Top 5)', fontsize=14, fontweight='bold', pad=20)
        
        # Save chart
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _generate_score_histogram(self, students: List[Student], output_path: str):
        """
        Generate histogram showing distribution of average scores
        
        Args:
            students: List of Student objects
            output_path: Path to save chart image
        """
        # Calculate average scores
        avg_scores = []
        for student in students:
            avg = student.get_average_score()
            if avg is not None:
                avg_scores.append(avg)
        
        if not avg_scores:
            return
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create histogram
        n, bins, patches = ax.hist(
            avg_scores,
            bins=[0, 2, 4, 5, 6.5, 8, 10],
            color='#3F51B5',
            alpha=0.7,
            edgecolor='black',
            linewidth=1.5
        )
        
        # Color code bins by grade
        colors = ['#F44336', '#FF9800', '#FFC107', '#8BC34A', '#4CAF50']
        for i, patch in enumerate(patches):
            if i < len(colors):
                patch.set_facecolor(colors[i])
        
        # Add value labels on bars
        for i in range(len(n)):
            if n[i] > 0:
                ax.text(
                    (bins[i] + bins[i+1])/2,
                    n[i],
                    f'{int(n[i])}',
                    ha='center',
                    va='bottom',
                    fontsize=11,
                    fontweight='bold'
                )
        
        # Add vertical lines for grade thresholds
        ax.axvline(x=5.0, color='red', linestyle='--', linewidth=2, alpha=0.5, label='Trung bình (5.0)')
        ax.axvline(x=6.5, color='orange', linestyle='--', linewidth=2, alpha=0.5, label='Khá (6.5)')
        ax.axvline(x=8.0, color='green', linestyle='--', linewidth=2, alpha=0.5, label='Giỏi (8.0)')
        
        # Customize chart
        ax.set_xlabel('Điểm trung bình', fontsize=12, fontweight='bold')
        ax.set_ylabel('Số lượng sinh viên', fontsize=12, fontweight='bold')
        ax.set_title('Phân bố điểm trung bình\n(Chỉ tính sinh viên có đủ điểm 3 môn)', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3)
        ax.legend()
        
        # Save chart
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
