"""
Report Generator Service
Generates comprehensive reports with Excel files and visualization charts
"""

import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.models.student import Student


class ReportGeneratorService:
    """Service for generating comprehensive student reports"""
    
    def __init__(self):
        self.base_report_dir = "reports"
        self.ensure_report_directory()
        
        # Set style for charts
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 10
        
    def ensure_report_directory(self):
        """Ensure the base reports directory exists"""
        os.makedirs(self.base_report_dir, exist_ok=True)
    
    def create_report_folder(self, prefix: str = "crawl") -> str:
        """Create a timestamped folder for the report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"{prefix}_{timestamp}"
        folder_path = os.path.join(self.base_report_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path
    
    def generate_comprehensive_report(
        self, 
        students: List[Student], 
        report_type: str = "crawl",
        additional_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive report with Excel file and multiple charts
        
        Args:
            students: List of Student objects
            report_type: Type of report (crawl, export, analysis, etc.)
            additional_info: Additional information to include in the report
            
        Returns:
            Dictionary with report information
        """
        if not students:
            raise ValueError("No student data provided for report generation")
        
        # Debug logging
        print(f"DEBUG: Type of students: {type(students)}")
        if students:
            print(f"DEBUG: Type of first student: {type(students[0])}")
            print(f"DEBUG: First student: {students[0]}")
        
        # Create report folder
        report_folder = self.create_report_folder(prefix=report_type)
        
        # Convert students to DataFrame
        df = self._students_to_dataframe(students)
        
        # Generate Excel file
        excel_path = self._generate_excel_report(df, report_folder, additional_info)
        
        # Generate all charts
        charts = self._generate_all_charts(df, report_folder)
        
        # Generate summary file
        summary_path = self._generate_summary_file(df, report_folder, additional_info, charts)
        
        return {
            "report_folder": report_folder,
            "excel_file": excel_path,
            "charts": charts,
            "summary_file": summary_path,
            "total_students": len(students),
            "timestamp": datetime.now().isoformat()
        }
    
    def _students_to_dataframe(self, students: List[Student]) -> pd.DataFrame:
        """Convert list of Student objects to pandas DataFrame"""
        data = []
        for student in students:
            # Handle both Student objects and dict representations
            if isinstance(student, dict):
                student_dict = student
            elif hasattr(student, 'dict'):
                student_dict = student.dict()
            else:
                # Direct attribute access
                student_dict = {
                    'student_id': student.student_id,
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'email': student.email,
                    'birth_date': student.birth_date,
                    'hometown': student.hometown,
                    'math_score': student.math_score,
                    'literature_score': student.literature_score,
                    'english_score': student.english_score,
                    'average_score': student.average_score,
                    'grade': student.grade
                }
            
            data.append({
                'Student ID': student_dict.get('student_id'),
                'First Name': student_dict.get('first_name'),
                'Last Name': student_dict.get('last_name'),
                'Full Name': f"{student_dict.get('first_name', '')} {student_dict.get('last_name', '')}",
                'Email': student_dict.get('email'),
                'Birth Date': student_dict.get('birth_date'),
                'Age': student_dict.get('age') if 'age' in student_dict else None,
                'Hometown': student_dict.get('hometown'),
                'Math Score': float(student_dict.get('math_score', 0)) if student_dict.get('math_score') is not None else 0.0,
                'Literature Score': float(student_dict.get('literature_score', 0)) if student_dict.get('literature_score') is not None else 0.0,
                'English Score': float(student_dict.get('english_score', 0)) if student_dict.get('english_score') is not None else 0.0,
                'Average Score': float(student_dict.get('average_score', 0)) if student_dict.get('average_score') is not None else 0.0,
                'Grade': student_dict.get('grade', 'N/A')
            })
        
        df = pd.DataFrame(data)
        
        # Ensure numeric columns are float type
        numeric_columns = ['Math Score', 'Literature Score', 'English Score', 'Average Score']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
        
        return df
    
    def _generate_excel_report(
        self, 
        df: pd.DataFrame, 
        report_folder: str,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate Excel file with multiple sheets"""
        excel_path = os.path.join(report_folder, "student_report.xlsx")
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Main data sheet
            df.to_excel(writer, sheet_name='Students', index=False)
            
            # Statistics sheet
            stats_df = self._calculate_statistics(df)
            stats_df.to_excel(writer, sheet_name='Statistics')
            
            # Grade distribution sheet
            grade_dist = df['Grade'].value_counts().reset_index()
            grade_dist.columns = ['Grade', 'Count']
            grade_dist.to_excel(writer, sheet_name='Grade Distribution', index=False)
            
            # Hometown analysis sheet
            hometown_stats = df.groupby('Hometown').agg({
                'Student ID': 'count',
                'Average Score': 'mean'
            }).reset_index()
            hometown_stats.columns = ['Hometown', 'Student Count', 'Avg Score']
            hometown_stats = hometown_stats.sort_values('Avg Score', ascending=False)
            hometown_stats.to_excel(writer, sheet_name='Hometown Analysis', index=False)
            
            # Top performers sheet
            top_performers = df.nlargest(20, 'Average Score')[['Student ID', 'Full Name', 'Average Score', 'Grade']]
            top_performers.to_excel(writer, sheet_name='Top Performers', index=False)
            
            # Subject-wise analysis
            subject_analysis = pd.DataFrame({
                'Subject': ['Math', 'Literature', 'English'],
                'Average': [df['Math Score'].mean(), df['Literature Score'].mean(), df['English Score'].mean()],
                'Max': [df['Math Score'].max(), df['Literature Score'].max(), df['English Score'].max()],
                'Min': [df['Math Score'].min(), df['Literature Score'].min(), df['English Score'].min()],
                'Std Dev': [df['Math Score'].std(), df['Literature Score'].std(), df['English Score'].std()]
            })
            subject_analysis.to_excel(writer, sheet_name='Subject Analysis', index=False)
            
            # Additional info sheet
            if additional_info:
                info_df = pd.DataFrame(list(additional_info.items()), columns=['Key', 'Value'])
                info_df.to_excel(writer, sheet_name='Report Info', index=False)
        
        return excel_path
    
    def _calculate_statistics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate comprehensive statistics"""
        stats = {
            'Total Students': len(df),
            'Math Average': df['Math Score'].mean(),
            'Literature Average': df['Literature Score'].mean(),
            'English Average': df['English Score'].mean(),
            'Overall Average': df['Average Score'].mean(),
            'Math Median': df['Math Score'].median(),
            'Literature Median': df['Literature Score'].median(),
            'English Median': df['English Score'].median(),
            'Math Std Dev': df['Math Score'].std(),
            'Literature Std Dev': df['Literature Score'].std(),
            'English Std Dev': df['English Score'].std(),
            'Excellent Count': (df['Grade'] == 'Excellent').sum(),
            'Good Count': (df['Grade'] == 'Good').sum(),
            'Average Count': (df['Grade'] == 'Average').sum(),
            'Poor Count': (df['Grade'] == 'Poor').sum(),
        }
        return pd.DataFrame(list(stats.items()), columns=['Metric', 'Value'])
    
    def _generate_all_charts(self, df: pd.DataFrame, report_folder: str) -> List[Dict[str, str]]:
        """Generate all visualization charts"""
        charts = []
        
        # 1. Score Distribution (Histogram)
        chart_path = self._create_score_distribution_chart(df, report_folder)
        charts.append({"name": "score_distribution", "path": chart_path})
        
        # 2. Grade Distribution (Pie Chart)
        chart_path = self._create_grade_pie_chart(df, report_folder)
        charts.append({"name": "grade_distribution", "path": chart_path})
        
        # 3. Subject Comparison (Bar Chart)
        chart_path = self._create_subject_comparison_chart(df, report_folder)
        charts.append({"name": "subject_comparison", "path": chart_path})
        
        # 4. Score Correlation Heatmap
        chart_path = self._create_correlation_heatmap(df, report_folder)
        charts.append({"name": "correlation_heatmap", "path": chart_path})
        
        # 5. Hometown Performance (Bar Chart)
        chart_path = self._create_hometown_performance_chart(df, report_folder)
        charts.append({"name": "hometown_performance", "path": chart_path})
        
        # 6. Box Plot for Scores
        chart_path = self._create_score_boxplot(df, report_folder)
        charts.append({"name": "score_boxplot", "path": chart_path})
        
        # 7. Top 10 Students (Bar Chart)
        chart_path = self._create_top_students_chart(df, report_folder)
        charts.append({"name": "top_students", "path": chart_path})
        
        # 8. Score Distribution by Subject (Violin Plot)
        chart_path = self._create_violin_plot(df, report_folder)
        charts.append({"name": "violin_plot", "path": chart_path})
        
        # 9. Performance Trends (if age data available)
        if 'Age' in df.columns and df['Age'].notna().any():
            chart_path = self._create_age_performance_chart(df, report_folder)
            charts.append({"name": "age_performance", "path": chart_path})
        
        # 10. Grade Distribution by Hometown
        chart_path = self._create_grade_by_hometown_chart(df, report_folder)
        charts.append({"name": "grade_by_hometown", "path": chart_path})
        
        # 11. Score Range Analysis (NEW!)
        chart_path = self._create_score_range_analysis(df, report_folder)
        charts.append({"name": "score_range_analysis", "path": chart_path})
        
        # 12. Average Score by Hometown (Horizontal Bar) (NEW!)
        chart_path = self._create_avg_score_by_hometown(df, report_folder)
        charts.append({"name": "avg_score_by_hometown", "path": chart_path})
        
        # 13. Score Density Plot (NEW!)
        chart_path = self._create_score_density_plot(df, report_folder)
        charts.append({"name": "score_density", "path": chart_path})
        
        # 14. Performance Radar Chart (Top 5 Students) (NEW!)
        chart_path = self._create_performance_radar(df, report_folder)
        charts.append({"name": "performance_radar", "path": chart_path})
        
        # 15. Score Scatter Matrix (NEW!)
        chart_path = self._create_score_scatter_matrix(df, report_folder)
        charts.append({"name": "score_scatter_matrix", "path": chart_path})
        
        # 16. Grade Count by Score Range (NEW!)
        chart_path = self._create_grade_count_chart(df, report_folder)
        charts.append({"name": "grade_count", "path": chart_path})
        
        # 17. Subject Performance Comparison (Line Chart) (NEW!)
        chart_path = self._create_subject_line_comparison(df, report_folder)
        charts.append({"name": "subject_line_comparison", "path": chart_path})
        
        # 18. Cumulative Score Distribution (NEW!)
        chart_path = self._create_cumulative_distribution(df, report_folder)
        charts.append({"name": "cumulative_distribution", "path": chart_path})
        
        # 19. Heatmap of Student Performance (NEW!)
        chart_path = self._create_student_performance_heatmap(df, report_folder)
        charts.append({"name": "student_performance_heatmap", "path": chart_path})
        
        # 20. Statistical Summary Chart (NEW!)
        chart_path = self._create_statistical_summary(df, report_folder)
        charts.append({"name": "statistical_summary", "path": chart_path})
        
        return charts
    
    def _create_score_distribution_chart(self, df: pd.DataFrame, report_folder: str) -> str:
        """Create score distribution histogram"""
        plt.figure(figsize=(12, 6))
        
        plt.subplot(1, 3, 1)
        plt.hist(df['Math Score'], bins=20, color='skyblue', edgecolor='black', alpha=0.7)
        plt.xlabel('Math Score')
        plt.ylabel('Frequency')
        plt.title('Math Score Distribution')
        plt.axvline(df['Math Score'].mean(), color='red', linestyle='--', label=f'Mean: {df["Math Score"].mean():.2f}')
        plt.legend()
        
        plt.subplot(1, 3, 2)
        plt.hist(df['Literature Score'], bins=20, color='lightgreen', edgecolor='black', alpha=0.7)
        plt.xlabel('Literature Score')
        plt.ylabel('Frequency')
        plt.title('Literature Score Distribution')
        plt.axvline(df['Literature Score'].mean(), color='red', linestyle='--', label=f'Mean: {df["Literature Score"].mean():.2f}')
        plt.legend()
        
        plt.subplot(1, 3, 3)
        plt.hist(df['English Score'], bins=20, color='lightcoral', edgecolor='black', alpha=0.7)
        plt.xlabel('English Score')
        plt.ylabel('Frequency')
        plt.title('English Score Distribution')
        plt.axvline(df['English Score'].mean(), color='red', linestyle='--', label=f'Mean: {df["English Score"].mean():.2f}')
        plt.legend()
        
        plt.tight_layout()
        chart_path = os.path.join(report_folder, "01_score_distribution.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_grade_pie_chart(self, df: pd.DataFrame, report_folder: str) -> str:
        """Create grade distribution pie chart"""
        plt.figure(figsize=(10, 8))
        
        grade_counts = df['Grade'].value_counts()
        colors = ['#4CAF50', '#2196F3', '#FFC107', '#F44336']
        explode = [0.1 if i == 0 else 0 for i in range(len(grade_counts))]
        
        plt.pie(grade_counts.values, labels=grade_counts.index, autopct='%1.1f%%',
                startangle=90, colors=colors, explode=explode, shadow=True)
        plt.title('Grade Distribution', fontsize=16, fontweight='bold')
        
        chart_path = os.path.join(report_folder, "02_grade_distribution.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_subject_comparison_chart(self, df: pd.DataFrame, report_folder: str) -> str:
        """Create subject comparison bar chart"""
        plt.figure(figsize=(10, 6))
        
        subjects = ['Math Score', 'Literature Score', 'English Score']
        averages = [df[subject].mean() for subject in subjects]
        
        bars = plt.bar(['Math', 'Literature', 'English'], averages, 
                      color=['skyblue', 'lightgreen', 'lightcoral'], edgecolor='black')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        plt.ylabel('Average Score', fontsize=12)
        plt.title('Average Score by Subject', fontsize=16, fontweight='bold')
        plt.ylim(0, 10)
        plt.grid(axis='y', alpha=0.3)
        
        chart_path = os.path.join(report_folder, "03_subject_comparison.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_correlation_heatmap(self, df: pd.DataFrame, report_folder: str) -> str:
        """Create correlation heatmap"""
        plt.figure(figsize=(10, 8))
        
        score_cols = ['Math Score', 'Literature Score', 'English Score', 'Average Score']
        corr_matrix = df[score_cols].corr()
        
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, linewidths=1, cbar_kws={"shrink": 0.8},
                   fmt='.2f', vmin=-1, vmax=1)
        
        plt.title('Score Correlation Heatmap', fontsize=16, fontweight='bold', pad=20)
        
        chart_path = os.path.join(report_folder, "04_correlation_heatmap.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_hometown_performance_chart(self, df: pd.DataFrame, report_folder: str) -> str:
        """Create hometown performance chart"""
        plt.figure(figsize=(14, 8))
        
        hometown_stats = df.groupby('Hometown').agg({
            'Average Score': 'mean',
            'Student ID': 'count'
        }).sort_values('Average Score', ascending=False).head(15)
        
        x = range(len(hometown_stats))
        
        # Create bar chart
        bars = plt.bar(x, hometown_stats['Average Score'], color='steelblue', edgecolor='black', alpha=0.7)
        
        # Add student count labels
        for i, (idx, row) in enumerate(hometown_stats.iterrows()):
            plt.text(i, row['Average Score'] + 0.1, f"n={row['Student ID']}", 
                    ha='center', fontsize=9)
        
        plt.xlabel('Hometown', fontsize=12)
        plt.ylabel('Average Score', fontsize=12)
        plt.title('Top 15 Hometowns by Average Score', fontsize=16, fontweight='bold')
        plt.xticks(x, hometown_stats.index, rotation=45, ha='right')
        plt.ylim(0, 10)
        plt.grid(axis='y', alpha=0.3)
        
        chart_path = os.path.join(report_folder, "05_hometown_performance.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_score_boxplot(self, df: pd.DataFrame, report_folder: str) -> str:
        """Create box plot for score distribution"""
        plt.figure(figsize=(12, 8))
        
        data = [df['Math Score'], df['Literature Score'], df['English Score'], df['Average Score']]
        labels = ['Math', 'Literature', 'English', 'Average']
        
        bp = plt.boxplot(data, labels=labels, patch_artist=True, notch=True,
                        boxprops=dict(facecolor='lightblue', alpha=0.7),
                        medianprops=dict(color='red', linewidth=2),
                        whiskerprops=dict(color='black', linewidth=1.5),
                        capprops=dict(color='black', linewidth=1.5))
        
        plt.ylabel('Score', fontsize=12)
        plt.title('Score Distribution Box Plot', fontsize=16, fontweight='bold')
        plt.ylim(0, 10)
        plt.grid(axis='y', alpha=0.3)
        
        chart_path = os.path.join(report_folder, "06_score_boxplot.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_top_students_chart(self, df: pd.DataFrame, report_folder: str) -> str:
        """Create top 10 students chart"""
        plt.figure(figsize=(12, 8))
        
        top_10 = df.nlargest(10, 'Average Score')[['Full Name', 'Average Score']]
        
        colors = plt.cm.viridis(np.linspace(0, 1, len(top_10)))
        bars = plt.barh(range(len(top_10)), top_10['Average Score'], color=colors, edgecolor='black')
        
        plt.yticks(range(len(top_10)), top_10['Full Name'])
        plt.xlabel('Average Score', fontsize=12)
        plt.title('Top 10 Students by Average Score', fontsize=16, fontweight='bold')
        plt.xlim(0, 10)
        plt.gca().invert_yaxis()
        
        # Add score labels
        for i, (idx, row) in enumerate(top_10.iterrows()):
            plt.text(row['Average Score'] + 0.1, i, f"{row['Average Score']:.2f}", 
                    va='center', fontsize=10, fontweight='bold')
        
        chart_path = os.path.join(report_folder, "07_top_students.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_violin_plot(self, df: pd.DataFrame, report_folder: str) -> str:
        """Create violin plot for score distribution"""
        plt.figure(figsize=(12, 8))
        
        # Prepare data for violin plot
        data_melted = pd.melt(df, value_vars=['Math Score', 'Literature Score', 'English Score'],
                             var_name='Subject', value_name='Score')
        
        sns.violinplot(x='Subject', y='Score', data=data_melted, palette='Set2')
        plt.title('Score Distribution by Subject (Violin Plot)', fontsize=16, fontweight='bold')
        plt.ylabel('Score', fontsize=12)
        plt.xlabel('Subject', fontsize=12)
        plt.ylim(0, 10)
        plt.grid(axis='y', alpha=0.3)
        
        chart_path = os.path.join(report_folder, "08_violin_plot.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_age_performance_chart(self, df: pd.DataFrame, report_folder: str) -> str:
        """Create age vs performance scatter plot"""
        plt.figure(figsize=(12, 8))
        
        df_clean = df.dropna(subset=['Age', 'Average Score'])
        
        plt.scatter(df_clean['Age'], df_clean['Average Score'], 
                   alpha=0.6, s=100, c=df_clean['Average Score'], 
                   cmap='viridis', edgecolors='black')
        
        # Add trend line
        z = np.polyfit(df_clean['Age'], df_clean['Average Score'], 1)
        p = np.poly1d(z)
        plt.plot(df_clean['Age'].sort_values(), p(df_clean['Age'].sort_values()), 
                "r--", linewidth=2, label='Trend')
        
        plt.xlabel('Age', fontsize=12)
        plt.ylabel('Average Score', fontsize=12)
        plt.title('Age vs Performance Analysis', fontsize=16, fontweight='bold')
        plt.colorbar(label='Average Score')
        plt.legend()
        plt.grid(alpha=0.3)
        
        chart_path = os.path.join(report_folder, "09_age_performance.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_grade_by_hometown_chart(self, df: pd.DataFrame, report_folder: str) -> str:
        """Create stacked bar chart for grade distribution by hometown"""
        plt.figure(figsize=(14, 8))
        
        # Get top 10 hometowns by student count
        top_hometowns = df['Hometown'].value_counts().head(10).index
        df_filtered = df[df['Hometown'].isin(top_hometowns)]
        
        # Create pivot table
        grade_hometown = pd.crosstab(df_filtered['Hometown'], df_filtered['Grade'])
        
        # Plot stacked bar chart
        grade_hometown.plot(kind='bar', stacked=True, 
                           color=['#4CAF50', '#2196F3', '#FFC107', '#F44336'],
                           figsize=(14, 8), edgecolor='black')
        
        plt.xlabel('Hometown', fontsize=12)
        plt.ylabel('Number of Students', fontsize=12)
        plt.title('Grade Distribution by Top 10 Hometowns', fontsize=16, fontweight='bold')
        plt.legend(title='Grade', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        
        chart_path = os.path.join(report_folder, "10_grade_by_hometown.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    # ========================================================================
    # NEW CHARTS (11-20)
    # ========================================================================
    
    def _create_score_range_analysis(self, df: pd.DataFrame, report_folder: str) -> str:
        """Create score range analysis chart"""
        plt.figure(figsize=(12, 6))
        
        # Define score ranges
        ranges = ['0-5', '5-6', '6-7', '7-8', '8-9', '9-10']
        subjects = ['Math Score', 'Literature Score', 'English Score']
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        x = np.arange(len(ranges))
        width = 0.25
        
        for i, subject in enumerate(subjects):
            counts = []
            for range_label in ranges:
                if range_label == '0-5':
                    count = ((df[subject] >= 0) & (df[subject] < 5)).sum()
                elif range_label == '5-6':
                    count = ((df[subject] >= 5) & (df[subject] < 6)).sum()
                elif range_label == '6-7':
                    count = ((df[subject] >= 6) & (df[subject] < 7)).sum()
                elif range_label == '7-8':
                    count = ((df[subject] >= 7) & (df[subject] < 8)).sum()
                elif range_label == '8-9':
                    count = ((df[subject] >= 8) & (df[subject] < 9)).sum()
                else:  # 9-10
                    count = ((df[subject] >= 9) & (df[subject] <= 10)).sum()
                counts.append(count)
            
            plt.bar(x + i*width, counts, width, label=subject.replace(' Score', ''), 
                   color=colors[i], alpha=0.8, edgecolor='black')
        
        plt.xlabel('Score Range', fontsize=12)
        plt.ylabel('Number of Students', fontsize=12)
        plt.title('Score Distribution by Range', fontsize=16, fontweight='bold')
        plt.xticks(x + width, ranges)
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        
        chart_path = os.path.join(report_folder, "11_score_range_analysis.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_avg_score_by_hometown(self, df: pd.DataFrame, report_folder: str) -> str:
        """Create average score by hometown horizontal bar chart"""
        plt.figure(figsize=(10, 8))
        
        hometown_stats = df.groupby('Hometown')['Average Score'].agg(['mean', 'count'])
        hometown_stats = hometown_stats[hometown_stats['count'] >= 2]  # At least 2 students
        hometown_stats = hometown_stats.sort_values('mean', ascending=True).tail(15)
        
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(hometown_stats)))
        bars = plt.barh(hometown_stats.index, hometown_stats['mean'], 
                       color=colors, edgecolor='black', alpha=0.8)
        
        # Add value labels
        for i, (idx, row) in enumerate(hometown_stats.iterrows()):
            plt.text(row['mean'] + 0.05, i, f"{row['mean']:.2f}", 
                    va='center', fontsize=9, fontweight='bold')
        
        plt.xlabel('Average Score', fontsize=12)
        plt.ylabel('Hometown', fontsize=12)
        plt.title('Average Score by Hometown (Top 15)', fontsize=16, fontweight='bold')
        plt.xlim(0, 10.5)
        plt.grid(axis='x', alpha=0.3)
        
        chart_path = os.path.join(report_folder, "12_avg_score_by_hometown.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_score_density_plot(self, df: pd.DataFrame, report_folder: str) -> str:
        """Create density plot for all subjects"""
        plt.figure(figsize=(12, 6))
        
        subjects = ['Math Score', 'Literature Score', 'English Score']
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        for subject, color in zip(subjects, colors):
            df[subject].plot(kind='density', color=color, linewidth=2.5, 
                           label=subject.replace(' Score', ''), alpha=0.7)
        
        plt.xlabel('Score', fontsize=12)
        plt.ylabel('Density', fontsize=12)
        plt.title('Score Density Distribution', fontsize=16, fontweight='bold')
        plt.legend(fontsize=11)
        plt.grid(alpha=0.3)
        plt.xlim(0, 10)
        
        chart_path = os.path.join(report_folder, "13_score_density.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_performance_radar(self, df: pd.DataFrame, report_folder: str) -> str:
        """Create radar chart for top 5 students"""
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection='polar')
        
        # Get top 5 students
        top_students = df.nlargest(5, 'Average Score')
        
        categories = ['Math', 'Literature', 'English']
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]
        
        colors = plt.cm.Set3(np.linspace(0, 1, 5))
        
        for idx, (_, student) in enumerate(top_students.iterrows()):
            values = [
                student['Math Score'],
                student['Literature Score'],
                student['English Score']
            ]
            values += values[:1]
            
            ax.plot(angles, values, 'o-', linewidth=2, 
                   label=f"{student['Full Name']} ({student['Average Score']:.2f})",
                   color=colors[idx])
            ax.fill(angles, values, alpha=0.15, color=colors[idx])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=11)
        ax.set_ylim(0, 10)
        ax.set_yticks([2, 4, 6, 8, 10])
        ax.set_title('Top 5 Students Performance Radar', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)
        ax.grid(True)
        
        chart_path = os.path.join(report_folder, "14_performance_radar.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_score_scatter_matrix(self, df: pd.DataFrame, report_folder: str) -> str:
        """Create scatter matrix for score relationships"""
        from pandas.plotting import scatter_matrix
        
        fig = plt.figure(figsize=(12, 12))
        scatter_matrix(df[['Math Score', 'Literature Score', 'English Score', 'Average Score']],
                      alpha=0.6, diagonal='hist', 
                      color='#4ECDC4', edgecolor='black', s=50, figsize=(12, 12))
        
        plt.suptitle('Score Correlation Scatter Matrix', fontsize=16, fontweight='bold')
        
        chart_path = os.path.join(report_folder, "15_score_scatter_matrix.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_grade_count_chart(self, df: pd.DataFrame, report_folder: str) -> str:
        """Create grade count donut chart"""
        plt.figure(figsize=(10, 8))
        
        grade_counts = df['Grade'].value_counts()
        colors = plt.cm.Spectral(np.linspace(0.2, 0.8, len(grade_counts)))
        
        wedges, texts, autotexts = plt.pie(grade_counts, labels=grade_counts.index,
                                           autopct='%1.1f%%', startangle=90,
                                           colors=colors, explode=[0.05]*len(grade_counts),
                                           wedgeprops={'edgecolor': 'black', 'linewidth': 2})
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(11)
            autotext.set_fontweight('bold')
        
        # Add count in center
        centre_circle = plt.Circle((0, 0), 0.70, fc='white', linewidth=1.5, edgecolor='black')
        plt.gca().add_artist(centre_circle)
        
        plt.text(0, 0, f'Total\n{len(df)}', ha='center', va='center', 
                fontsize=20, fontweight='bold')
        
        plt.title('Grade Distribution (Donut Chart)', fontsize=16, fontweight='bold', pad=20)
        
        chart_path = os.path.join(report_folder, "16_grade_count.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_subject_line_comparison(self, df: pd.DataFrame, report_folder: str) -> str:
        """Create line chart comparing subjects across students"""
        plt.figure(figsize=(14, 6))
        
        # Sort by average score
        df_sorted = df.sort_values('Average Score', ascending=False).head(30)
        
        x = range(len(df_sorted))
        plt.plot(x, df_sorted['Math Score'], marker='o', linewidth=2, 
                label='Math', color='#FF6B6B', markersize=6)
        plt.plot(x, df_sorted['Literature Score'], marker='s', linewidth=2, 
                label='Literature', color='#4ECDC4', markersize=6)
        plt.plot(x, df_sorted['English Score'], marker='^', linewidth=2, 
                label='English', color='#45B7D1', markersize=6)
        plt.plot(x, df_sorted['Average Score'], marker='D', linewidth=2.5, 
                label='Average', color='#95E1D3', markersize=7, linestyle='--')
        
        plt.xlabel('Student Rank (Top 30)', fontsize=12)
        plt.ylabel('Score', fontsize=12)
        plt.title('Subject Performance Comparison (Top 30 Students)', 
                 fontsize=16, fontweight='bold')
        plt.legend(fontsize=11, loc='best')
        plt.grid(alpha=0.3)
        plt.ylim(0, 10.5)
        
        chart_path = os.path.join(report_folder, "17_subject_line_comparison.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_cumulative_distribution(self, df: pd.DataFrame, report_folder: str) -> str:
        """Create cumulative distribution function"""
        plt.figure(figsize=(12, 6))
        
        subjects = ['Math Score', 'Literature Score', 'English Score', 'Average Score']
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#95E1D3']
        
        for subject, color in zip(subjects, colors):
            sorted_scores = np.sort(df[subject])
            cumulative = np.arange(1, len(sorted_scores) + 1) / len(sorted_scores) * 100
            plt.plot(sorted_scores, cumulative, linewidth=2.5, 
                    label=subject.replace(' Score', ''), color=color)
        
        plt.xlabel('Score', fontsize=12)
        plt.ylabel('Cumulative Percentage (%)', fontsize=12)
        plt.title('Cumulative Score Distribution', fontsize=16, fontweight='bold')
        plt.legend(fontsize=11)
        plt.grid(alpha=0.3)
        plt.xlim(0, 10)
        plt.ylim(0, 100)
        
        chart_path = os.path.join(report_folder, "18_cumulative_distribution.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_student_performance_heatmap(self, df: pd.DataFrame, report_folder: str) -> str:
        """Create heatmap showing top 20 students performance"""
        plt.figure(figsize=(10, 12))
        
        # Get top 20 students
        top_students = df.nlargest(20, 'Average Score')
        
        # Create matrix
        data_matrix = top_students[['Math Score', 'Literature Score', 'English Score']].values
        student_names = [name[:15] + '...' if len(name) > 15 else name 
                        for name in top_students['Full Name']]
        
        sns.heatmap(data_matrix, annot=True, fmt='.2f', cmap='YlGnBu',
                   yticklabels=student_names, 
                   xticklabels=['Math', 'Literature', 'English'],
                   cbar_kws={'label': 'Score'}, linewidths=0.5, 
                   linecolor='gray', vmin=0, vmax=10)
        
        plt.title('Top 20 Students Performance Heatmap', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Subject', fontsize=12)
        plt.ylabel('Student', fontsize=12)
        plt.tight_layout()
        
        chart_path = os.path.join(report_folder, "19_student_performance_heatmap.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _create_statistical_summary(self, df: pd.DataFrame, report_folder: str) -> str:
        """Create statistical summary visualization"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Statistical Summary Dashboard', fontsize=18, fontweight='bold')
        
        # 1. Mean scores by subject
        ax1 = axes[0, 0]
        subjects = ['Math Score', 'Literature Score', 'English Score']
        means = [df[s].mean() for s in subjects]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        bars = ax1.bar(range(len(subjects)), means, color=colors, 
                      edgecolor='black', alpha=0.8)
        ax1.set_xticks(range(len(subjects)))
        ax1.set_xticklabels([s.replace(' Score', '') for s in subjects])
        ax1.set_ylabel('Average Score', fontsize=11)
        ax1.set_title('Mean Scores by Subject', fontsize=13, fontweight='bold')
        ax1.set_ylim(0, 10)
        ax1.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar, mean in zip(bars, means):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{mean:.2f}', ha='center', va='bottom', fontweight='bold')
        
        # 2. Standard deviation
        ax2 = axes[0, 1]
        stds = [df[s].std() for s in subjects]
        bars = ax2.bar(range(len(subjects)), stds, color=colors, 
                      edgecolor='black', alpha=0.8)
        ax2.set_xticks(range(len(subjects)))
        ax2.set_xticklabels([s.replace(' Score', '') for s in subjects])
        ax2.set_ylabel('Standard Deviation', fontsize=11)
        ax2.set_title('Score Variability', fontsize=13, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        for bar, std in zip(bars, stds):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{std:.2f}', ha='center', va='bottom', fontweight='bold')
        
        # 3. Min-Max range
        ax3 = axes[1, 0]
        x_pos = np.arange(len(subjects))
        mins = [df[s].min() for s in subjects]
        maxs = [df[s].max() for s in subjects]
        
        ax3.barh(x_pos, maxs, color=colors, alpha=0.5, label='Maximum', 
                edgecolor='black')
        ax3.barh(x_pos, mins, color=colors, alpha=0.9, label='Minimum', 
                edgecolor='black')
        ax3.set_yticks(x_pos)
        ax3.set_yticklabels([s.replace(' Score', '') for s in subjects])
        ax3.set_xlabel('Score', fontsize=11)
        ax3.set_title('Score Range (Min-Max)', fontsize=13, fontweight='bold')
        ax3.legend()
        ax3.grid(axis='x', alpha=0.3)
        
        # 4. Median and quartiles
        ax4 = axes[1, 1]
        medians = [df[s].median() for s in subjects]
        q1 = [df[s].quantile(0.25) for s in subjects]
        q3 = [df[s].quantile(0.75) for s in subjects]
        
        ax4.plot(range(len(subjects)), medians, 'o-', linewidth=2.5, 
                markersize=10, label='Median', color='#2E86AB')
        ax4.plot(range(len(subjects)), q1, 's--', linewidth=2, 
                markersize=8, label='Q1 (25%)', color='#A23B72')
        ax4.plot(range(len(subjects)), q3, '^--', linewidth=2, 
                markersize=8, label='Q3 (75%)', color='#F18F01')
        
        ax4.set_xticks(range(len(subjects)))
        ax4.set_xticklabels([s.replace(' Score', '') for s in subjects])
        ax4.set_ylabel('Score', fontsize=11)
        ax4.set_title('Median and Quartiles', fontsize=13, fontweight='bold')
        ax4.legend()
        ax4.grid(alpha=0.3)
        ax4.set_ylim(0, 10)
        
        plt.tight_layout()
        
        chart_path = os.path.join(report_folder, "20_statistical_summary.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _generate_summary_file(
        self, 
        df: pd.DataFrame, 
        report_folder: str,
        additional_info: Optional[Dict[str, Any]],
        charts: List[Dict[str, str]]
    ) -> str:
        """Generate HTML summary file"""
        summary_path = os.path.join(report_folder, "README.html")
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Student Report Summary</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2196F3;
            border-bottom: 3px solid #2196F3;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #4CAF50;
            margin-top: 30px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-label {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .chart {{
            margin: 20px 0;
            text-align: center;
        }}
        .chart img {{
            max-width: 100%;
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #2196F3;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Student Report Summary</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        
        <h2>📈 Key Statistics</h2>
        <div class="stats">
            <div class="stat-box">
                <div class="stat-label">Total Students</div>
                <div class="stat-value">{len(df)}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Math Average</div>
                <div class="stat-value">{df['Math Score'].mean():.2f}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Literature Average</div>
                <div class="stat-value">{df['Literature Score'].mean():.2f}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">English Average</div>
                <div class="stat-value">{df['English Score'].mean():.2f}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Overall Average</div>
                <div class="stat-value">{df['Average Score'].mean():.2f}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Excellent Students</div>
                <div class="stat-value">{(df['Grade'] == 'Excellent').sum()}</div>
            </div>
        </div>
        
        <h2>📁 Report Files</h2>
        <ul>
            <li><strong>Excel Report:</strong> student_report.xlsx</li>
            <li><strong>Charts:</strong> {len(charts)} visualization charts</li>
        </ul>
        
        <h2>📊 Visualizations</h2>
"""
        
        # Add all charts
        for chart in charts:
            chart_name = chart['name'].replace('_', ' ').title()
            chart_file = os.path.basename(chart['path'])
            html_content += f"""
        <div class="chart">
            <h3>{chart_name}</h3>
            <img src="{chart_file}" alt="{chart_name}">
        </div>
"""
        
        html_content += """
    </div>
</body>
</html>
"""
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return summary_path


# Create singleton instance
report_generator = ReportGeneratorService()
