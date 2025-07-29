from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, date

from src.models.student import (
    StudentDB, AttendanceDB, AssignmentDB, ContactDB,
    StudentCreate, StudentResponse
)
from src.models.student import Student, Attendance, Assignment, Contact


class StudentService:
    """Service để quản lý sinh viên"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_student(self, student_data: StudentCreate) -> StudentDB:
        """Tạo sinh viên mới"""
        db_student = StudentDB(
            student_id=student_data.student_id,
            student_name=student_data.student_name
        )
        self.db.add(db_student)
        self.db.commit()
        self.db.refresh(db_student)
        return db_student
    
    def get_student_by_id(self, student_id: str) -> Optional[StudentDB]:
        """Lấy sinh viên theo ID"""
        return self.db.query(StudentDB).filter(StudentDB.student_id == student_id).first()
    
    def get_student_by_db_id(self, db_id: int) -> Optional[StudentDB]:
        """Lấy sinh viên theo database ID"""
        return self.db.query(StudentDB).filter(StudentDB.id == db_id).first()
    
    def get_all_students(self) -> List[StudentDB]:
        """Lấy tất cả sinh viên"""
        return self.db.query(StudentDB).all()
    
    def add_attendance(self, student_id: str, attendance_data: List[Attendance]):
        """Thêm dữ liệu điểm danh cho sinh viên"""
        student = self.get_student_by_id(student_id)
        if not student:
            raise ValueError(f"Không tìm thấy sinh viên với ID: {student_id}")
        
        for att in attendance_data:
            db_attendance = AttendanceDB(
                student_id=student.id,
                date=datetime.combine(att.date, datetime.min.time()),
                status=att.status
            )
            self.db.add(db_attendance)
        
        self.db.commit()
    
    def add_assignments(self, student_id: str, assignment_data: List[Assignment]):
        """Thêm dữ liệu bài tập cho sinh viên"""
        student = self.get_student_by_id(student_id)
        if not student:
            raise ValueError(f"Không tìm thấy sinh viên với ID: {student_id}")
        
        for ass in assignment_data:
            db_assignment = AssignmentDB(
                student_id=student.id,
                date=datetime.combine(ass.date, datetime.min.time()),
                name=ass.name,
                submitted=ass.submitted
            )
            self.db.add(db_assignment)
        
        self.db.commit()
    
    def add_contacts(self, student_id: str, contact_data: List[Contact]):
        """Thêm dữ liệu liên lạc cho sinh viên"""
        student = self.get_student_by_id(student_id)
        if not student:
            raise ValueError(f"Không tìm thấy sinh viên với ID: {student_id}")
        
        for cont in contact_data:
            db_contact = ContactDB(
                student_id=student.id,
                date=datetime.combine(cont.date, datetime.min.time()),
                status=cont.status
            )
            self.db.add(db_contact)
        
        self.db.commit()
    
    def get_student_profile(self, student_id: str) -> Optional[Student]:
        """Lấy hồ sơ đầy đủ của sinh viên"""
        db_student = self.get_student_by_id(student_id)
        if not db_student:
            return None
        
        # Lấy điểm danh
        attendance_records = self.db.query(AttendanceDB).filter(
            AttendanceDB.student_id == db_student.id
        ).all()
        
        attendance = [
            Attendance(
                date=record.date.date(),
                status=record.status
            )
            for record in attendance_records
        ]
        
        # Lấy bài tập
        assignment_records = self.db.query(AssignmentDB).filter(
            AssignmentDB.student_id == db_student.id
        ).all()
        
        assignments = [
            Assignment(
                date=record.date.date(),
                name=record.name,
                submitted=record.submitted
            )
            for record in assignment_records
        ]
        
        # Lấy liên lạc
        contact_records = self.db.query(ContactDB).filter(
            ContactDB.student_id == db_student.id
        ).all()
        
        contacts = [
            Contact(
                date=record.date.date(),
                status=record.status
            )
            for record in contact_records
        ]
        
        return Student(
            student_id=db_student.student_id,
            student_name=db_student.student_name,
            attendance=attendance,
            assignments=assignments,
            contacts=contacts
        ) 