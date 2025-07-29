from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from src.models.student import RiskEvaluationDB, RiskEvaluationResponse
from src.risk_assessment.calculator import RiskCalculator
from src.risk_assessment.config import RiskConfig
from src.services.student_service import StudentService


class RiskService:
    """Service để quản lý đánh giá rủi ro"""
    
    def __init__(self, db: Session):
        self.db = db
        self.student_service = StudentService(db)
        self.risk_calculator = RiskCalculator()
    
    def predict_dropout_risk(self, student_id: str, config: RiskConfig = None) -> RiskEvaluationDB:
        """Dự đoán rủi ro bỏ học cho sinh viên"""
        # Lấy hồ sơ sinh viên
        student_profile = self.student_service.get_student_profile(student_id)
        if not student_profile:
            raise ValueError(f"Không tìm thấy sinh viên với ID: {student_id}")
        
        # Lấy ngưỡng rủi ro từ cấu hình
        from src.services.config_service import ConfigService
        config_service = ConfigService(self.db)
        thresholds = config_service.get_risk_thresholds()
        
        # Tính toán rủi ro
        if config:
            self.risk_calculator.config = config
        
        risk_result = self.risk_calculator.calculate_risk(student_profile, thresholds)
        
        # Lấy student database ID
        db_student = self.student_service.get_student_by_id(student_id)
        
        # Lưu kết quả vào database
        db_risk_evaluation = RiskEvaluationDB(
            student_id=db_student.id,
            score=risk_result.score,
            risk_level=risk_result.risk_level,
            note=risk_result.note,
            evaluated_at=datetime.utcnow()
        )
        
        self.db.add(db_risk_evaluation)
        self.db.commit()
        self.db.refresh(db_risk_evaluation)
        
        return db_risk_evaluation
    
    def get_latest_risk_evaluation(self, student_id: str) -> Optional[RiskEvaluationDB]:
        """Lấy kết quả đánh giá rủi ro mới nhất của sinh viên"""
        db_student = self.student_service.get_student_by_id(student_id)
        if not db_student:
            return None
        
        return self.db.query(RiskEvaluationDB).filter(
            RiskEvaluationDB.student_id == db_student.id
        ).order_by(RiskEvaluationDB.evaluated_at.desc()).first()
    
    def get_all_risk_evaluations(self, student_id: str) -> List[RiskEvaluationDB]:
        """Lấy tất cả kết quả đánh giá rủi ro của sinh viên"""
        db_student = self.student_service.get_student_by_id(student_id)
        if not db_student:
            return []
        
        return self.db.query(RiskEvaluationDB).filter(
            RiskEvaluationDB.student_id == db_student.id
        ).order_by(RiskEvaluationDB.evaluated_at.desc()).all()
    
    def get_high_risk_students(self) -> List[RiskEvaluationDB]:
        """Lấy danh sách sinh viên có rủi ro cao (chỉ đánh giá mới nhất)"""
        # Subquery để lấy đánh giá mới nhất cho mỗi sinh viên
        latest_evaluations = self.db.query(
            RiskEvaluationDB.student_id,
            func.max(RiskEvaluationDB.evaluated_at).label('latest_evaluated_at')
        ).group_by(RiskEvaluationDB.student_id).subquery()
        
        return self.db.query(RiskEvaluationDB).join(
            latest_evaluations,
            (RiskEvaluationDB.student_id == latest_evaluations.c.student_id) &
            (RiskEvaluationDB.evaluated_at == latest_evaluations.c.latest_evaluated_at)
        ).filter(
            RiskEvaluationDB.risk_level == "HIGH"
        ).order_by(RiskEvaluationDB.evaluated_at.desc()).all()
    
    def get_medium_risk_students(self) -> List[RiskEvaluationDB]:
        """Lấy danh sách sinh viên có rủi ro trung bình (chỉ đánh giá mới nhất)"""
        # Subquery để lấy đánh giá mới nhất cho mỗi sinh viên
        latest_evaluations = self.db.query(
            RiskEvaluationDB.student_id,
            func.max(RiskEvaluationDB.evaluated_at).label('latest_evaluated_at')
        ).group_by(RiskEvaluationDB.student_id).subquery()
        
        return self.db.query(RiskEvaluationDB).join(
            latest_evaluations,
            (RiskEvaluationDB.student_id == latest_evaluations.c.student_id) &
            (RiskEvaluationDB.evaluated_at == latest_evaluations.c.latest_evaluated_at)
        ).filter(
            RiskEvaluationDB.risk_level == "MEDIUM"
        ).order_by(RiskEvaluationDB.evaluated_at.desc()).all()
    
    def get_student_risk_summary(self, student_id: str) -> dict:
        """Lấy tổng quan rủi ro của sinh viên"""
        student_profile = self.student_service.get_student_profile(student_id)
        if not student_profile:
            return None
        
        latest_evaluation = self.get_latest_risk_evaluation(student_id)
        
        # Tính toán thống kê
        total_attendance = len(student_profile.attendance)
        attended_sessions = sum(1 for a in student_profile.attendance if a.status == "ATTEND")
        attendance_rate = (attended_sessions / total_attendance * 100) if total_attendance > 0 else 0
        
        total_assignments = len(student_profile.assignments)
        submitted_assignments = sum(1 for a in student_profile.assignments if a.submitted)
        submission_rate = (submitted_assignments / total_assignments * 100) if total_assignments > 0 else 0
        
        failed_contacts = sum(1 for c in student_profile.contacts if c.status == "FAILED")
        
        return {
            "student_id": student_id,
            "student_name": student_profile.student_name,
            "attendance_rate": round(attendance_rate, 2),
            "submission_rate": round(submission_rate, 2),
            "failed_contacts": failed_contacts,
            "latest_risk_evaluation": latest_evaluation,
            "total_attendance_sessions": total_attendance,
            "total_assignments": total_assignments,
            "total_contacts": len(student_profile.contacts)
        } 