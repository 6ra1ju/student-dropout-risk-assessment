from dataclasses import dataclass
from typing import Dict


@dataclass
class RiskConfig:
    """Cấu hình cho hệ thống đánh giá rủi ro"""
    
    # Ngưỡng tỷ lệ đi học (mặc định: 75%)
    attendance_threshold: float = 0.75
    
    # Ngưỡng tỷ lệ nộp bài tập (mặc định: 50%)
    assignment_threshold: float = 0.50
    
    # Ngưỡng số lần liên lạc thất bại (mặc định: 2)
    contact_failed_threshold: int = 2
    
    # Mapping điểm số sang mức rủi ro
    score_mapping: Dict[str, str] = None
    
    def __post_init__(self):
        if self.score_mapping is None:
            self.score_mapping = {
                "0-1": "LOW",
                "2": "MEDIUM", 
                "3": "HIGH"
            }
    
    def get_risk_level(self, score: int) -> str:
        """Lấy mức rủi ro dựa trên điểm số"""
        if score <= 1:
            return self.score_mapping["0-1"]
        elif score == 2:
            return self.score_mapping["2"]
        else:
            return self.score_mapping["3"] 