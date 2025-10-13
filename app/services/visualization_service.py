"""
Visualization Service - Creates beautiful statistical charts using Seaborn
"""
import io
import base64
from typing import Dict, Any, List
from sqlmodel import Session, select
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from app.models.student import Student


class VisualizationService:
    """Service for creating beautiful visualizations with Seaborn"""
    
    def __init__(self):
        sns.set_theme(style="whitegrid")
        sns.set_palette("husl")
    
    def _students_to_dataframe(self, students: List[Student]) -> pd.DataFrame:
        data = []
        for student in students:
            if all([student.math_score is not None, student.literature_score is not None, student.english_score is not None]):
                data.append({
                    'student_id': student.student_id,
                    'first_name': student.first_name,
                    'last_name': student.last_name,
                    'age': student.get_age() if student.get_age() else None,
                    'hometown': student.hometown,
                    'math_score': student.math_score,
                    'literature_score': student.literature_score,
                    'english_score': student.english_score,
                    'average_score': student.get_average_score(),
                    'grade': student.get_grade()
                })
        return pd.DataFrame(data)
    
    def _fig_to_base64(self, fig) -> str:
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        plt.close(fig)
        return img_base64
    
    def generate_score_distribution_plot(self, db: Session) -> Dict[str, Any]:
        statement = select(Student)
        students = db.exec(statement).all()
        if not students:
            return {"success": False, "message": "No student data available"}
        df = self._students_to_dataframe(students)
        if df.empty:
            return {"success": False, "message": "No students with complete scores"}
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Score Distribution Analysis', fontsize=16, fontweight='bold')
        score_data = df[['math_score', 'literature_score', 'english_score']].melt(var_name='Subject', value_name='Score')
        score_data['Subject'] = score_data['Subject'].str.replace('_score', '').str.title()
        sns.violinplot(data=score_data, x='Subject', y='Score', ax=axes[0, 0])
        axes[0, 0].set_title('Score Distribution by Subject')
        axes[0, 0].set_ylabel('Score')
        sns.histplot(data=df, x='average_score', bins=20, kde=True, ax=axes[0, 1])
        axes[0, 1].set_title('Average Score Distribution')
        axes[0, 1].set_xlabel('Average Score')
        axes[0, 1].set_ylabel('Count')
        grade_counts = df['grade'].value_counts()
        axes[1, 0].pie(grade_counts.values, labels=grade_counts.index, autopct='%1.1f%%')
        axes[1, 0].set_title('Grade Distribution')
        sns.boxplot(data=df[['math_score', 'literature_score', 'english_score']], ax=axes[1, 1])
        axes[1, 1].set_title('Score Comparison by Subject')
        axes[1, 1].set_ylabel('Score')
        axes[1, 1].set_xticklabels(['Math', 'Literature', 'English'])
        plt.tight_layout()
        return {"success": True, "chart_type": "score_distribution", "image_base64": self._fig_to_base64(fig), "total_students": len(df)}
    
    def generate_correlation_heatmap(self, db: Session) -> Dict[str, Any]:
        statement = select(Student)
        students = db.exec(statement).all()
        df = self._students_to_dataframe(students)
        if df.empty:
            return {"success": False, "message": "No data"}
        numeric_cols = ['math_score', 'literature_score', 'english_score', 'average_score']
        if 'age' in df.columns:
            numeric_cols.append('age')
        corr_df = df[numeric_cols].corr()
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr_df, annot=True, fmt='.2f', cmap='coolwarm', center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
        ax.set_title('Score Correlation Heatmap', fontsize=14, fontweight='bold')
        plt.tight_layout()
        return {"success": True, "chart_type": "correlation_heatmap", "image_base64": self._fig_to_base64(fig), "total_students": len(df)}
    
    def generate_hometown_analysis(self, db: Session) -> Dict[str, Any]:
        return {"success": False, "message": "Not implemented yet"}
    
    def generate_age_performance_plot(self, db: Session) -> Dict[str, Any]:
        return {"success": False, "message": "Not implemented yet"}
    
    def generate_performance_categories(self, db: Session) -> Dict[str, Any]:
        return {"success": False, "message": "Not implemented yet"}
    
    def generate_comprehensive_report(self, db: Session) -> Dict[str, Any]:
        charts = []
        charts.append(self.generate_score_distribution_plot(db))
        charts.append(self.generate_correlation_heatmap(db))
        successful_charts = [c for c in charts if c.get('success')]
        return {"success": True, "total_charts": len(successful_charts), "charts": successful_charts}


visualization_service = VisualizationService()
