#!/usr/bin/env python3
"""
Student Dropout Risk Assessment System
Hệ thống đánh giá rủi ro bỏ học của sinh viên
"""

import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path

from src.utils.data_loader import DataLoader
from src.risk_assessment.calculator import RiskCalculator
from src.risk_assessment.config import RiskConfig

app = typer.Typer()
console = Console()


@app.command()
def main(
    input_file: str = typer.Option("data/sample_students.json", "--input", "-i", help="Đường dẫn file JSON đầu vào"),
    output_file: str = typer.Option("results.csv", "--output", "-o", help="Đường dẫn file CSV đầu ra"),
    attendance_threshold: float = typer.Option(0.75, "--attendance", help="Ngưỡng tỷ lệ đi học (0-1)"),
    assignment_threshold: float = typer.Option(0.50, "--assignment", help="Ngưỡng tỷ lệ nộp bài tập (0-1)"),
    contact_threshold: int = typer.Option(2, "--contact", help="Ngưỡng số lần liên lạc thất bại")
):
    """
    Hệ thống đánh giá rủi ro bỏ học của sinh viên
    
    Tính toán rủi ro dựa trên 3 tín hiệu:
    - Điểm danh: Tỷ lệ đi học
    - Bài tập: Tỷ lệ nộp bài tập  
    - Liên lạc: Số lần liên lạc thất bại
    """
    
    try:
        # Tạo cấu hình
        config = RiskConfig(
            attendance_threshold=attendance_threshold,
            assignment_threshold=assignment_threshold,
            contact_failed_threshold=contact_threshold
        )
        
        console.print(f"[bold blue]Hệ thống đánh giá rủi ro bỏ học[/bold blue]")
        console.print(f"📁 File đầu vào: {input_file}")
        console.print(f"📊 Cấu hình:")
        console.print(f"   - Ngưỡng đi học: {attendance_threshold*100}%")
        console.print(f"   - Ngưỡng bài tập: {assignment_threshold*100}%")
        console.print(f"   - Ngưỡng liên lạc: {contact_threshold} lần thất bại")
        console.print()
        
        # Load dữ liệu
        console.print("[yellow]Đang load dữ liệu...[/yellow]")
        students = DataLoader.load_students_from_json(input_file)
        console.print(f"✅ Đã load {len(students)} sinh viên")
        
        # Tính toán rủi ro
        console.print("[yellow]Đang tính toán rủi ro...[/yellow]")
        calculator = RiskCalculator(config)
        results = calculator.calculate_risks(students)
        
        # Hiển thị kết quả
        display_results(results)
        
        # Lưu kết quả
        if output_file:
            DataLoader.save_results_to_csv(results, output_file)
        
        console.print(f"\n[bold green]✅ Hoàn thành![/bold green]")
        
    except FileNotFoundError as e:
        console.print(f"[bold red]❌ Lỗi: {e}[/bold red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]❌ Lỗi không mong muốn: {e}[/bold red]")
        raise typer.Exit(1)


def display_results(results):
    """Hiển thị kết quả dưới dạng bảng"""
    table = Table(title="Kết quả đánh giá rủi ro")
    
    table.add_column("Student ID", style="cyan", no_wrap=True)
    table.add_column("Score", style="magenta", justify="center")
    table.add_column("Risk Level", style="bold")
    table.add_column("Note", style="dim")
    
    for result in results:
        # Màu sắc cho mức rủi ro
        risk_color = {
            "LOW": "green",
            "MEDIUM": "yellow", 
            "HIGH": "red"
        }.get(result.risk_level, "white")
        
        table.add_row(
            result.student_id,
            str(result.score),
            f"[{risk_color}]{result.risk_level}[/{risk_color}]",
            result.note or ""
        )
    
    console.print(table)


@app.command()
def export_current_results(
    output_file: str = typer.Option("results.csv", "--output", "-o", help="Output CSV file path")
):
    """Export kết quả đánh giá rủi ro hiện tại từ database ra CSV"""
    try:
        from src.database.database import SessionLocal, create_tables
        from src.services.student_service import StudentService
        from src.services.risk_service import RiskService
        
        # Tạo database nếu chưa có
        create_tables()
        
        # Kết nối database
        db = SessionLocal()
        student_service = StudentService(db)
        risk_service = RiskService(db)
        
        # Lấy tất cả sinh viên và đánh giá rủi ro mới nhất
        all_students = student_service.get_all_students()
        results = []
        
        console.print("📊 Đang thu thập dữ liệu từ database...", style="blue")
        
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
        
        # Lưu vào CSV
        DataLoader.save_results_to_csv(results, output_file)
        
        # Hiển thị thống kê
        total_students = len(results)
        evaluated_students = len([r for r in results if r['Score'] != 'N/A'])
        
        console.print(f"\n📈 Thống kê:", style="green")
        console.print(f"   Tổng sinh viên: {total_students}", style="white")
        console.print(f"   Đã đánh giá: {evaluated_students}", style="white")
        console.print(f"   Chưa đánh giá: {total_students - evaluated_students}", style="white")
        
        console.print(f"\n✅ Kết quả đã được lưu vào: {output_file}", style="green")
        
        db.close()
        
    except Exception as e:
        console.print(f"❌ Lỗi: {e}", style="red")
        raise typer.Exit(1)


if __name__ == "__main__":
    app() 