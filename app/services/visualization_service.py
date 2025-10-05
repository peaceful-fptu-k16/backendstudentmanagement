"""
Visualization Service using Seaborn
Provides advanced data visualization capabilities
"""
import io
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
from sqlmodel import Session

from app.crud.student import student_crud

# Set matplotlib to use non-interactive backend
matplotlib.use('Agg')

# Set seaborn style
sns.set_theme(style="whitegrid", palette="pastel")
sns.set_context("notebook", font_scale=1.2)


class VisualizationService:
    """Service for creating beautiful visualizations with Seaborn"""
    
    @staticmethod
    def _fig_to_base64(fig) -> str:
        """Convert matplotlib figure to base64 encoded string"""
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close(fig)
        return image_base64
    
    @staticmethod
    def create_students_dataframe(db: Session) -> pd.DataFrame:
        """Create a DataFrame from all students"""
        students = student_crud.get_all(db=db)
        
        if not students:
            return pd.DataFrame()
        
        data = []
        for student in students:
            # Calculate average score
            scores = [s for s in [student.math_score, student.literature_score, student.english_score] if s is not None]
            avg_score = sum(scores) / len(scores) if scores else 0
            
            data.append({
                'id': student.id,
                'student_id': student.student_id,
                'name': f"{student.first_name} {student.last_name}",
                'age': (datetime.now().date() - student.birth_date).days // 365 if student.birth_date else None,
                'hometown': student.hometown,
                'math_score': student.math_score,
                'literature_score': student.literature_score,
                'english_score': student.english_score,
                'average_score': avg_score
            })
        
        return pd.DataFrame(data)
    
    def generate_score_distribution_plot(self, db: Session) -> Dict[str, Any]:
        """Generate score distribution plot using Seaborn"""
        df = self.create_students_dataframe(db)
        
        if df.empty:
            return {"error": "No data available"}
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('📊 Student Score Distribution Analysis', fontsize=16, fontweight='bold')
        
        # 1. Distribution of Average Scores (Histogram with KDE)
        sns.histplot(data=df, x='average_score', kde=True, ax=axes[0, 0], color='skyblue')
        axes[0, 0].set_title('Distribution of Average Scores', fontweight='bold')
        axes[0, 0].set_xlabel('Average Score')
        axes[0, 0].set_ylabel('Frequency')
        
        # 2. Box plot for all subjects
        subjects_data = df[['math_score', 'literature_score', 'english_score']].melt(
            var_name='Subject', value_name='Score'
        )
        sns.boxplot(data=subjects_data, x='Subject', y='Score', ax=axes[0, 1], palette='Set2')
        axes[0, 1].set_title('Score Distribution by Subject', fontweight='bold')
        axes[0, 1].set_xticklabels(['Math', 'Literature', 'English'])
        
        # 3. Violin plot for subjects
        sns.violinplot(data=subjects_data, x='Subject', y='Score', ax=axes[1, 0], palette='muted')
        axes[1, 0].set_title('Score Density by Subject', fontweight='bold')
        axes[1, 0].set_xticklabels(['Math', 'Literature', 'English'])
        
        # 4. Average score by subject (Bar plot)
        avg_scores = df[['math_score', 'literature_score', 'english_score']].mean()
        sns.barplot(x=['Math', 'Literature', 'English'], y=avg_scores.values, 
                   ax=axes[1, 1], palette='viridis')
        axes[1, 1].set_title('Average Scores by Subject', fontweight='bold')
        axes[1, 1].set_ylabel('Average Score')
        axes[1, 1].set_ylim(0, 10)
        
        # Add value labels on bars
        for i, v in enumerate(avg_scores.values):
            axes[1, 1].text(i, v + 0.1, f'{v:.2f}', ha='center', fontweight='bold')
        
        plt.tight_layout()
        
        return {
            "chart_type": "score_distribution",
            "image": self._fig_to_base64(fig),
            "format": "png",
            "encoding": "base64",
            "statistics": {
                "total_students": len(df),
                "average_scores": {
                    "math": float(df['math_score'].mean()),
                    "literature": float(df['literature_score'].mean()),
                    "english": float(df['english_score'].mean()),
                    "overall": float(df['average_score'].mean())
                }
            }
        }
    
    def generate_correlation_heatmap(self, db: Session) -> Dict[str, Any]:
        """Generate correlation heatmap between subjects"""
        df = self.create_students_dataframe(db)
        
        if df.empty:
            return {"error": "No data available"}
        
        # Calculate correlation matrix
        score_columns = ['math_score', 'literature_score', 'english_score']
        correlation = df[score_columns].corr()
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(correlation, annot=True, fmt='.3f', cmap='coolwarm', 
                   center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8},
                   xticklabels=['Math', 'Literature', 'English'],
                   yticklabels=['Math', 'Literature', 'English'],
                   ax=ax)
        ax.set_title('🔥 Score Correlation Heatmap', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        return {
            "chart_type": "correlation_heatmap",
            "image": self._fig_to_base64(fig),
            "format": "png",
            "encoding": "base64",
            "correlation_matrix": correlation.to_dict()
        }
    
    def generate_hometown_analysis(self, db: Session) -> Dict[str, Any]:
        """Generate hometown-based analysis plots"""
        df = self.create_students_dataframe(db)
        
        if df.empty:
            return {"error": "No data available"}
        
        # Create figure with subplots
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle('🌍 Hometown Analysis', fontsize=16, fontweight='bold')
        
        # 1. Student count by hometown
        hometown_counts = df['hometown'].value_counts().head(10)
        sns.barplot(x=hometown_counts.values, y=hometown_counts.index, 
                   ax=axes[0], palette='rocket')
        axes[0].set_title('Top 10 Hometowns by Student Count', fontweight='bold')
        axes[0].set_xlabel('Number of Students')
        axes[0].set_ylabel('Hometown')
        
        # 2. Average score by hometown (top 10)
        hometown_avg = df.groupby('hometown')['average_score'].mean().sort_values(ascending=False).head(10)
        sns.barplot(x=hometown_avg.values, y=hometown_avg.index, 
                   ax=axes[1], palette='flare')
        axes[1].set_title('Top 10 Hometowns by Average Score', fontweight='bold')
        axes[1].set_xlabel('Average Score')
        axes[1].set_ylabel('Hometown')
        
        plt.tight_layout()
        
        return {
            "chart_type": "hometown_analysis",
            "image": self._fig_to_base64(fig),
            "format": "png",
            "encoding": "base64",
            "statistics": {
                "total_hometowns": df['hometown'].nunique(),
                "most_common_hometown": df['hometown'].mode()[0] if not df['hometown'].mode().empty else "N/A",
                "top_performing_hometown": hometown_avg.index[0] if not hometown_avg.empty else "N/A"
            }
        }
    
    def generate_age_performance_plot(self, db: Session) -> Dict[str, Any]:
        """Generate age vs performance analysis"""
        df = self.create_students_dataframe(db)
        
        if df.empty:
            return {"error": "No data available"}
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('📈 Age vs Performance Analysis', fontsize=16, fontweight='bold')
        
        # 1. Scatter plot: Age vs Average Score
        sns.scatterplot(data=df, x='age', y='average_score', 
                       hue='average_score', size='average_score',
                       palette='viridis', ax=axes[0, 0], legend=False)
        axes[0, 0].set_title('Age vs Average Score', fontweight='bold')
        axes[0, 0].set_xlabel('Age')
        axes[0, 0].set_ylabel('Average Score')
        
        # Add regression line
        sns.regplot(data=df, x='age', y='average_score', 
                   scatter=False, color='red', ax=axes[0, 0])
        
        # 2. Box plot: Score distribution by age
        sns.boxplot(data=df, x='age', y='average_score', 
                   palette='Set3', ax=axes[0, 1])
        axes[0, 1].set_title('Score Distribution by Age', fontweight='bold')
        axes[0, 1].set_xlabel('Age')
        axes[0, 1].set_ylabel('Average Score')
        
        # 3. Student count by age
        age_counts = df['age'].value_counts().sort_index()
        sns.barplot(x=age_counts.index, y=age_counts.values, 
                   palette='Blues_d', ax=axes[1, 0])
        axes[1, 0].set_title('Student Count by Age', fontweight='bold')
        axes[1, 0].set_xlabel('Age')
        axes[1, 0].set_ylabel('Number of Students')
        
        # 4. Average score by age
        age_avg = df.groupby('age')['average_score'].mean()
        sns.lineplot(x=age_avg.index, y=age_avg.values, 
                    marker='o', markersize=8, linewidth=2, 
                    color='green', ax=axes[1, 1])
        axes[1, 1].set_title('Average Score Trend by Age', fontweight='bold')
        axes[1, 1].set_xlabel('Age')
        axes[1, 1].set_ylabel('Average Score')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        return {
            "chart_type": "age_performance",
            "image": self._fig_to_base64(fig),
            "format": "png",
            "encoding": "base64",
            "statistics": {
                "age_range": {
                    "min": int(df['age'].min()),
                    "max": int(df['age'].max()),
                    "mean": float(df['age'].mean())
                },
                "correlation_age_score": float(df[['age', 'average_score']].corr().iloc[0, 1])
            }
        }
    
    def generate_performance_categories(self, db: Session) -> Dict[str, Any]:
        """Generate performance category analysis"""
        df = self.create_students_dataframe(db)
        
        if df.empty:
            return {"error": "No data available"}
        
        # Create performance categories
        def categorize_performance(score):
            if score >= 8.5:
                return 'Excellent'
            elif score >= 7.0:
                return 'Good'
            elif score >= 5.5:
                return 'Average'
            else:
                return 'Below Average'
        
        df['performance_category'] = df['average_score'].apply(categorize_performance)
        
        # Create figure
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('🎯 Performance Category Analysis', fontsize=16, fontweight='bold')
        
        # 1. Pie chart of performance categories
        category_counts = df['performance_category'].value_counts()
        colors = sns.color_palette('pastel')[0:len(category_counts)]
        axes[0].pie(category_counts.values, labels=category_counts.index, 
                   autopct='%1.1f%%', startangle=90, colors=colors)
        axes[0].set_title('Performance Category Distribution', fontweight='bold')
        
        # 2. Count plot
        sns.countplot(data=df, x='performance_category', 
                     order=['Excellent', 'Good', 'Average', 'Below Average'],
                     palette='Set2', ax=axes[1])
        axes[1].set_title('Student Count by Performance Category', fontweight='bold')
        axes[1].set_xlabel('Performance Category')
        axes[1].set_ylabel('Number of Students')
        axes[1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        return {
            "chart_type": "performance_categories",
            "image": self._fig_to_base64(fig),
            "format": "png",
            "encoding": "base64",
            "category_distribution": category_counts.to_dict()
        }
    
    def generate_comprehensive_report(self, db: Session) -> Dict[str, Any]:
        """Generate comprehensive visualization report"""
        return {
            "score_distribution": self.generate_score_distribution_plot(db),
            "correlation_analysis": self.generate_correlation_heatmap(db),
            "hometown_analysis": self.generate_hometown_analysis(db),
            "age_performance": self.generate_age_performance_plot(db),
            "performance_categories": self.generate_performance_categories(db)
        }


# Create singleton instance
visualization_service = VisualizationService()
