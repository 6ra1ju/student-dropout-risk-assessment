import json
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

from src.models.student import SystemConfigDB
from src.models.config import SystemConfig, RiskThresholdConfig, ConfigUpdateRequest


class ConfigService:
    """Service để quản lý cấu hình hệ thống"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_default_config(self) -> SystemConfig:
        """Lấy cấu hình mặc định"""
        return SystemConfig(
            risk_thresholds=RiskThresholdConfig(
                low_threshold=1,
                medium_threshold=2,
                high_threshold=3
            ),
            auto_refresh_interval=30,
            enable_notifications=True,
            max_students_per_page=20
        )
    
    def get_config(self) -> SystemConfig:
        """Lấy cấu hình hiện tại từ database"""
        try:
            # Lấy cấu hình từ database
            config_record = self.db.query(SystemConfigDB).filter(
                SystemConfigDB.config_key == "system_config"
            ).first()
            
            if config_record:
                config_data = json.loads(config_record.config_value)
                return SystemConfig(**config_data)
            else:
                # Tạo cấu hình mặc định nếu chưa có
                default_config = self.get_default_config()
                self.save_config(default_config)
                return default_config
                
        except Exception as e:
            print(f"Lỗi khi lấy cấu hình: {e}")
            return self.get_default_config()
    
    def save_config(self, config: SystemConfig) -> bool:
        """Lưu cấu hình vào database"""
        try:
            config_data = config.model_dump_json()
            
            # Kiểm tra xem đã có cấu hình chưa
            existing_config = self.db.query(SystemConfigDB).filter(
                SystemConfigDB.config_key == "system_config"
            ).first()
            
            if existing_config:
                existing_config.config_value = config_data
                existing_config.updated_at = datetime.utcnow()
            else:
                new_config = SystemConfigDB(
                    config_key="system_config",
                    config_value=config_data
                )
                self.db.add(new_config)
            
            self.db.commit()
            return True
            
        except Exception as e:
            print(f"Lỗi khi lưu cấu hình: {e}")
            self.db.rollback()
            return False
    
    def update_config(self, update_request: ConfigUpdateRequest) -> Optional[SystemConfig]:
        """Cập nhật cấu hình"""
        try:
            current_config = self.get_config()
            
            # Cập nhật các trường được cung cấp
            if update_request.risk_thresholds:
                current_config.risk_thresholds = update_request.risk_thresholds
            
            if update_request.auto_refresh_interval is not None:
                current_config.auto_refresh_interval = update_request.auto_refresh_interval
            
            if update_request.enable_notifications is not None:
                current_config.enable_notifications = update_request.enable_notifications
            
            if update_request.max_students_per_page is not None:
                current_config.max_students_per_page = update_request.max_students_per_page
            
            # Lưu cấu hình mới
            if self.save_config(current_config):
                return current_config
            else:
                return None
                
        except Exception as e:
            print(f"Lỗi khi cập nhật cấu hình: {e}")
            return None
    
    def get_risk_thresholds(self) -> RiskThresholdConfig:
        """Lấy ngưỡng rủi ro hiện tại"""
        config = self.get_config()
        return config.risk_thresholds
    
    def reset_to_default(self) -> bool:
        """Reset về cấu hình mặc định"""
        default_config = self.get_default_config()
        return self.save_config(default_config) 