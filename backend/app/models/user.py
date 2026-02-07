from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class GradeEnum(enum.Enum):
    """年级枚举"""
    GRADE_1 = 1
    GRADE_2 = 2
    GRADE_3 = 3
    GRADE_4 = 4
    GRADE_5 = 5
    GRADE_6 = 6


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    openid = Column(String(64), unique=True, index=True, nullable=False, comment="微信OpenID")
    nickname = Column(String(64), nullable=True, comment="昵称")
    avatar_url = Column(String(512), nullable=True, comment="头像URL")
    grade = Column(SQLEnum(GradeEnum), nullable=True, comment="年级")
    
    # 统计字段（冗余存储，提高查询效率）
    total_readings = Column(Integer, default=0, comment="累计阅读篇数")
    streak_days = Column(Integer, default=0, comment="当前连续打卡天数")
    max_streak_days = Column(Integer, default=0, comment="最长连续打卡天数")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    progresses = relationship("UserProgress", back_populates="user")
    check_ins = relationship("CheckIn", back_populates="user")
    badges = relationship("UserBadge", back_populates="user")
    abilities = relationship("UserAbility", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, nickname={self.nickname})>"
