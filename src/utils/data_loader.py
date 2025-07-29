import json
from typing import List
from pathlib import Path
from src.models.student import Student


class DataLoader:
    """Class để load và xử lý dữ liệu sinh viên từ file JSON"""
    
    @staticmethod
    def load_students_from_json(file_path: str) -> List[Student]:
        """Load danh sách sinh viên từ file JSON"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File không tồn tại: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            students = []
            for student_data in data:
                student = Student(**student_data)
                students.append(student)
            
            return students
            
        except json.JSONDecodeError as e:
            raise ValueError(f"File JSON không hợp lệ: {e}")
        except Exception as e:
            raise ValueError(f"Lỗi khi load dữ liệu: {e}")
    
    @staticmethod
    def save_results_to_csv(results: List, output_path: str):
        """Lưu kết quả ra file CSV"""
        import pandas as pd
        
        # Chuyển đổi kết quả thành DataFrame
        data = []
        for result in results:
            data.append({
                'Student ID': result.student_id,
                'Score': result.score,
                'Risk Level': result.risk_level,
                'Note': result.note or ''
            })
        
        df = pd.DataFrame(data)
        df.to_csv(output_path, index=False)
        print(f"Kết quả đã được lưu vào: {output_path}") 