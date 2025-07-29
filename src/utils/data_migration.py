"""
Data Migration Utility
Công cụ để migrate dữ liệu từ file JSON sang database
"""

import json
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

from src.database.database import SessionLocal
from src.services.student_service import StudentService
from src.models.student import StudentCreate, Attendance, Assignment, Contact


def migrate_json_to_database(json_file_path: str):
    """Migrate dữ liệu từ file JSON sang database"""
    db = SessionLocal()
    student_service = StudentService(db)
    
    try:
        # Đọc file JSON
        with open(json_file_path, 'r', encoding='utf-8') as f:
            students_data = json.load(f)
        
        print(f"📁 Đang migrate {len(students_data)} sinh viên từ {json_file_path}")
        
        for student_data in students_data:
            student_id = student_data['student_id']
            student_name = student_data['student_name']
            
            # Kiểm tra sinh viên đã tồn tại
            existing_student = student_service.get_student_by_id(student_id)
            if existing_student:
                print(f"⚠️  Sinh viên {student_id} đã tồn tại, bỏ qua...")
                continue
            
            # Tạo sinh viên mới
            student_create = StudentCreate(
                student_id=student_id,
                student_name=student_name
            )
            
            new_student = student_service.create_student(student_create)
            print(f"✅ Đã tạo sinh viên: {student_id} - {student_name}")
            
            # Thêm dữ liệu điểm danh
            if student_data.get('attendance'):
                attendance_list = [
                    Attendance(
                        date=datetime.strptime(att['date'], '%Y-%m-%d').date(),
                        status=att['status']
                    )
                    for att in student_data['attendance']
                ]
                student_service.add_attendance(student_id, attendance_list)
                print(f"   📊 Đã thêm {len(attendance_list)} bản ghi điểm danh")
            
            # Thêm dữ liệu bài tập
            if student_data.get('assignments'):
                assignment_list = [
                    Assignment(
                        date=datetime.strptime(ass['date'], '%Y-%m-%d').date(),
                        name=ass['name'],
                        submitted=ass['submitted']
                    )
                    for ass in student_data['assignments']
                ]
                student_service.add_assignments(student_id, assignment_list)
                print(f"   📝 Đã thêm {len(assignment_list)} bản ghi bài tập")
            
            # Thêm dữ liệu liên lạc
            if student_data.get('contacts'):
                contact_list = [
                    Contact(
                        date=datetime.strptime(cont['date'], '%Y-%m-%d').date(),
                        status=cont['status']
                    )
                    for cont in student_data['contacts']
                ]
                student_service.add_contacts(student_id, contact_list)
                print(f"   📞 Đã thêm {len(contact_list)} bản ghi liên lạc")
        
        print("🎉 Migration hoàn thành!")
        
    except Exception as e:
        print(f"❌ Lỗi trong quá trình migration: {e}")
        db.rollback()
    finally:
        db.close()


def migrate_sample_data():
    """Migrate dữ liệu mẫu từ data/sample_students.json"""
    sample_file = Path("data/sample_students.json")
    
    if not sample_file.exists():
        print(f"❌ Không tìm thấy file {sample_file}")
        return
    
    print("🔄 Bắt đầu migration dữ liệu mẫu...")
    migrate_json_to_database(str(sample_file))


if __name__ == "__main__":
    migrate_sample_data() 