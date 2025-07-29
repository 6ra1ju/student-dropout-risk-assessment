"""
Templates Management Module
Quản lý templates cho web interface

Cấu trúc:
- src/web/templates.py: Logic tạo templates (file Python)
- templates/: Thư mục chứa HTML templates (được tạo tự động)
"""

import os
from pathlib import Path
from fastapi import Request
from fastapi.templating import Jinja2Templates

# Tạo thư mục templates nếu chưa tồn tại
templates_dir = Path("templates")
templates_dir.mkdir(exist_ok=True)

# Jinja2Templates để render HTML templates
templates = Jinja2Templates(directory="templates")


def create_base_template():
    """Tạo template cơ bản"""
    return """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Hệ thống đánh giá rủi ro bỏ học{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .risk-low { color: #28a745; }
        .risk-medium { color: #ffc107; }
        .risk-high { color: #dc3545; }
        .sidebar { min-height: 100vh; background-color: #f8f9fa; }
        .main-content { padding: 20px; }
        .risk-card { border-left: 4px solid; }
        .risk-card.high { border-left-color: #dc3545; }
        .risk-card.medium { border-left-color: #ffc107; }
        .risk-card.low { border-left-color: #28a745; }
        .loading { display: none; }
        .alert-auto-hide { animation: fadeOut 5s forwards; }
        @keyframes fadeOut { to { opacity: 0; } }
        .config-panel { background: #f8f9fa; border-radius: 8px; padding: 20px; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <nav class="col-md-3 col-lg-2 d-md-block sidebar collapse">
                <div class="position-sticky pt-3">
                    <h6 class="sidebar-heading d-flex justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
                        <span>Hệ thống</span>
                    </h6>
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link" href="/">
                                <i class="fas fa-home"></i> Dashboard
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/students">
                                <i class="fas fa-users"></i> Danh sách sinh viên
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/risk/high">
                                <i class="fas fa-exclamation-triangle"></i> Rủi ro cao
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/risk/medium">
                                <i class="fas fa-exclamation-circle"></i> Rủi ro trung bình
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/config">
                                <i class="fas fa-cog"></i> Cấu hình
                            </a>
                        </li>
                    </ul>
                </div>
            </nav>

            <!-- Main content -->
            <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 main-content">
                <!-- Loading indicator -->
                <div id="loading" class="loading text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Đang tải...</span>
                    </div>
                </div>
                
                <!-- Alert container -->
                <div id="alertContainer"></div>
                
                {% block content %}{% endblock %}
            </main>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <script>
    // Utility functions
    function showLoading() {
        document.getElementById('loading').style.display = 'block';
    }
    
    function hideLoading() {
        document.getElementById('loading').style.display = 'none';
    }
    
    function showAlert(message, type = 'info') {
        const alertContainer = document.getElementById('alertContainer');
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show alert-auto-hide`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        alertContainer.appendChild(alert);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 5000);
    }
    
    function makeRequest(url, options = {}) {
        showLoading();
        return fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        })
        .then(response => {
            hideLoading();
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            hideLoading();
            showAlert(`Lỗi: ${error.message}`, 'danger');
            throw error;
        });
    }
    </script>
    
    {% block scripts %}{% endblock %}
</body>
</html>"""


def create_dashboard_template():
    """Tạo template dashboard"""
    return """{% extends "base.html" %}

{% block title %}Dashboard - Hệ thống đánh giá rủi ro{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">
        <i class="fas fa-tachometer-alt"></i> Dashboard
    </h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <button onclick="refreshDashboard()" class="btn btn-sm btn-outline-secondary">
            <i class="fas fa-sync-alt"></i> Làm mới
        </button>
    </div>
</div>

<!-- Statistics Cards -->
<div class="row mb-4">
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <h3 class="text-primary" id="totalStudents">-</h3>
                <p class="card-text">Tổng sinh viên</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <h3 class="text-danger" id="highRiskCount">-</h3>
                <p class="card-text">Rủi ro cao</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <h3 class="text-warning" id="mediumRiskCount">-</h3>
                <p class="card-text">Rủi ro trung bình</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body">
                <h3 class="text-success" id="lowRiskCount">-</h3>
                <p class="card-text">Rủi ro thấp</p>
            </div>
        </div>
    </div>
</div>

<!-- Charts -->
<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-chart-pie"></i> Phân bố rủi ro</h5>
            </div>
            <div class="card-body">
                <canvas id="riskChart" width="400" height="200"></canvas>
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-chart-line"></i> Xu hướng rủi ro</h5>
            </div>
            <div class="card-body">
                <canvas id="trendChart" width="400" height="200"></canvas>
            </div>
        </div>
    </div>
</div>

<!-- Recent High Risk Students -->
<div class="row mt-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-exclamation-triangle"></i> Sinh viên rủi ro cao gần đây</h5>
            </div>
            <div class="card-body">
                <div id="recentHighRiskStudents">
                    <div class="text-center py-4">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Đang tải...</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
// Load dashboard data
function loadDashboardData() {
    // Load statistics
    makeRequest('/api/dashboard/stats')
        .then(data => {
            document.getElementById('totalStudents').textContent = data.total_students;
            document.getElementById('highRiskCount').textContent = data.high_risk_count;
            document.getElementById('mediumRiskCount').textContent = data.medium_risk_count;
            document.getElementById('lowRiskCount').textContent = data.low_risk_count;
            
            // Create risk distribution chart
            createRiskChart(data.risk_distribution);
        })
        .catch(error => {
            console.error('Error loading dashboard stats:', error);
        });
    
    // Load recent high risk students
    makeRequest('/api/risk/high-risk-students')
        .then(data => {
            displayRecentHighRiskStudents(data.slice(0, 5));
        })
        .catch(error => {
            console.error('Error loading high risk students:', error);
        });
}

function createRiskChart(data) {
    const ctx = document.getElementById('riskChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Thấp', 'Trung bình', 'Cao'],
            datasets: [{
                data: [data.low, data.medium, data.high],
                backgroundColor: [
                    'rgba(40, 167, 69, 0.8)',
                    'rgba(255, 193, 7, 0.8)',
                    'rgba(220, 53, 69, 0.8)'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function displayRecentHighRiskStudents(students) {
    const container = document.getElementById('recentHighRiskStudents');
    
    if (students.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">Không có sinh viên rủi ro cao</p>';
        return;
    }
    
    const html = students.map(student => `
        <div class="d-flex justify-content-between align-items-center mb-2">
            <div>
                <strong>${student.student_name}</strong> (${student.student_id})
                <br><small class="text-muted">Điểm: ${student.score}/5</small>
            </div>
            <a href="/students/${student.student_id}" class="btn btn-sm btn-outline-primary">
                <i class="fas fa-eye"></i> Xem
            </a>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

function refreshDashboard() {
    loadDashboardData();
    showAlert('Dashboard đã được làm mới', 'success');
}

// Load data when page loads
document.addEventListener('DOMContentLoaded', loadDashboardData);
</script>
{% endblock %}"""


def create_config_template():
    """Tạo template cấu hình"""
    return """{% extends "base.html" %}

{% block title %}Cấu hình hệ thống{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">
        <i class="fas fa-cog"></i> Cấu hình hệ thống
    </h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <button onclick="resetConfig()" class="btn btn-sm btn-outline-warning">
            <i class="fas fa-undo"></i> Reset mặc định
        </button>
    </div>
</div>

<div class="row">
    <div class="col-md-8">
        <div class="config-panel">
            <form id="configForm">
                <h5 class="mb-3">Ngưỡng rủi ro</h5>
                <div class="row mb-3">
                    <div class="col-md-4">
                        <label for="lowThreshold" class="form-label">Ngưỡng rủi ro thấp</label>
                        <input type="number" class="form-control" id="lowThreshold" min="0" max="5" required>
                    </div>
                    <div class="col-md-4">
                        <label for="mediumThreshold" class="form-label">Ngưỡng rủi ro trung bình</label>
                        <input type="number" class="form-control" id="mediumThreshold" min="0" max="5" required>
                    </div>
                    <div class="col-md-4">
                        <label for="highThreshold" class="form-label">Ngưỡng rủi ro cao</label>
                        <input type="number" class="form-control" id="highThreshold" min="0" max="5" required>
                    </div>
                </div>
                
                <h5 class="mb-3">Cấu hình giao diện</h5>
                <div class="row mb-3">
                    <div class="col-md-6">
                        <label for="refreshInterval" class="form-label">Thời gian tự động refresh (giây)</label>
                        <input type="number" class="form-control" id="refreshInterval" min="10" max="300" required>
                    </div>
                    <div class="col-md-6">
                        <label for="maxStudentsPerPage" class="form-label">Số sinh viên tối đa mỗi trang</label>
                        <input type="number" class="form-control" id="maxStudentsPerPage" min="5" max="100" required>
                    </div>
                </div>
                
                <div class="mb-3">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="enableNotifications">
                        <label class="form-check-label" for="enableNotifications">
                            Bật thông báo
                        </label>
                    </div>
                </div>
                
                <button type="submit" class="btn btn-primary">
                    <i class="fas fa-save"></i> Lưu cấu hình
                </button>
            </form>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-info-circle"></i> Thông tin</h5>
            </div>
            <div class="card-body">
                <p><strong>Ngưỡng rủi ro:</strong> Xác định điểm số để phân loại mức rủi ro</p>
                <p><strong>Tự động refresh:</strong> Thời gian tự động cập nhật dữ liệu</p>
                <p><strong>Số sinh viên mỗi trang:</strong> Giới hạn hiển thị để tối ưu hiệu suất</p>
                <p><strong>Thông báo:</strong> Hiển thị thông báo khi có thay đổi</p>
            </div>
        </div>
    </div>
</div>

<script>
// Load current config
function loadConfig() {
    makeRequest('/api/config')
        .then(data => {
            const config = data.config;
            
            // Set form values
            document.getElementById('lowThreshold').value = config.risk_thresholds.low_threshold;
            document.getElementById('mediumThreshold').value = config.risk_thresholds.medium_threshold;
            document.getElementById('highThreshold').value = config.risk_thresholds.high_threshold;
            document.getElementById('refreshInterval').value = config.auto_refresh_interval;
            document.getElementById('maxStudentsPerPage').value = config.max_students_per_page;
            document.getElementById('enableNotifications').checked = config.enable_notifications;
        })
        .catch(error => {
            console.error('Error loading config:', error);
            showAlert('Không thể tải cấu hình', 'danger');
        });
}

// Save config
document.getElementById('configForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const configData = {
        risk_thresholds: {
            low_threshold: parseInt(document.getElementById('lowThreshold').value),
            medium_threshold: parseInt(document.getElementById('mediumThreshold').value),
            high_threshold: parseInt(document.getElementById('highThreshold').value)
        },
        auto_refresh_interval: parseInt(document.getElementById('refreshInterval').value),
        max_students_per_page: parseInt(document.getElementById('maxStudentsPerPage').value),
        enable_notifications: document.getElementById('enableNotifications').checked
    };
    
    makeRequest('/api/config', {
        method: 'PUT',
        body: JSON.stringify(configData)
    })
    .then(data => {
        showAlert('Cấu hình đã được lưu thành công', 'success');
    })
    .catch(error => {
        console.error('Error saving config:', error);
        showAlert('Không thể lưu cấu hình', 'danger');
    });
});

// Reset config
function resetConfig() {
    if (confirm('Bạn có chắc muốn reset về cấu hình mặc định?')) {
        makeRequest('/api/config/reset', {
            method: 'POST'
        })
        .then(data => {
            showAlert('Cấu hình đã được reset', 'success');
            loadConfig(); // Reload form
        })
        .catch(error => {
            console.error('Error resetting config:', error);
            showAlert('Không thể reset cấu hình', 'danger');
        });
    }
}

// Load config when page loads
document.addEventListener('DOMContentLoaded', loadConfig);
</script>
{% endblock %}"""


def create_student_list_template():
    """Tạo template danh sách sinh viên với sort và filter"""
    return """{% extends "base.html" %}

{% block title %}Danh sách sinh viên{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">
        <i class="fas fa-users"></i> Danh sách sinh viên
    </h1>
                <div class="btn-toolbar mb-2 mb-md-0">
                <div class="btn-group me-2">
                    <button onclick="refreshStudents()" class="btn btn-sm btn-outline-secondary">
                        <i class="fas fa-sync-alt"></i> Làm mới
                    </button>
                    <button onclick="exportToCSV()" class="btn btn-sm btn-success">
                        <i class="fas fa-download"></i> Export CSV
                    </button>
                </div>
            </div>
</div>

<!-- Filter and Sort Controls -->
<div class="row mb-4">
    <div class="col-md-12">
        <div class="card">
            <div class="card-body">
                <div class="row">
                    <div class="col-md-3">
                        <label for="riskFilter" class="form-label">Lọc theo rủi ro</label>
                        <select class="form-select" id="riskFilter" onchange="applyFilters()">
                            <option value="">Tất cả</option>
                            <option value="HIGH">Rủi ro cao</option>
                            <option value="MEDIUM">Rủi ro trung bình</option>
                            <option value="LOW">Rủi ro thấp</option>
                        </select>
                    </div>
                    <div class="col-md-3">
                        <label for="sortBy" class="form-label">Sắp xếp theo</label>
                        <select class="form-select" id="sortBy" onchange="applyFilters()">
                            <option value="student_id">Mã sinh viên</option>
                            <option value="student_name">Tên sinh viên</option>
                            <option value="risk_level">Mức rủi ro</option>
                        </select>
                    </div>
                    <div class="col-md-2">
                        <label for="sortOrder" class="form-label">Thứ tự</label>
                        <select class="form-select" id="sortOrder" onchange="applyFilters()">
                            <option value="asc">Tăng dần</option>
                            <option value="desc">Giảm dần</option>
                        </select>
                    </div>
                    <div class="col-md-2">
                        <label for="pageSize" class="form-label">Số lượng</label>
                        <select class="form-select" id="pageSize" onchange="applyFilters()">
                            <option value="10">10</option>
                            <option value="20" selected>20</option>
                            <option value="50">50</option>
                        </select>
                    </div>
                    <div class="col-md-2">
                        <label class="form-label">&nbsp;</label>
                        <button onclick="clearFilters()" class="btn btn-outline-secondary w-100">
                            <i class="fas fa-times"></i> Xóa bộ lọc
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Students List -->
<div id="studentsContainer">
    <div class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Đang tải...</span>
        </div>
    </div>
</div>

<!-- Pagination -->
<div class="row mt-4">
    <div class="col-md-12">
        <nav aria-label="Student pagination">
            <ul class="pagination justify-content-center" id="pagination">
            </ul>
        </nav>
    </div>
</div>

<script>
let currentPage = 1;
let totalPages = 1;

// Load students with filters
function loadStudents(page = 1) {
    currentPage = page;
    
    const riskFilter = document.getElementById('riskFilter').value;
    const sortBy = document.getElementById('sortBy').value;
    const sortOrder = document.getElementById('sortOrder').value;
    const pageSize = document.getElementById('pageSize').value;
    
    const params = new URLSearchParams({
        page: page,
        limit: pageSize,
        sort_by: sortBy,
        sort_order: sortOrder
    });
    
    if (riskFilter) {
        params.append('risk_level', riskFilter);
    }
    
    makeRequest(`/api/students/?${params.toString()}`)
        .then(students => {
            displayStudents(students);
            updatePagination();
        })
        .catch(error => {
            console.error('Error loading students:', error);
            showAlert('Không thể tải danh sách sinh viên', 'danger');
        });
}

function displayStudents(students) {
    const container = document.getElementById('studentsContainer');
    
    if (students.length === 0) {
        container.innerHTML = `
            <div class="alert alert-info text-center">
                <i class="fas fa-info-circle"></i> Không tìm thấy sinh viên nào phù hợp với bộ lọc.
            </div>
        `;
        return;
    }
    
    const html = `
        <div class="row">
            ${students.map(student => `
                <div class="col-md-6 col-lg-4 mb-4">
                    <div class="card h-100">
                        <div class="card-body">
                            <h5 class="card-title">
                                <i class="fas fa-user-graduate"></i> ${student.student_name}
                            </h5>
                            <p class="card-text">
                                <strong>Mã SV:</strong> ${student.student_id}<br>
                                <strong>Ngày tạo:</strong> ${new Date(student.created_at).toLocaleDateString('vi-VN')}
                            </p>
                            <div class="d-flex justify-content-between align-items-center">
                                <a href="/students/${student.student_id}" class="btn btn-primary btn-sm">
                                    <i class="fas fa-eye"></i> Xem chi tiết
                                </a>
                                <button onclick="predictRisk('${student.student_id}')" class="btn btn-outline-success btn-sm">
                                    <i class="fas fa-calculator"></i> Đánh giá rủi ro
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
    
    container.innerHTML = html;
}

function updatePagination() {
    const pagination = document.getElementById('pagination');
    const pageSize = parseInt(document.getElementById('pageSize').value);
    
    // Calculate total pages (simplified - in real app you'd get this from API)
    totalPages = Math.ceil(20 / pageSize); // Assuming 20 students total for demo
    
    let paginationHtml = '';
    
    // Previous button
    paginationHtml += `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="loadStudents(${currentPage - 1})">Trước</a>
        </li>
    `;
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        paginationHtml += `
            <li class="page-item ${currentPage === i ? 'active' : ''}">
                <a class="page-link" href="#" onclick="loadStudents(${i})">${i}</a>
            </li>
        `;
    }
    
    // Next button
    paginationHtml += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="loadStudents(${currentPage + 1})">Sau</a>
        </li>
    `;
    
    pagination.innerHTML = paginationHtml;
}

function applyFilters() {
    loadStudents(1); // Reset to first page
}

function clearFilters() {
    document.getElementById('riskFilter').value = '';
    document.getElementById('sortBy').value = 'student_id';
    document.getElementById('sortOrder').value = 'asc';
    document.getElementById('pageSize').value = '20';
    loadStudents(1);
}

function refreshStudents() {
    loadStudents(currentPage);
    showAlert('Danh sách sinh viên đã được làm mới', 'success');
}

function predictRisk(studentId) {
    makeRequest(`/api/students/${studentId}/predict-risk`, {
        method: 'POST'
    })
    .then(data => {
        showAlert(`Đánh giá rủi ro hoàn thành! Mức rủi ro: ${data.risk_level}`, 'success');
        refreshStudents(); // Reload to show updated risk
    })
    .catch(error => {
        console.error('Error predicting risk:', error);
        showAlert('Không thể đánh giá rủi ro', 'danger');
    });
}

function exportToCSV() {
    // Tạo link download
    const link = document.createElement('a');
    link.href = '/api/export/csv';
    link.download = `results_${new Date().toISOString().slice(0,10)}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showAlert('Đang tải file CSV...', 'info');
}

// Load students when page loads
document.addEventListener('DOMContentLoaded', () => {
    loadStudents(1);
});
</script>
{% endblock %}"""


def create_student_detail_template():
    """Tạo template chi tiết sinh viên"""
    return """{% extends "base.html" %}

{% block title %}{{ student.student_name }} - Chi tiết{% endblock %}

{% block content %}
<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2">
        <i class="fas fa-user-graduate"></i> {{ student.student_name }}
    </h1>
    <div class="btn-toolbar mb-2 mb-md-0">
        <div class="btn-group me-2">
            <a href="/students" class="btn btn-sm btn-outline-secondary">
                <i class="fas fa-arrow-left"></i> Quay lại
            </a>
            <button onclick="predictRisk()" class="btn btn-sm btn-primary">
                <i class="fas fa-calculator"></i> Đánh giá rủi ro
            </button>
        </div>
    </div>
</div>

<div class="row">
    <!-- Thông tin cơ bản -->
    <div class="col-md-4">
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-info-circle"></i> Thông tin cơ bản</h5>
            </div>
            <div class="card-body">
                <p><strong>Mã sinh viên:</strong> {{ student.student_id }}</p>
                <p><strong>Tên:</strong> {{ student.student_name }}</p>
                <p><strong>Tỷ lệ điểm danh:</strong> {{ "%.1f"|format(attendance_rate) }}%</p>
                <p><strong>Tỷ lệ nộp bài:</strong> {{ "%.1f"|format(submission_rate) }}%</p>
                <p><strong>Liên lạc thất bại:</strong> {{ failed_contacts }} lần</p>
            </div>
        </div>

        <!-- Rủi ro hiện tại -->
        {% if latest_risk %}
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-exclamation-triangle"></i> Rủi ro hiện tại</h5>
            </div>
            <div class="card-body">
                <div class="risk-card {{ latest_risk.risk_level.lower() }}">
                    <h4 class="risk-{{ latest_risk.risk_level.lower() }}">
                        {{ latest_risk.risk_level }}
                    </h4>
                    <p><strong>Điểm số:</strong> {{ latest_risk.score }}/5</p>
                    <p><strong>Ngày đánh giá:</strong> {{ latest_risk.evaluated_at.strftime('%d/%m/%Y %H:%M') }}</p>
                </div>
            </div>
        </div>
        {% endif %}
    </div>

    <!-- Biểu đồ và thống kê -->
    <div class="col-md-8">
        <!-- Biểu đồ điểm danh -->
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-chart-line"></i> Biểu đồ điểm danh</h5>
            </div>
            <div class="card-body">
                <canvas id="attendanceChart" width="400" height="200"></canvas>
            </div>
        </div>

        <!-- Lịch sử đánh giá rủi ro -->
        {% if risk_evaluations %}
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-history"></i> Lịch sử đánh giá rủi ro</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Ngày</th>
                                <th>Điểm số</th>
                                <th>Mức rủi ro</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for evaluation in risk_evaluations %}
                            <tr>
                                <td>{{ evaluation.evaluated_at.strftime('%d/%m/%Y %H:%M') }}</td>
                                <td>{{ evaluation.score }}/5</td>
                                <td>
                                    <span class="risk-{{ evaluation.risk_level.lower() }}">
                                        {{ evaluation.risk_level }}
                                    </span>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}
    </div>
</div>

<script>
function predictRisk() {
    makeRequest('/api/students/{{ student.student_id }}/predict-risk', {
        method: 'POST'
    })
    .then(data => {
        showAlert('Đánh giá rủi ro hoàn thành! Mức rủi ro: ' + data.risk_level, 'success');
        location.reload();
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Có lỗi xảy ra khi đánh giá rủi ro', 'danger');
    });
}

// Biểu đồ điểm danh
const attendanceCtx = document.getElementById('attendanceChart').getContext('2d');
new Chart(attendanceCtx, {
    type: 'line',
    data: {
        labels: {{ attendance_dates | tojson }},
        datasets: [{
            label: 'Điểm danh',
            data: {{ attendance_data | tojson }},
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            tension: 0.1
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true,
                max: 1,
                ticks: {
                    stepSize: 1
                }
            }
        }
    }
});
</script>
{% endblock %}"""


def create_templates():
    """Tạo tất cả templates"""
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Tạo base template
    with open(templates_dir / "base.html", "w", encoding="utf-8") as f:
        f.write(create_base_template())
    
    # Tạo dashboard template
    with open(templates_dir / "dashboard.html", "w", encoding="utf-8") as f:
        f.write(create_dashboard_template())
    
    # Tạo student list template
    with open(templates_dir / "student_list.html", "w", encoding="utf-8") as f:
        f.write(create_student_list_template())
    
    # Tạo student detail template
    with open(templates_dir / "student_detail.html", "w", encoding="utf-8") as f:
        f.write(create_student_detail_template())
    
    # Tạo config template
    with open(templates_dir / "config.html", "w", encoding="utf-8") as f:
        f.write(create_config_template())
    
    print("✅ Web templates đã được tạo") 