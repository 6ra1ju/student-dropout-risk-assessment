from typing import List
from src.models.student import Student, RiskResult
from src.risk_assessment.config import RiskConfig


class RiskCalculator:
    """Class chính để tính toán rủi ro bỏ học của sinh viên"""
    
    def __init__(self, config: RiskConfig = None):
        self.config = config or RiskConfig()
    
    def calculate_attendance_risk(self, student: Student) -> bool:
        """Tính toán rủi ro từ điểm danh"""
        if not student.attendance:
            return False
        
        total_sessions = len(student.attendance)
        attended_sessions = sum(1 for a in student.attendance if a.status == "ATTEND")
        attendance_rate = attended_sessions / total_sessions
        
        return attendance_rate < self.config.attendance_threshold
    
    def calculate_assignment_risk(self, student: Student) -> bool:
        """Tính toán rủi ro từ bài tập"""
        if not student.assignments:
            return False
        
        total_assignments = len(student.assignments)
        submitted_assignments = sum(1 for a in student.assignments if a.submitted)
        submission_rate = submitted_assignments / total_assignments
        
        return submission_rate < self.config.assignment_threshold
    
    def calculate_contact_risk(self, student: Student) -> bool:
        """Tính toán rủi ro từ liên lạc"""
        failed_contacts = sum(1 for c in student.contacts if c.status == "FAILED")
        return failed_contacts >= self.config.contact_failed_threshold
    
    def generate_note(self, attendance_risk: bool, assignment_risk: bool, contact_risk: bool) -> str:
        """Tạo ghi chú cho kết quả đánh giá"""
        risk_factors = []
        
        if attendance_risk:
            risk_factors.append("attendance")
        if assignment_risk:
            risk_factors.append("assignment")
        if contact_risk:
            risk_factors.append("communication")
        
        if not risk_factors:
            return "No signs of disengagement detected"
        
        return ", ".join(risk_factors) + " risk factors"
    
    def calculate_risk(self, student: Student, thresholds=None) -> RiskResult:
        """Tính toán rủi ro tổng thể cho một sinh viên"""
        attendance_risk = self.calculate_attendance_risk(student)
        assignment_risk = self.calculate_assignment_risk(student)
        contact_risk = self.calculate_contact_risk(student)
        
        # Tính điểm số (0-3)
        score = sum([attendance_risk, assignment_risk, contact_risk])
        
        # Xác định mức rủi ro dựa trên ngưỡng
        if thresholds:
            if score >= thresholds.high_threshold:
                risk_level = "HIGH"
            elif score >= thresholds.medium_threshold:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
        else:
            # Sử dụng config mặc định
            risk_level = self.config.get_risk_level(score)
        
        # Tạo ghi chú
        note = self.generate_note(attendance_risk, assignment_risk, contact_risk)
        
        return RiskResult(
            student_id=student.student_id,
            score=score,
            risk_level=risk_level,
            note=note
        )
    
    def calculate_risks(self, students: List[Student]) -> List[RiskResult]:
        """Tính toán rủi ro cho danh sách sinh viên"""
        results = []
        for student in students:
            result = self.calculate_risk(student)
            results.append(result)
        return results 