from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List

from src.database.database import get_db
from src.services.student_service import StudentService
from src.services.risk_service import RiskService
from src.web.templates import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request, db: Session = Depends(get_db)):
    """Dashboard trang chủ"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request
    })


@router.get("/config", response_class=HTMLResponse)
async def config_page(request: Request, db: Session = Depends(get_db)):
    """Trang cấu hình hệ thống"""
    return templates.TemplateResponse("config.html", {
        "request": request
    })


@router.get("/students", response_class=HTMLResponse)
async def students_page(request: Request, db: Session = Depends(get_db)):
    """Trang danh sách sinh viên với sort và filter"""
    return templates.TemplateResponse("student_list.html", {
        "request": request
    })


@router.get("/students/{student_id}", response_class=HTMLResponse)
async def student_detail_page(
    request: Request, 
    student_id: str, 
    db: Session = Depends(get_db)
):
    """Trang chi tiết sinh viên"""
    student_service = StudentService(db)
    risk_service = RiskService(db)
    
    # Lấy hồ sơ sinh viên
    student_profile = student_service.get_student_profile(student_id)
    if not student_profile:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")
    
    # Lấy thông tin rủi ro
    latest_risk = risk_service.get_latest_risk_evaluation(student_id)
    risk_evaluations = risk_service.get_all_risk_evaluations(student_id)
    
    # Tính toán thống kê
    total_attendance = len(student_profile.attendance)
    attended_sessions = sum(1 for a in student_profile.attendance if a.status == "ATTEND")
    attendance_rate = (attended_sessions / total_attendance * 100) if total_attendance > 0 else 0
    
    total_assignments = len(student_profile.assignments)
    submitted_assignments = sum(1 for a in student_profile.assignments if a.submitted)
    submission_rate = (submitted_assignments / total_assignments * 100) if total_assignments > 0 else 0
    
    failed_contacts = sum(1 for c in student_profile.contacts if c.status == "FAILED")
    
    # Dữ liệu cho biểu đồ điểm danh
    attendance_dates = [att.date.strftime('%d/%m') for att in student_profile.attendance]
    attendance_data = [1 if att.status == "ATTEND" else 0 for att in student_profile.attendance]
    
    # Dữ liệu cho biểu đồ rủi ro
    risk_distribution = [0, 0, 0]  # [LOW, MEDIUM, HIGH]
    for evaluation in risk_evaluations:
        if evaluation.risk_level == "LOW":
            risk_distribution[0] += 1
        elif evaluation.risk_level == "MEDIUM":
            risk_distribution[1] += 1
        elif evaluation.risk_level == "HIGH":
            risk_distribution[2] += 1
    
    return templates.TemplateResponse("student_detail.html", {
        "request": request,
        "student": student_profile,
        "latest_risk": latest_risk,
        "risk_evaluations": risk_evaluations,
        "attendance_rate": attendance_rate,
        "submission_rate": submission_rate,
        "failed_contacts": failed_contacts,
        "attendance_dates": attendance_dates,
        "attendance_data": attendance_data,
        "risk_distribution": risk_distribution
    })


@router.get("/risk/high", response_class=HTMLResponse)
async def high_risk_page(request: Request, db: Session = Depends(get_db)):
    """Trang sinh viên có rủi ro cao"""
    risk_service = RiskService(db)
    student_service = StudentService(db)
    
    high_risk_evaluations = risk_service.get_high_risk_students()
    
    # Thêm thông tin sinh viên
    for evaluation in high_risk_evaluations:
        student = student_service.get_student_by_db_id(evaluation.student_id)
        evaluation.student = student
    
    return templates.TemplateResponse("risk_page.html", {
        "request": request,
        "risk_evaluations": high_risk_evaluations,
        "risk_level": "HIGH"
    })


@router.get("/risk/medium", response_class=HTMLResponse)
async def medium_risk_page(request: Request, db: Session = Depends(get_db)):
    """Trang sinh viên có rủi ro trung bình"""
    risk_service = RiskService(db)
    student_service = StudentService(db)
    
    medium_risk_evaluations = risk_service.get_medium_risk_students()
    
    # Thêm thông tin sinh viên
    for evaluation in medium_risk_evaluations:
        student = student_service.get_student_by_db_id(evaluation.student_id)
        evaluation.student = student
    
    return templates.TemplateResponse("risk_page.html", {
        "request": request,
        "risk_evaluations": medium_risk_evaluations,
        "risk_level": "MEDIUM"
    }) 