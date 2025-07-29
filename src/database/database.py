from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Tạo thư mục database nếu chưa tồn tại
db_dir = Path("database")
db_dir.mkdir(exist_ok=True)

# Cấu hình database
SQLALCHEMY_DATABASE_URL = "sqlite:///database/student_risk.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tạo Base chung cho toàn bộ ứng dụng
Base = declarative_base()


def get_db():
    """Dependency để lấy database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Tạo tất cả bảng trong database"""
    # Import tất cả models để đảm bảo chúng được đăng ký với Base
    from src.models.student import StudentDB, AttendanceDB, AssignmentDB, ContactDB, RiskEvaluationDB, SystemConfigDB
    
    Base.metadata.create_all(bind=engine) 