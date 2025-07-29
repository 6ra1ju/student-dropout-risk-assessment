from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RiskThresholdConfig(BaseModel):
    """Model cho cấu hình ngưỡng rủi ro"""
    low_threshold: int = Field(default=1, ge=0, le=5, description="Ngưỡng rủi ro thấp")
    medium_threshold: int = Field(default=2, ge=0, le=5, description="Ngưỡng rủi ro trung bình")
    high_threshold: int = Field(default=3, ge=0, le=5, description="Ngưỡng rủi ro cao")
    
    class Config:
        json_schema_extra = {
            "example": {
                "low_threshold": 1,
                "medium_threshold": 2,
                "high_threshold": 3
            }
        }


class SystemConfig(BaseModel):
    """Model cho cấu hình hệ thống"""
    risk_thresholds: RiskThresholdConfig
    auto_refresh_interval: int = Field(default=30, ge=10, le=300, description="Thời gian tự động refresh (giây)")
    enable_notifications: bool = Field(default=True, description="Bật thông báo")
    max_students_per_page: int = Field(default=20, ge=5, le=100, description="Số sinh viên tối đa mỗi trang")
    
    class Config:
        json_schema_extra = {
            "example": {
                "risk_thresholds": {
                    "low_threshold": 1,
                    "medium_threshold": 2,
                    "high_threshold": 3
                },
                "auto_refresh_interval": 30,
                "enable_notifications": True,
                "max_students_per_page": 20
            }
        }


class ConfigUpdateRequest(BaseModel):
    """Model cho request cập nhật cấu hình"""
    risk_thresholds: Optional[RiskThresholdConfig] = None
    auto_refresh_interval: Optional[int] = Field(None, ge=10, le=300)
    enable_notifications: Optional[bool] = None
    max_students_per_page: Optional[int] = Field(None, ge=5, le=100)


class ConfigResponse(BaseModel):
    """Model response cho cấu hình"""
    config: SystemConfig
    updated_at: datetime
    
    class Config:
        from_attributes = True 