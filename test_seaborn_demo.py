"""
Quick demo script to test Seaborn integration
Creates sample visualizations without needing the full API
"""
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Set seaborn style
sns.set_theme(style="whitegrid", palette="pastel")

def create_sample_data():
    """Create sample student data"""
    data = {
        'name': [f'Student {i}' for i in range(1, 51)],
        'age': [18, 19, 20, 21, 22] * 10,
        'math_score': [7.5, 8.0, 6.5, 9.0, 7.0] * 10,
        'literature_score': [7.0, 8.5, 6.0, 8.5, 7.5] * 10,
        'english_score': [8.0, 7.5, 6.5, 9.0, 8.0] * 10,
        'hometown': ['Hanoi', 'HCMC', 'Danang', 'Haiphong', 'Cantho'] * 10
    }
    df = pd.DataFrame(data)
    df['average_score'] = (df['math_score'] + df['literature_score'] + df['english_score']) / 3
    return df

def test_basic_seaborn():
    """Test basic Seaborn functionality"""
    print("Testing Seaborn Integration...")
    print("=" * 60)
    
    # Create sample data
    print("Creating sample data...")
    df = create_sample_data()
    print(f"   Created {len(df)} sample students")
    print(f"   Columns: {', '.join(df.columns)}")
    
    # Test 1: Simple histogram
    print("\nTest 1: Creating histogram...")
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(data=df, x='average_score', kde=True, ax=ax, color='skyblue')
        ax.set_title('Score Distribution')
        plt.savefig('test_histogram.png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        print("   SUCCESS: Histogram saved as 'test_histogram.png'")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 2: Box plot
    print("\nTest 2: Creating box plot...")
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        subjects_data = df[['math_score', 'literature_score', 'english_score']].melt(
            var_name='Subject', value_name='Score'
        )
        sns.boxplot(data=subjects_data, x='Subject', y='Score', ax=ax, palette='Set2')
        ax.set_title('Score Distribution by Subject')
        plt.savefig('test_boxplot.png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        print("   SUCCESS: Box plot saved as 'test_boxplot.png'")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 3: Correlation heatmap
    print("\nTest 3: Creating correlation heatmap...")
    try:
        fig, ax = plt.subplots(figsize=(8, 6))
        correlation = df[['math_score', 'literature_score', 'english_score']].corr()
        sns.heatmap(correlation, annot=True, fmt='.2f', cmap='coolwarm', 
                   square=True, ax=ax)
        ax.set_title('Score Correlation Heatmap')
        plt.savefig('test_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        print("   SUCCESS: Heatmap saved as 'test_heatmap.png'")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 4: Scatter plot
    print("\nTest 4: Creating scatter plot...")
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(data=df, x='age', y='average_score', 
                       hue='hometown', size='average_score',
                       palette='viridis', ax=ax)
        ax.set_title('Age vs Average Score')
        plt.savefig('test_scatter.png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        print("   SUCCESS: Scatter plot saved as 'test_scatter.png'")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 5: Multiple subplots
    print("\nTest 5: Creating dashboard with multiple plots...")
    try:
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Student Analytics Dashboard', fontsize=16, fontweight='bold')
        
        # Plot 1: Histogram
        sns.histplot(data=df, x='average_score', kde=True, ax=axes[0, 0], color='skyblue')
        axes[0, 0].set_title('Score Distribution')
        
        # Plot 2: Box plot
        subjects_data = df[['math_score', 'literature_score', 'english_score']].melt(
            var_name='Subject', value_name='Score'
        )
        sns.boxplot(data=subjects_data, x='Subject', y='Score', ax=axes[0, 1], palette='Set2')
        axes[0, 1].set_title('Scores by Subject')
        
        # Plot 3: Bar plot
        avg_by_hometown = df.groupby('hometown')['average_score'].mean().sort_values(ascending=False)
        sns.barplot(x=avg_by_hometown.values, y=avg_by_hometown.index, 
                   ax=axes[1, 0], palette='rocket')
        axes[1, 0].set_title('Average Score by Hometown')
        
        # Plot 4: Line plot
        age_avg = df.groupby('age')['average_score'].mean()
        sns.lineplot(x=age_avg.index, y=age_avg.values, 
                    marker='o', linewidth=2, ax=axes[1, 1])
        axes[1, 1].set_title('Average Score by Age')
        
        plt.tight_layout()
        plt.savefig('test_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        print("   SUCCESS: Dashboard saved as 'test_dashboard.png'")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUCCESS: Seaborn test completed!")
    print("Files created:")
    print("   - test_histogram.png")
    print("   - test_boxplot.png")
    print("   - test_heatmap.png")
    print("   - test_scatter.png")
    print("   - test_dashboard.png")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_basic_seaborn()
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
