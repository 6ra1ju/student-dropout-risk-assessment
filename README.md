# Student Dropout Risk Assessment System

Hệ thống đánh giá rủi ro bỏ học của sinh viên với giao diện web và API RESTful.

## Tính năng chính

- **📊 Dashboard** - Thống kê tổng quan với biểu đồ
- **👥 Quản lý sinh viên** - CRUD sinh viên với sort/filter
- **⚠️ Đánh giá rủi ro** - Thuật toán tính toán rủi ro bỏ học
- **⚙️ Cấu hình động** - Điều chỉnh ngưỡng rủi ro và cài đặt hệ thống
- **📈 Biểu đồ** - Visualize dữ liệu điểm danh và rủi ro
- **🔍 Tìm kiếm & Lọc** - Sort/filter theo nhiều tiêu chí

## Cài đặt & Chạy

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 2. Chạy ứng dụng
```bash
python app.py
```

### 3. Truy cập
- **Web Interface:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **API Base:** http://localhost:8000/api

## 📁 Cấu trúc dự án

```
ex1/
├── app.py                 # Entry point
├── main.py               # CLI tool
├── requirements.txt      # Dependencies
├── README.md            # Documentation
├── .gitignore           # Git ignore rules
├── src/                 # Source code
│   ├── models/          # Data models
│   ├── services/        # Business logic
│   ├── api/            # REST API routes
│   ├── web/            # Web interface
│   ├── database/       # Database setup
│   ├── risk_assessment/ # Risk calculation
│   └── utils/          # Utilities
├── templates/           # HTML templates
├── database/           # SQLite database
└── data/              # Sample data
```

## API Endpoints

### Students
- `GET /api/students/` - Danh sách sinh viên (với sort/filter)
- `POST /api/students/` - Tạo sinh viên mới
- `GET /api/students/{id}` - Chi tiết sinh viên
- `POST /api/students/{id}/predict-risk` - Đánh giá rủi ro

### Risk Assessment
- `GET /api/risk/high-risk-students` - Sinh viên rủi ro cao
- `GET /api/risk/medium-risk-students` - Sinh viên rủi ro trung bình
- `GET /api/risk/evaluations/{student_id}` - Lịch sử đánh giá

### Configuration
- `GET /api/config` - Lấy cấu hình
- `PUT /api/config` - Cập nhật cấu hình
- `POST /api/config/reset` - Reset về mặc định

### Dashboard
- `GET /api/dashboard/stats` - Thống kê dashboard

## Query Parameters

### Sort & Filter
```bash
# Filter theo risk level
GET /api/students/?risk_level=HIGH

# Sort theo tên sinh viên
GET /api/students/?sort_by=student_name&sort_order=asc

# Phân trang
GET /api/students/?page=1&limit=20
```

## Thuật toán đánh giá rủi ro

Hệ thống tính toán rủi ro dựa trên 3 yếu tố:

1. **Điểm danh** (0-1 điểm)
   - Vắng mặt nhiều → Rủi ro cao

2. **Bài tập** (0-1 điểm)  
   - Không nộp bài → Rủi ro cao

3. **Liên lạc** (0-1 điểm)
   - Liên lạc thất bại → Rủi ro cao

**Tổng điểm:** 0-3 điểm → Phân loại: LOW/MEDIUM/HIGH

## 🛠️ Công nghệ sử dụng

- **Backend:** FastAPI, SQLAlchemy, Pydantic
- **Database:** SQLite
- **Frontend:** Bootstrap, Chart.js, Jinja2
- **CLI:** Typer, Rich
