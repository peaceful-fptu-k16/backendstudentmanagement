# 🎨 Seaborn Visualization Integration

## 📊 Overview
This Student Management System now includes **advanced data visualization** using **Seaborn** and **Matplotlib** for creating beautiful, publication-quality statistical graphics.

## 🔧 Installation

### Install Required Packages
```bash
pip install -r requirements.txt
```

The following packages are included:
- `seaborn==0.13.0` - Statistical data visualization
- `matplotlib==3.8.2` - Plotting backend
- `pandas==2.1.4` - Data manipulation

## 🚀 Features

### Available Visualizations

#### 1. **Score Distribution Analysis**
- Histogram with KDE (Kernel Density Estimation)
- Box plots for each subject
- Violin plots showing score density
- Bar chart of average scores by subject

**Endpoint:** `GET /api/v1/visualizations/score-distribution`

#### 2. **Correlation Heatmap**
- Shows correlation between Math, Physics, and Chemistry scores
- Color-coded matrix (red = positive, blue = negative correlation)
- Helpful for understanding subject relationships

**Endpoint:** `GET /api/v1/visualizations/correlation-heatmap`

#### 3. **Hometown Analysis**
- Top 10 hometowns by student count
- Top 10 hometowns by average score
- Identifies regional performance patterns

**Endpoint:** `GET /api/v1/visualizations/hometown-analysis`

#### 4. **Age vs Performance**
- Scatter plot with regression line
- Box plots by age group
- Student count distribution by age
- Average score trends by age

**Endpoint:** `GET /api/v1/visualizations/age-performance`

#### 5. **Performance Categories**
- Pie chart of performance distribution
- Bar chart showing counts per category
- Categories: Excellent (≥8.5), Good (≥7), Average (≥5.5), Below Average (<5.5)

**Endpoint:** `GET /api/v1/visualizations/performance-categories`

#### 6. **Comprehensive Report**
- All visualizations in one response
- Complete statistical overview

**Endpoint:** `GET /api/v1/visualizations/comprehensive-report`

## 📖 Usage

### 1. Start the Server
```bash
python scripts/run.py
```

### 2. Access Visualizations

#### Via Browser
Navigate to: `http://127.0.0.1:8001/docs`

Look for the **visualizations** section in the Swagger UI.

#### Via cURL
```bash
# Get score distribution
curl http://127.0.0.1:8001/api/v1/visualizations/score-distribution

# Get correlation heatmap
curl http://127.0.0.1:8001/api/v1/visualizations/correlation-heatmap

# Get comprehensive report
curl http://127.0.0.1:8001/api/v1/visualizations/comprehensive-report
```

#### Via Python
```python
import requests
import base64

# Get visualization
response = requests.get('http://127.0.0.1:8001/api/v1/visualizations/score-distribution')
data = response.json()

# Save image
image_data = base64.b64decode(data['image'])
with open('chart.png', 'wb') as f:
    f.write(image_data)
```

### 3. Run Test Script
```bash
python test_seaborn_visualizations.py
```

This will:
- Test all visualization endpoints
- Save all charts as PNG files in `visualization_outputs/` folder
- Display statistics and test results

## 🎨 Seaborn Styling

The visualizations use the following Seaborn configuration:

```python
# Theme
sns.set_theme(style="whitegrid", palette="pastel")

# Context
sns.set_context("notebook", font_scale=1.2)

# Available Styles
- whitegrid (current)
- darkgrid
- white
- dark
- ticks

# Available Palettes
- pastel (current)
- deep
- muted
- bright
- dark
- colorblind
```

## 📊 Response Format

All visualization endpoints return JSON with:

```json
{
  "chart_type": "score_distribution",
  "image": "base64_encoded_png_string",
  "format": "png",
  "encoding": "base64",
  "statistics": {
    "total_students": 150,
    "average_scores": {
      "math": 7.5,
      "physics": 7.2,
      "chemistry": 7.8
    }
  }
}
```

## 🛠️ Customization

### Modify Visualization Service

Edit `app/services/visualization_service.py` to customize:

1. **Change Color Palette**
```python
sns.set_theme(style="darkgrid", palette="deep")
```

2. **Adjust Figure Size**
```python
fig, axes = plt.subplots(figsize=(20, 15))  # Larger figures
```

3. **Change DPI (Resolution)**
```python
fig.savefig(buffer, format='png', dpi=600, bbox_inches='tight')  # Higher resolution
```

4. **Add New Visualizations**
```python
def generate_custom_chart(self, db: Session) -> Dict[str, Any]:
    df = self.create_students_dataframe(db)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.your_plot_type(data=df, ...)
    
    return {
        "chart_type": "custom",
        "image": self._fig_to_base64(fig),
        ...
    }
```

## 📈 Examples

### Example 1: Score Distribution
Shows how scores are distributed across all subjects with multiple visualization types.

![Score Distribution](docs/examples/score_distribution.png)

### Example 2: Correlation Heatmap
Visualizes the relationship between subject scores.

![Correlation Heatmap](docs/examples/correlation_heatmap.png)

### Example 3: Performance Categories
Displays student distribution across performance levels.

![Performance Categories](docs/examples/performance_categories.png)

## 🐛 Troubleshooting

### Issue: "ImportError: No module named seaborn"
**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "RuntimeError: Failed to start Agg"
**Solution:** Matplotlib backend is already configured to use 'Agg' (non-interactive)

### Issue: Charts not displaying
**Solution:** The charts are returned as base64 strings. Decode them:
```python
import base64
image_bytes = base64.b64decode(base64_string)
```

### Issue: Memory issues with large datasets
**Solution:** Add pagination or sampling:
```python
df = df.sample(n=1000)  # Sample 1000 students
```

## 📚 Additional Resources

- [Seaborn Documentation](https://seaborn.pydata.org/)
- [Matplotlib Gallery](https://matplotlib.org/stable/gallery/)
- [Pandas Visualization](https://pandas.pydata.org/docs/user_guide/visualization.html)

## 🎯 Best Practices

1. **Cache Visualizations**: Consider caching generated charts for frequently accessed data
2. **Async Processing**: For large datasets, use background tasks
3. **Image Optimization**: Compress PNG files if needed
4. **Error Handling**: Always check for empty dataframes
5. **Memory Management**: Close figures with `plt.close()` after saving

## 📝 API Documentation

Full API documentation available at:
- Swagger UI: `http://127.0.0.1:8001/docs`
- ReDoc: `http://127.0.0.1:8001/redoc`

## 🤝 Contributing

To add new visualizations:
1. Create method in `VisualizationService`
2. Add endpoint in `visualizations.py`
3. Update this README
4. Add tests to `test_seaborn_visualizations.py`

## 📄 License

See LICENSE file for details.
