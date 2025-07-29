#!/usr/bin/env python3
"""
Student Dropout Risk Assessment System - FastAPI Application
Hệ thống đánh giá rủi ro bỏ học của sinh viên
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from src.database.database import create_tables
from src.api.routes import router as api_router
from src.web.routes import router as web_router
from src.web.templates import create_templates


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events cho ứng dụng"""
    # Startup
    print("🚀 Khởi động hệ thống đánh giá rủi ro bỏ học...")
    
    # Tạo database tables
    create_tables()
    print("✅ Database tables đã được tạo")
    
    # Tạo web templates
    create_templates()
    print("✅ Web templates đã được tạo")
    
    yield
    
    # Shutdown
    print("🛑 Đang tắt hệ thống...")


# Tạo FastAPI app
app = FastAPI(
    title="Student Dropout Risk Assessment System",
    description="Hệ thống đánh giá rủi ro bỏ học của sinh viên dựa trên điểm danh, bài tập và liên lạc",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (optional)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(api_router, prefix="/api", tags=["API"])
app.include_router(web_router, tags=["Web"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Student Dropout Risk Assessment System",
        "version": "1.0.0",
        "docs": "/docs",
        "web": "/students"
    }


if __name__ == "__main__":
    import uvicorn
    
    print("🎓 Student Dropout Risk Assessment System")
    print("📚 Hệ thống đánh giá rủi ro bỏ học của sinh viên")
    print("🌐 Web Interface: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔧 API Endpoints: http://localhost:8000/api")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 