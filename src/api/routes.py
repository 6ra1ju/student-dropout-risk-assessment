from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from src.database.database import get_db
from src.services.student_service import StudentService
from src.services.risk_service import RiskService
from src.models.student import (
    StudentCreate, StudentResponse, RiskEvaluationResponse,
    Attendance, Assignment, Contact
)
from src.models.config import SystemConfig, ConfigUpdateRequest, ConfigResponse
from src.services.config_service import ConfigService
from src.risk_assessment.config import RiskConfig

router = APIRouter()


# Student Management APIs
@router.post("/students/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student_data: StudentCreate, db: Session = Depends(get_db)):
    """Tạo sinh viên mới"""
    student_service = StudentService(db)
    
    # Kiểm tra sinh viên đã tồn tại
    existing_student = student_service.get_student_by_id(student_data.student_id)
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sinh viên với ID {student_data.student_id} đã tồn tại"
        )
    
    return student_service.create_student(student_data)


@router.get("/students/", response_model=List[StudentResponse])
def get_all_students(
    risk_level: str = None,
    sort_by: str = "student_id",
    sort_order: str = "asc",
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Lấy danh sách sinh viên với filter và sort"""
    student_service = StudentService(db)
    risk_service = RiskService(db)
    
    # Lấy tất cả sinh viên
    all_students = student_service.get_all_students()
    
    # Filter theo risk level nếu có
    if risk_level and risk_level.upper() in ["LOW", "MEDIUM", "HIGH"]:
        filtered_students = []
        for student in all_students:
            latest_risk = risk_service.get_latest_risk_evaluation(student.student_id)
            if latest_risk and latest_risk.risk_level == risk_level.upper():
                filtered_students.append(student)
        all_students = filtered_students
    
    # Sort
    reverse = sort_order.lower() == "desc"
    if sort_by == "student_name":
        all_students.sort(key=lambda x: x.student_name, reverse=reverse)
    elif sort_by == "risk_level":
        # Sort theo risk level (HIGH > MEDIUM > LOW)
        risk_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        all_students.sort(key=lambda x: risk_order.get(
            risk_service.get_latest_risk_evaluation(x.student_id).risk_level if risk_service.get_latest_risk_evaluation(x.student_id) else "LOW", 0
        ), reverse=reverse)
    else:  # sort_by == "student_id" (default)
        all_students.sort(key=lambda x: x.student_id, reverse=reverse)
    
    # Pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_students = all_students[start_idx:end_idx]
    
    return paginated_students


@router.get("/students/{student_id}/profile")
def get_student_profile(student_id: str, db: Session = Depends(get_db)):
    """Lấy hồ sơ đầy đủ của sinh viên"""
    student_service = StudentService(db)
    profile = student_service.get_student_profile(student_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sinh viên với ID: {student_id}"
        )
    
    return profile


@router.post("/students/{student_id}/attendance")
def add_student_attendance(
    student_id: str, 
    attendance_data: List[Attendance], 
    db: Session = Depends(get_db)
):
    """Thêm dữ liệu điểm danh cho sinh viên"""
    student_service = StudentService(db)
    
    try:
        student_service.add_attendance(student_id, attendance_data)
        return {"message": f"Đã thêm {len(attendance_data)} bản ghi điểm danh cho sinh viên {student_id}"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/students/{student_id}/assignments")
def add_student_assignments(
    student_id: str, 
    assignment_data: List[Assignment], 
    db: Session = Depends(get_db)
):
    """Thêm dữ liệu bài tập cho sinh viên"""
    student_service = StudentService(db)
    
    try:
        student_service.add_assignments(student_id, assignment_data)
        return {"message": f"Đã thêm {len(assignment_data)} bản ghi bài tập cho sinh viên {student_id}"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/students/{student_id}/contacts")
def add_student_contacts(
    student_id: str, 
    contact_data: List[Contact], 
    db: Session = Depends(get_db)
):
    """Thêm dữ liệu liên lạc cho sinh viên"""
    student_service = StudentService(db)
    
    try:
        student_service.add_contacts(student_id, contact_data)
        return {"message": f"Đã thêm {len(contact_data)} bản ghi liên lạc cho sinh viên {student_id}"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# Risk Assessment APIs
@router.post("/students/{student_id}/predict-risk", response_model=RiskEvaluationResponse)
def predict_dropout_risk(
    student_id: str, 
    config: RiskConfig = None,
    db: Session = Depends(get_db)
):
    """Dự đoán rủi ro bỏ học cho sinh viên"""
    risk_service = RiskService(db)
    
    try:
        result = risk_service.predict_dropout_risk(student_id, config)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/students/{student_id}/risk-evaluations", response_model=List[RiskEvaluationResponse])
def get_student_risk_evaluations(student_id: str, db: Session = Depends(get_db)):
    """Lấy tất cả kết quả đánh giá rủi ro của sinh viên"""
    risk_service = RiskService(db)
    evaluations = risk_service.get_all_risk_evaluations(student_id)
    
    if not evaluations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy kết quả đánh giá rủi ro cho sinh viên: {student_id}"
        )
    
    return evaluations


@router.get("/students/{student_id}/latest-risk", response_model=RiskEvaluationResponse)
def get_latest_risk_evaluation(student_id: str, db: Session = Depends(get_db)):
    """Lấy kết quả đánh giá rủi ro mới nhất của sinh viên"""
    risk_service = RiskService(db)
    evaluation = risk_service.get_latest_risk_evaluation(student_id)
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy kết quả đánh giá rủi ro cho sinh viên: {student_id}"
        )
    
    return evaluation


@router.get("/students/{student_id}/risk-summary")
def get_student_risk_summary(student_id: str, db: Session = Depends(get_db)):
    """Lấy tổng quan rủi ro của sinh viên"""
    risk_service = RiskService(db)
    summary = risk_service.get_student_risk_summary(student_id)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sinh viên: {student_id}"
        )
    
    return summary


# Risk Analytics APIs
@router.get("/risk/high-risk-students", response_model=List[RiskEvaluationResponse])
def get_high_risk_students(db: Session = Depends(get_db)):
    """Lấy danh sách sinh viên có rủi ro cao"""
    risk_service = RiskService(db)
    return risk_service.get_high_risk_students()


@router.get("/risk/medium-risk-students", response_model=List[RiskEvaluationResponse])
def get_medium_risk_students(db: Session = Depends(get_db)):
    """Lấy danh sách sinh viên có rủi ro trung bình"""
    risk_service = RiskService(db)
    return risk_service.get_medium_risk_students()


# Configuration APIs
@router.get("/config", response_model=ConfigResponse)
def get_system_config(db: Session = Depends(get_db)):
    """Lấy cấu hình hệ thống hiện tại"""
    config_service = ConfigService(db)
    config = config_service.get_config()
    return ConfigResponse(
        config=config,
        updated_at=datetime.utcnow()
    )


@router.put("/config", response_model=ConfigResponse)
def update_system_config(
    update_request: ConfigUpdateRequest,
    db: Session = Depends(get_db)
):
    """Cập nhật cấu hình hệ thống"""
    config_service = ConfigService(db)
    updated_config = config_service.update_config(update_request)
    
    if not updated_config:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể cập nhật cấu hình"
        )
    
    return ConfigResponse(
        config=updated_config,
        updated_at=datetime.utcnow()
    )


@router.post("/config/reset")
def reset_system_config(db: Session = Depends(get_db)):
    """Reset cấu hình về mặc định"""
    config_service = ConfigService(db)
    success = config_service.reset_to_default()
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể reset cấu hình"
        )
    
    return {"message": "Cấu hình đã được reset về mặc định"}


@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Lấy thống kê cho dashboard"""
    student_service = StudentService(db)
    risk_service = RiskService(db)
    
    # Lấy dữ liệu
    all_students = student_service.get_all_students()
    high_risk_students = risk_service.get_high_risk_students()
    medium_risk_students = risk_service.get_medium_risk_students()
    
    # Tính toán thống kê
    total_students = len(all_students)
    high_risk_count = len(high_risk_students)
    medium_risk_count = len(medium_risk_students)
    low_risk_count = total_students - high_risk_count - medium_risk_count
    
    return {
        "total_students": total_students,
        "high_risk_count": high_risk_count,
        "medium_risk_count": medium_risk_count,
        "low_risk_count": low_risk_count,
        "risk_distribution": {
            "low": low_risk_count,
            "medium": medium_risk_count,
            "high": high_risk_count
        }
    }


@router.get("/export/csv")
def export_results_to_csv(db: Session = Depends(get_db)):
    """Export kết quả đánh giá rủi ro ra file CSV"""
    from fastapi.responses import FileResponse
    import csv
    import os
    from datetime import datetime
    
    student_service = StudentService(db)
    risk_service = RiskService(db)
    
    # Lấy tất cả sinh viên và đánh giá rủi ro mới nhất
    all_students = student_service.get_all_students()
    results = []
    
    for student in all_students:
        latest_risk = risk_service.get_latest_risk_evaluation(student.student_id)
        
        if latest_risk:
            results.append({
                'Student ID': student.student_id,
                'Student Name': student.student_name,
                'Score': latest_risk.score,
                'Risk Level': latest_risk.risk_level,
                'Note': latest_risk.note,
                'Evaluated At': latest_risk.evaluated_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        else:
            # Sinh viên chưa được đánh giá
            results.append({
                'Student ID': student.student_id,
                'Student Name': student.student_name,
                'Score': 'N/A',
                'Risk Level': 'N/A',
                'Note': 'Chưa được đánh giá',
                'Evaluated At': 'N/A'
            })
    
    # Tạo file CSV
    csv_filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    csv_path = csv_filename
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Student ID', 'Student Name', 'Score', 'Risk Level', 'Note', 'Evaluated At']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    
    # Trả về file để download
    return FileResponse(
        path=csv_path,
        filename=csv_filename,
        media_type='text/csv'
    )


@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Student Dropout Risk Assessment System is running"} 