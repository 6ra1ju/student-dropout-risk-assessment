from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship

# Import Base từ database module
from src.database.database import Base


class Attendance(BaseModel):
    """Model cho dữ liệu điểm danh"""
    date: date
    status: str = Field(..., description="Trạng thái: ATTEND hoặc ABSENT")


class Assignment(BaseModel):
    """Model cho dữ liệu bài tập"""
    date: date
    name: str
    submitted: bool


class Contact(BaseModel):
    """Model cho dữ liệu liên lạc"""
    date: date
    status: str = Field(..., description="Trạng thái: SUCCESS hoặc FAILED")


class Student(BaseModel):
    """Model cho dữ liệu sinh viên"""
    student_id: str
    student_name: str
    attendance: List[Attendance]
    assignments: List[Assignment]
    contacts: List[Contact]


class RiskResult(BaseModel):
    """Model cho kết quả đánh giá rủi ro"""
    student_id: str
    score: int = Field(..., ge=0, le=3)
    risk_level: str = Field(..., description="LOW, MEDIUM, hoặc HIGH")
    note: Optional[str] = None


# Database Models
class StudentDB(Base):
    """Database model cho sinh viên"""
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), unique=True, index=True, nullable=False)
    student_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attendance_records = relationship("AttendanceDB", back_populates="student", cascade="all, delete-orphan")
    assignment_records = relationship("AssignmentDB", back_populates="student", cascade="all, delete-orphan")
    contact_records = relationship("ContactDB", back_populates="student", cascade="all, delete-orphan")
    risk_evaluations = relationship("RiskEvaluationDB", back_populates="student", cascade="all, delete-orphan")


class AttendanceDB(Base):
    """Database model cho điểm danh"""
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False)  # ATTEND or ABSENT
    
    student = relationship("StudentDB", back_populates="attendance_records")


class AssignmentDB(Base):
    """Database model cho bài tập"""
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    name = Column(String(100), nullable=False)
    submitted = Column(Boolean, default=False)
    
    student = relationship("StudentDB", back_populates="assignment_records")


class ContactDB(Base):
    """Database model cho liên lạc"""
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False)  # SUCCESS or FAILED
    
    student = relationship("StudentDB", back_populates="contact_records")


class RiskEvaluationDB(Base):
    """Database model cho kết quả đánh giá rủi ro"""
    __tablename__ = "risk_evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    score = Column(Integer, nullable=False)
    risk_level = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH
    note = Column(Text, nullable=True)
    evaluated_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("StudentDB", back_populates="risk_evaluations")


class SystemConfigDB(Base):
    """Database model cho cấu hình hệ thống"""
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Pydantic models for API
class StudentCreate(BaseModel):
    """Model để tạo sinh viên mới"""
    student_id: str
    student_name: str


class StudentResponse(BaseModel):
    """Model response cho sinh viên"""
    id: int
    student_id: str
    student_name: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RiskEvaluationResponse(BaseModel):
    """Model response cho kết quả đánh giá rủi ro"""
    id: int
    student_id: int
    score: int
    risk_level: str
    note: Optional[str]
    evaluated_at: datetime
    
    class Config:
        from_attributes = True 