# 🎨 Seaborn Quick Start Guide

## 🚀 Cài đặt nhanh

### Bước 1: Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### Bước 2: Khởi động server
```bash
python scripts/run.py
```

## 📊 Sử dụng Visualizations

### Option 1: Sử dụng Web Dashboard (Khuyến nghị)

1. Mở file `visualization_dashboard.html` trong trình duyệt
2. Click vào các nút để xem biểu đồ
3. Tất cả biểu đồ sẽ hiển thị trực tiếp trên trang

### Option 2: Sử dụng Swagger UI

1. Truy cập: http://127.0.0.1:8001/docs
2. Tìm section **visualizations** (màu xanh lá)
3. Click vào endpoint bạn muốn test
4. Click **Try it out** → **Execute**
5. Kết quả trả về base64 image string

### Option 3: Chạy Test Script

```bash
python test_seaborn_visualizations.py
```

Script này sẽ:
- ✅ Test tất cả endpoints
- 💾 Lưu tất cả biểu đồ vào folder `visualization_outputs/`
- 📊 Hiển thị statistics

## 📈 Các loại biểu đồ có sẵn

### 1. Score Distribution (Phân phối điểm)
```
GET /api/v1/visualizations/score-distribution
```
- Histogram với KDE
- Box plots cho từng môn
- Violin plots
- Bar chart điểm trung bình

### 2. Correlation Heatmap (Ma trận tương quan)
```
GET /api/v1/visualizations/correlation-heatmap
```
- Heatmap tương quan giữa các môn học
- Màu sắc: đỏ (tương quan dương), xanh (tương quan âm)

### 3. Hometown Analysis (Phân tích quê quán)
```
GET /api/v1/visualizations/hometown-analysis
```
- Top 10 quê quán có nhiều sinh viên nhất
- Top 10 quê quán có điểm TB cao nhất

### 4. Age Performance (Tuổi vs Thành tích)
```
GET /api/v1/visualizations/age-performance
```
- Scatter plot với regression line
- Box plots theo nhóm tuổi
- Phân phối sinh viên theo tuổi
- Xu hướng điểm theo tuổi

### 5. Performance Categories (Phân loại học lực)
```
GET /api/v1/visualizations/performance-categories
```
- Pie chart phân phối học lực
- Bar chart số lượng theo loại
- Categories:
  - Excellent: ≥ 8.5
  - Good: ≥ 7.0
  - Average: ≥ 5.5
  - Below Average: < 5.5

### 6. Comprehensive Report (Báo cáo tổng hợp)
```
GET /api/v1/visualizations/comprehensive-report
```
- Tất cả biểu đồ trong một request
- Phù hợp để tạo báo cáo đầy đủ

## 💡 Ví dụ sử dụng

### Python
```python
import requests
import base64

# Lấy biểu đồ phân phối điểm
response = requests.get('http://127.0.0.1:8001/api/v1/visualizations/score-distribution')
data = response.json()

# Lưu hình ảnh
image_bytes = base64.b64decode(data['image'])
with open('score_distribution.png', 'wb') as f:
    f.write(image_bytes)

# Xem statistics
print(data['statistics'])
```

### cURL
```bash
curl -X GET "http://127.0.0.1:8001/api/v1/visualizations/score-distribution"
```

### JavaScript (Trong HTML)
```javascript
async function loadChart() {
    const response = await fetch('http://127.0.0.1:8001/api/v1/visualizations/score-distribution');
    const data = await response.json();
    
    // Hiển thị hình ảnh
    const img = document.createElement('img');
    img.src = `data:image/png;base64,${data.image}`;
    document.body.appendChild(img);
}
```

## 🎨 Tùy chỉnh Style

### Thay đổi màu sắc
Mở `app/services/visualization_service.py` và sửa:

```python
# Thay đổi theme
sns.set_theme(style="darkgrid", palette="deep")

# Available palettes:
# - pastel (current)
# - deep
# - muted
# - bright
# - dark
# - colorblind
```

### Thay đổi kích thước
```python
fig, axes = plt.subplots(figsize=(20, 15))  # Lớn hơn
```

### Thay đổi độ phân giải
```python
fig.savefig(buffer, format='png', dpi=600)  # Cao hơn
```

## 🔧 Troubleshooting

### Lỗi: ModuleNotFoundError: No module named 'seaborn'
**Giải pháp:**
```bash
pip install seaborn matplotlib
```

### Lỗi: Connection refused
**Giải pháp:** Đảm bảo server đang chạy:
```bash
python scripts/run.py
```

### Lỗi: Empty dataframe
**Giải pháp:** Thêm dữ liệu sinh viên vào database trước

### Biểu đồ không hiển thị trong dashboard
**Giải pháp:** 
1. Kiểm tra CORS settings trong `app/main.py`
2. Kiểm tra console của browser (F12)
3. Đảm bảo server chạy ở port 8001

## 📁 File Structure

```
BackendStudentManagement/
├── app/
│   ├── api/
│   │   └── endpoints/
│   │       └── visualizations.py    # API endpoints
│   └── services/
│       └── visualization_service.py  # Seaborn logic
├── visualization_dashboard.html      # Web dashboard
├── test_seaborn_visualizations.py   # Test script
├── SEABORN_GUIDE.md                 # Hướng dẫn chi tiết
└── requirements.txt                  # Dependencies
```

## 📚 Tài liệu thêm

- [Seaborn Documentation](https://seaborn.pydata.org/)
- [Matplotlib Gallery](https://matplotlib.org/stable/gallery/)
- Chi tiết hơn: Xem `SEABORN_GUIDE.md`

## ✨ Features

✅ 6 loại visualization khác nhau
✅ Base64 encoding - dễ dàng integrate
✅ High resolution (300 DPI)
✅ Beautiful Seaborn styling
✅ Comprehensive statistics
✅ Web dashboard included
✅ Test script included
✅ Full API documentation

## 🎯 Next Steps

1. Khởi động server
2. Mở `visualization_dashboard.html`
3. Click "Load All Charts"
4. Enjoy! 🎉

## 🤝 Hỗ trợ

Nếu có vấn đề gì, hãy:
1. Kiểm tra lại các bước cài đặt
2. Xem logs trong terminal
3. Kiểm tra file `SEABORN_GUIDE.md` để biết thêm chi tiết
