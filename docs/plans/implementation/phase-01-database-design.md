# Phase 1: 数据库设计

> **预估工时**: 2-3 人天  
> **前置依赖**: Phase 0 (项目基础架构)  
> **产出物**: 完整的数据库模型、迁移脚本、初始数据

---

## 1.1 目标概述

本阶段完成数据库设计，包括：
- 实体关系设计 (ER 图)
- SQLAlchemy 数据模型定义
- Alembic 数据库迁移配置
- 初始数据（标签、勋章配置等）

---

## 1.2 实体关系图 (ER Diagram)

```
┌─────────────────┐       ┌─────────────────┐
│      User       │       │     Article     │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ openid          │       │ title           │
│ nickname        │       │ content         │
│ avatar_url      │       │ source_book     │
│ grade           │       │ source_chapter  │
│ created_at      │       │ word_count      │
│ updated_at      │       │ reading_time    │
└────────┬────────┘       │ article_diff    │
         │                │ status          │
         │                │ created_at      │
         │                │ updated_at      │
         │                └────────┬────────┘
         │                         │
         │    ┌────────────────────┼────────────────────┐
         │    │                    │                    │
         │    ▼                    ▼                    ▼
┌────────┴────────┐    ┌─────────────────┐    ┌─────────────────┐
│  UserProgress   │    │    Question     │    │  ArticleTag     │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ id (PK)         │    │ id (PK)         │    │ article_id (FK) │
│ user_id (FK)    │    │ article_id (FK) │    │ tag_id (FK)     │
│ article_id (FK) │    │ type            │    └─────────────────┘
│ score           │    │ content         │             │
│ time_spent      │    │ options         │             ▼
│ completed_at    │    │ answer          │    ┌─────────────────┐
└─────────────────┘    │ hint            │    │      Tag        │
         │             │ ability_dim     │    ├─────────────────┤
         │             │ difficulty      │    │ id (PK)         │
         ▼             │ created_at      │    │ name            │
┌─────────────────┐    └─────────────────┘    │ category        │
│  QuestionAnswer │             │             │ description     │
├─────────────────┤             │             └─────────────────┘
│ id (PK)         │             │
│ progress_id(FK) │             ▼
│ question_id(FK) │    ┌─────────────────┐
│ user_answer     │    │ QuestionAbility │
│ is_correct      │    ├─────────────────┤
│ created_at      │    │ question_id(FK) │
└─────────────────┘    │ ability_id (FK) │
                       └─────────────────┘
┌─────────────────┐             │
│   CheckIn       │             ▼
├─────────────────┤    ┌─────────────────┐
│ id (PK)         │    │ AbilityDimension│
│ user_id (FK)    │    ├─────────────────┤
│ check_date      │    │ id (PK)         │
│ created_at      │    │ name            │
└─────────────────┘    │ category        │
                       │ description     │
┌─────────────────┐    │ display_order   │
│   UserBadge     │    └─────────────────┘
├─────────────────┤
│ id (PK)         │    ┌─────────────────┐
│ user_id (FK)    │    │     Badge       │
│ badge_id (FK)   │    ├─────────────────┤
│ earned_at       │    │ id (PK)         │
└─────────────────┘    │ name            │
         │             │ description     │
         └────────────►│ icon_url        │
                       │ category        │
                       │ condition_type  │
                       │ condition_value │
                       └─────────────────┘
                       
┌─────────────────┐
│  UserAbility    │
├─────────────────┤
│ id (PK)         │
│ user_id (FK)    │
│ ability_id (FK) │
│ correct_count   │
│ total_count     │
│ score           │
│ updated_at      │
└─────────────────┘
```

---

## 1.3 数据模型详细定义

### 1.3.1 用户模型 (models/user.py)

```python
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
```

### 1.3.2 文章模型 (models/article.py)

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class ArticleStatusEnum(enum.Enum):
    """文章状态枚举"""
    DRAFT = "draft"           # 草稿
    PENDING = "pending"       # 待审核
    PUBLISHED = "published"   # 已发布
    ARCHIVED = "archived"     # 已归档


class DifficultyEnum(enum.Enum):
    """难度枚举"""
    EASY = 1      # ⭐
    MEDIUM = 2    # ⭐⭐
    HARD = 3      # ⭐⭐⭐


class Article(Base):
    """文章表"""
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True, comment="标题")
    content = Column(Text, nullable=False, comment="文章内容")
    
    # 来源信息
    source_book = Column(String(200), nullable=True, comment="来源书籍，如《伊索寓言》")
    source_chapter = Column(String(200), nullable=True, comment="来源章节")
    is_excerpt = Column(Boolean, default=False, comment="是否为节选")
    
    # 文章属性
    word_count = Column(Integer, nullable=False, comment="字数")
    reading_time = Column(Integer, nullable=False, comment="预计阅读时间(分钟)")
    article_difficulty = Column(SQLEnum(DifficultyEnum), default=DifficultyEnum.MEDIUM, comment="文章难度")
    
    # 状态
    status = Column(SQLEnum(ArticleStatusEnum), default=ArticleStatusEnum.DRAFT, index=True, comment="状态")
    
    # AI 导入标记
    is_ai_generated = Column(Boolean, default=False, comment="是否AI导入")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    created_by = Column(Integer, nullable=True, comment="创建者ID（管理员）")
    
    # 关系
    questions = relationship("Question", back_populates="article", cascade="all, delete-orphan")
    tags = relationship("ArticleTag", back_populates="article", cascade="all, delete-orphan")
    progresses = relationship("UserProgress", back_populates="article")
    
    def __repr__(self):
        return f"<Article(id={self.id}, title={self.title})>"


class ArticleTag(Base):
    """文章-标签关联表"""
    __tablename__ = "article_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    
    # 关系
    article = relationship("Article", back_populates="tags")
    tag = relationship("Tag", back_populates="article_tags")
    
    # 唯一约束
    __table_args__ = (
        UniqueConstraint('article_id', 'tag_id', name='uq_article_tag'),
    )
```

### 1.3.3 标签模型 (models/tag.py)

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class TagCategoryEnum(enum.Enum):
    """标签分类枚举"""
    GRADE = "grade"           # 年级适配
    GENRE = "genre"           # 文体类型
    SOURCE = "source"         # 来源系列
    THEME = "theme"           # 主题标签
    CULTURE = "culture"       # 文化来源
    ADAPTATION = "adaptation" # 改编程度


class Tag(Base):
    """标签表"""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, comment="标签名称")
    category = Column(SQLEnum(TagCategoryEnum), nullable=False, index=True, comment="标签分类")
    description = Column(String(200), nullable=True, comment="标签描述")
    display_order = Column(Integer, default=0, comment="显示顺序")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    # 关系
    article_tags = relationship("ArticleTag", back_populates="tag")
    
    # 唯一约束（同一分类下标签名唯一）
    __table_args__ = (
        UniqueConstraint('name', 'category', name='uq_tag_name_category'),
    )
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name}, category={self.category})>"
```

### 1.3.4 题目模型 (models/question.py)

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class QuestionTypeEnum(enum.Enum):
    """题目类型枚举"""
    CHOICE = "choice"       # 选择题
    JUDGE = "judge"         # 判断题
    FILL = "fill"           # 填空题
    SHORT_ANSWER = "short_answer"  # 简答题


class Question(Base):
    """题目表"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 题目内容
    type = Column(SQLEnum(QuestionTypeEnum), nullable=False, comment="题目类型")
    content = Column(Text, nullable=False, comment="题干内容")
    
    # 选择题选项（JSON格式）
    # 格式: ["选项A", "选项B", "选项C", "选项D"]
    options = Column(JSON, nullable=True, comment="选项（选择题）")
    
    # 答案
    # 选择题: "A" / "B" / "C" / "D"
    # 判断题: "true" / "false"
    # 填空题: "正确答案"
    # 简答题: "参考答案要点"（用于AI评分参考）
    answer = Column(Text, nullable=False, comment="正确答案")
    
    # 解析和提示
    explanation = Column(Text, nullable=True, comment="答案解析")
    hint = Column(String(500), nullable=True, comment="温柔提示")
    
    # 难度
    difficulty = Column(SQLEnum(DifficultyEnum), default=DifficultyEnum.MEDIUM, comment="题目难度")
    
    # 顺序
    display_order = Column(Integer, default=0, comment="题目顺序")
    
    # AI 生成标记
    is_ai_generated = Column(Boolean, default=False, comment="是否AI生成")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    article = relationship("Article", back_populates="questions")
    abilities = relationship("QuestionAbility", back_populates="question", cascade="all, delete-orphan")
    answers = relationship("QuestionAnswer", back_populates="question")
    
    def __repr__(self):
        return f"<Question(id={self.id}, type={self.type})>"


class QuestionAbility(Base):
    """题目-能力维度关联表"""
    __tablename__ = "question_abilities"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    ability_id = Column(Integer, ForeignKey("ability_dimensions.id", ondelete="CASCADE"), nullable=False)
    
    # 权重（一道题可能涉及多个能力，但主要考察某个能力）
    weight = Column(Integer, default=1, comment="权重 1-10")
    
    # 关系
    question = relationship("Question", back_populates="abilities")
    ability = relationship("AbilityDimension", back_populates="question_abilities")
    
    __table_args__ = (
        UniqueConstraint('question_id', 'ability_id', name='uq_question_ability'),
    )
```

### 1.3.5 能力维度模型 (models/ability.py)

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class AbilityCategoryEnum(enum.Enum):
    """能力分类枚举"""
    INFORMATION = "information"     # 信息获取能力
    COMPREHENSION = "comprehension" # 理解与概括能力
    ANALYSIS = "analysis"           # 分析与推理能力
    EXPRESSION = "expression"       # 评价与表达能力


class AbilityDimension(Base):
    """能力维度表"""
    __tablename__ = "ability_dimensions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, comment="能力名称")
    code = Column(String(30), unique=True, nullable=False, comment="能力编码，如 detail_extraction")
    category = Column(SQLEnum(AbilityCategoryEnum), nullable=False, comment="能力分类")
    description = Column(String(200), nullable=True, comment="能力描述")
    display_order = Column(Integer, default=0, comment="显示顺序")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    # 关系
    question_abilities = relationship("QuestionAbility", back_populates="ability")
    user_abilities = relationship("UserAbility", back_populates="ability")
    
    def __repr__(self):
        return f"<AbilityDimension(id={self.id}, name={self.name})>"
```

### 1.3.6 用户学习记录模型 (models/progress.py)

```python
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class UserProgress(Base):
    """用户阅读进度表"""
    __tablename__ = "user_progresses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 成绩
    score = Column(Integer, nullable=True, comment="得分（百分制）")
    correct_count = Column(Integer, default=0, comment="正确题数")
    total_count = Column(Integer, default=0, comment="总题数")
    
    # 用时
    time_spent = Column(Integer, nullable=True, comment="用时（秒）")
    
    # 状态
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="开始时间")
    
    # 关系
    user = relationship("User", back_populates="progresses")
    article = relationship("Article", back_populates="progresses")
    answers = relationship("QuestionAnswer", back_populates="progress", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<UserProgress(id={self.id}, user_id={self.user_id}, article_id={self.article_id})>"


class QuestionAnswer(Base):
    """用户答题记录表"""
    __tablename__ = "question_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    progress_id = Column(Integer, ForeignKey("user_progresses.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 用户答案
    user_answer = Column(Text, nullable=True, comment="用户答案")
    is_correct = Column(Boolean, nullable=True, comment="是否正确")
    
    # 简答题 AI 评分（可选）
    ai_score = Column(Integer, nullable=True, comment="AI评分（0-100）")
    ai_feedback = Column(Text, nullable=True, comment="AI反馈")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="答题时间")
    
    # 关系
    progress = relationship("UserProgress", back_populates="answers")
    question = relationship("Question", back_populates="answers")
    
    def __repr__(self):
        return f"<QuestionAnswer(id={self.id}, is_correct={self.is_correct})>"
```

### 1.3.7 打卡记录模型 (models/checkin.py)

```python
from datetime import datetime, date
from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class CheckIn(Base):
    """打卡记录表"""
    __tablename__ = "check_ins"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    check_date = Column(Date, nullable=False, index=True, comment="打卡日期")
    
    # 关联的阅读进度（打卡时完成的那篇文章）
    progress_id = Column(Integer, ForeignKey("user_progresses.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="打卡时间")
    
    # 关系
    user = relationship("User", back_populates="check_ins")
    
    # 同一用户同一天只能打卡一次
    __table_args__ = (
        UniqueConstraint('user_id', 'check_date', name='uq_user_check_date'),
    )
    
    def __repr__(self):
        return f"<CheckIn(id={self.id}, user_id={self.user_id}, date={self.check_date})>"
```

### 1.3.8 勋章模型 (models/badge.py)

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class BadgeCategoryEnum(enum.Enum):
    """勋章分类枚举"""
    PERSISTENCE = "persistence"  # 坚持类
    ABILITY = "ability"          # 能力类
    READING = "reading"          # 阅读量类
    EXPLORE = "explore"          # 探索类


class BadgeConditionTypeEnum(enum.Enum):
    """勋章获取条件类型"""
    FIRST_READING = "first_reading"       # 首次阅读
    STREAK_DAYS = "streak_days"           # 连续打卡天数
    TOTAL_READINGS = "total_readings"     # 累计阅读篇数
    ABILITY_ACCURACY = "ability_accuracy" # 某能力正确率
    ABILITY_COUNT = "ability_count"       # 某能力题目累计正确数
    GENRE_COUNT = "genre_count"           # 某文体阅读数量
    ALL_GENRES = "all_genres"             # 阅读所有文体


class Badge(Base):
    """勋章表"""
    __tablename__ = "badges"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, comment="勋章名称")
    description = Column(String(200), nullable=True, comment="勋章描述")
    icon_url = Column(String(512), nullable=True, comment="勋章图标URL")
    
    category = Column(SQLEnum(BadgeCategoryEnum), nullable=False, comment="勋章分类")
    
    # 获取条件
    condition_type = Column(SQLEnum(BadgeConditionTypeEnum), nullable=False, comment="条件类型")
    condition_value = Column(Integer, nullable=False, comment="条件阈值")
    condition_extra = Column(String(100), nullable=True, comment="额外条件参数，如能力ID或文体名")
    
    # 显示顺序
    display_order = Column(Integer, default=0, comment="显示顺序")
    
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    # 关系
    user_badges = relationship("UserBadge", back_populates="badge")
    
    def __repr__(self):
        return f"<Badge(id={self.id}, name={self.name})>"


class UserBadge(Base):
    """用户勋章表"""
    __tablename__ = "user_badges"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    badge_id = Column(Integer, ForeignKey("badges.id", ondelete="CASCADE"), nullable=False, index=True)
    
    earned_at = Column(DateTime, default=datetime.utcnow, comment="获得时间")
    
    # 关系
    user = relationship("User", back_populates="badges")
    badge = relationship("Badge", back_populates="user_badges")
    
    # 同一用户同一勋章只能获得一次
    __table_args__ = (
        UniqueConstraint('user_id', 'badge_id', name='uq_user_badge'),
    )
    
    def __repr__(self):
        return f"<UserBadge(id={self.id}, user_id={self.user_id}, badge_id={self.badge_id})>"
```

### 1.3.9 用户能力统计模型 (models/user_ability.py)

```python
from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class UserAbility(Base):
    """用户能力统计表"""
    __tablename__ = "user_abilities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    ability_id = Column(Integer, ForeignKey("ability_dimensions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 统计数据
    correct_count = Column(Integer, default=0, comment="正确题数")
    total_count = Column(Integer, default=0, comment="总题数")
    
    # 计算得分（正确率 * 100）
    score = Column(Float, default=0, comment="能力得分（0-100）")
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关系
    user = relationship("User", back_populates="abilities")
    ability = relationship("AbilityDimension", back_populates="user_abilities")
    
    # 同一用户同一能力只有一条记录
    __table_args__ = (
        UniqueConstraint('user_id', 'ability_id', name='uq_user_ability'),
    )
    
    def __repr__(self):
        return f"<UserAbility(user_id={self.user_id}, ability_id={self.ability_id}, score={self.score})>"
```

---

## 1.4 数据库连接配置 (database.py)

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # 开发环境打印SQL
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# 创建异步 Session
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 声明基类
Base = declarative_base()


async def get_db():
    """获取数据库会话的依赖"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """初始化数据库（创建所有表）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

---

## 1.5 Alembic 数据库迁移配置

### 1.5.1 初始化 Alembic

```bash
cd backend
alembic init alembic
```

### 1.5.2 修改 alembic.ini

```ini
# 修改 sqlalchemy.url 为占位符，实际值从环境变量读取
sqlalchemy.url = driver://user:pass@localhost/dbname
```

### 1.5.3 修改 alembic/env.py

```python
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from app.config import settings
from app.database import Base
# 导入所有模型
from app.models import user, article, tag, question, ability, progress, checkin, badge, user_ability

config = context.config

# 设置数据库 URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("+asyncpg", ""))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """离线模式运行迁移"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """在线模式运行迁移"""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

### 1.5.4 创建初始迁移

```bash
# 生成迁移文件
alembic revision --autogenerate -m "initial tables"

# 执行迁移
alembic upgrade head
```

---

## 1.6 初始数据脚本

### 1.6.1 创建初始数据脚本 (scripts/init_data.py)

```python
"""
初始化基础数据
运行方式: python -m scripts.init_data
"""
import asyncio
from app.database import AsyncSessionLocal
from app.models.tag import Tag, TagCategoryEnum
from app.models.ability import AbilityDimension, AbilityCategoryEnum
from app.models.badge import Badge, BadgeCategoryEnum, BadgeConditionTypeEnum


async def init_tags():
    """初始化标签数据"""
    tags = [
        # 年级
        {"name": "1年级", "category": TagCategoryEnum.GRADE, "display_order": 1},
        {"name": "2年级", "category": TagCategoryEnum.GRADE, "display_order": 2},
        {"name": "3年级", "category": TagCategoryEnum.GRADE, "display_order": 3},
        {"name": "4年级", "category": TagCategoryEnum.GRADE, "display_order": 4},
        {"name": "5年级", "category": TagCategoryEnum.GRADE, "display_order": 5},
        {"name": "6年级", "category": TagCategoryEnum.GRADE, "display_order": 6},
        
        # 文体类型
        {"name": "童话", "category": TagCategoryEnum.GENRE, "display_order": 1},
        {"name": "寓言", "category": TagCategoryEnum.GENRE, "display_order": 2},
        {"name": "科普", "category": TagCategoryEnum.GENRE, "display_order": 3},
        {"name": "散文", "category": TagCategoryEnum.GENRE, "display_order": 4},
        {"name": "古诗词", "category": TagCategoryEnum.GENRE, "display_order": 5},
        {"name": "文言文", "category": TagCategoryEnum.GENRE, "display_order": 6},
        {"name": "神话传说", "category": TagCategoryEnum.GENRE, "display_order": 7},
        {"name": "历史故事", "category": TagCategoryEnum.GENRE, "display_order": 8},
        
        # 来源系列
        {"name": "伊索寓言", "category": TagCategoryEnum.SOURCE, "display_order": 1},
        {"name": "安徒生童话", "category": TagCategoryEnum.SOURCE, "display_order": 2},
        {"name": "格林童话", "category": TagCategoryEnum.SOURCE, "display_order": 3},
        {"name": "中国神话", "category": TagCategoryEnum.SOURCE, "display_order": 4},
        {"name": "唐诗三百首", "category": TagCategoryEnum.SOURCE, "display_order": 5},
        {"name": "宋词精选", "category": TagCategoryEnum.SOURCE, "display_order": 6},
        {"name": "成语故事", "category": TagCategoryEnum.SOURCE, "display_order": 7},
        
        # 主题标签
        {"name": "勇气", "category": TagCategoryEnum.THEME, "display_order": 1},
        {"name": "友谊", "category": TagCategoryEnum.THEME, "display_order": 2},
        {"name": "诚实", "category": TagCategoryEnum.THEME, "display_order": 3},
        {"name": "善良", "category": TagCategoryEnum.THEME, "display_order": 4},
        {"name": "智慧", "category": TagCategoryEnum.THEME, "display_order": 5},
        {"name": "自然", "category": TagCategoryEnum.THEME, "display_order": 6},
        {"name": "科学", "category": TagCategoryEnum.THEME, "display_order": 7},
        {"name": "亲情", "category": TagCategoryEnum.THEME, "display_order": 8},
        
        # 文化来源
        {"name": "中国传统", "category": TagCategoryEnum.CULTURE, "display_order": 1},
        {"name": "西方经典", "category": TagCategoryEnum.CULTURE, "display_order": 2},
        {"name": "日本故事", "category": TagCategoryEnum.CULTURE, "display_order": 3},
        {"name": "印度寓言", "category": TagCategoryEnum.CULTURE, "display_order": 4},
        
        # 改编程度
        {"name": "原文", "category": TagCategoryEnum.ADAPTATION, "display_order": 1},
        {"name": "简化版", "category": TagCategoryEnum.ADAPTATION, "display_order": 2},
        {"name": "白话改编", "category": TagCategoryEnum.ADAPTATION, "display_order": 3},
    ]
    
    async with AsyncSessionLocal() as session:
        for tag_data in tags:
            tag = Tag(**tag_data)
            session.add(tag)
        await session.commit()
        print(f"✓ 创建了 {len(tags)} 个标签")


async def init_abilities():
    """初始化能力维度数据"""
    abilities = [
        # 信息获取能力
        {
            "name": "细节提取",
            "code": "detail_extraction",
            "category": AbilityCategoryEnum.INFORMATION,
            "description": "找到文中明确写出的具体信息",
            "display_order": 1
        },
        {
            "name": "关键信息定位",
            "code": "key_info_location",
            "category": AbilityCategoryEnum.INFORMATION,
            "description": "定位时间、地点、人物等关键要素",
            "display_order": 2
        },
        
        # 理解与概括能力
        {
            "name": "主旨概括",
            "code": "main_idea",
            "category": AbilityCategoryEnum.COMPREHENSION,
            "description": "归纳文章中心思想、主要内容",
            "display_order": 3
        },
        {
            "name": "词语理解",
            "code": "vocabulary",
            "category": AbilityCategoryEnum.COMPREHENSION,
            "description": "结合语境理解词语含义",
            "display_order": 4
        },
        {
            "name": "段落大意",
            "code": "paragraph_summary",
            "category": AbilityCategoryEnum.COMPREHENSION,
            "description": "理解段落主要内容及段落间关系",
            "display_order": 5
        },
        
        # 分析与推理能力
        {
            "name": "人物分析",
            "code": "character_analysis",
            "category": AbilityCategoryEnum.ANALYSIS,
            "description": "分析人物性格、特点、动机",
            "display_order": 6
        },
        {
            "name": "情感理解",
            "code": "emotion_understanding",
            "category": AbilityCategoryEnum.ANALYSIS,
            "description": "体会人物情感变化、作者情感态度",
            "display_order": 7
        },
        {
            "name": "逻辑推理",
            "code": "logical_inference",
            "category": AbilityCategoryEnum.ANALYSIS,
            "description": "根据已知信息推断隐含意思",
            "display_order": 8
        },
        {
            "name": "因果关系",
            "code": "cause_effect",
            "category": AbilityCategoryEnum.ANALYSIS,
            "description": "理解事件之间的因果逻辑",
            "display_order": 9
        },
        
        # 评价与表达能力
        {
            "name": "观点表达",
            "code": "opinion_expression",
            "category": AbilityCategoryEnum.EXPRESSION,
            "description": "发表个人看法、评价人物或事件",
            "display_order": 10
        },
    ]
    
    async with AsyncSessionLocal() as session:
        for ability_data in abilities:
            ability = AbilityDimension(**ability_data)
            session.add(ability)
        await session.commit()
        print(f"✓ 创建了 {len(abilities)} 个能力维度")


async def init_badges():
    """初始化勋章数据"""
    badges = [
        # 坚持类
        {
            "name": "阅读新星",
            "description": "首次完成阅读",
            "category": BadgeCategoryEnum.PERSISTENCE,
            "condition_type": BadgeConditionTypeEnum.FIRST_READING,
            "condition_value": 1,
            "display_order": 1
        },
        {
            "name": "三日小达人",
            "description": "连续打卡3天",
            "category": BadgeCategoryEnum.PERSISTENCE,
            "condition_type": BadgeConditionTypeEnum.STREAK_DAYS,
            "condition_value": 3,
            "display_order": 2
        },
        {
            "name": "周冠军",
            "description": "连续打卡7天",
            "category": BadgeCategoryEnum.PERSISTENCE,
            "condition_type": BadgeConditionTypeEnum.STREAK_DAYS,
            "condition_value": 7,
            "display_order": 3
        },
        {
            "name": "月度之星",
            "description": "连续打卡30天",
            "category": BadgeCategoryEnum.PERSISTENCE,
            "condition_type": BadgeConditionTypeEnum.STREAK_DAYS,
            "condition_value": 30,
            "display_order": 4
        },
        
        # 阅读量类
        {
            "name": "小书虫",
            "description": "累计阅读10篇",
            "category": BadgeCategoryEnum.READING,
            "condition_type": BadgeConditionTypeEnum.TOTAL_READINGS,
            "condition_value": 10,
            "display_order": 10
        },
        {
            "name": "博学多才",
            "description": "累计阅读50篇",
            "category": BadgeCategoryEnum.READING,
            "condition_type": BadgeConditionTypeEnum.TOTAL_READINGS,
            "condition_value": 50,
            "display_order": 11
        },
        {
            "name": "阅读狂人",
            "description": "累计阅读100篇",
            "category": BadgeCategoryEnum.READING,
            "condition_type": BadgeConditionTypeEnum.TOTAL_READINGS,
            "condition_value": 100,
            "display_order": 12
        },
        
        # 能力类
        {
            "name": "细节大师",
            "description": "细节提取正确率达90%",
            "category": BadgeCategoryEnum.ABILITY,
            "condition_type": BadgeConditionTypeEnum.ABILITY_ACCURACY,
            "condition_value": 90,
            "condition_extra": "detail_extraction",
            "display_order": 20
        },
        {
            "name": "推理达人",
            "description": "逻辑推理题累计答对20题",
            "category": BadgeCategoryEnum.ABILITY,
            "condition_type": BadgeConditionTypeEnum.ABILITY_COUNT,
            "condition_value": 20,
            "condition_extra": "logical_inference",
            "display_order": 21
        },
        {
            "name": "表达之星",
            "description": "完成10道简答题",
            "category": BadgeCategoryEnum.ABILITY,
            "condition_type": BadgeConditionTypeEnum.ABILITY_COUNT,
            "condition_value": 10,
            "condition_extra": "opinion_expression",
            "display_order": 22
        },
        
        # 探索类
        {
            "name": "童话爱好者",
            "description": "阅读10篇童话",
            "category": BadgeCategoryEnum.EXPLORE,
            "condition_type": BadgeConditionTypeEnum.GENRE_COUNT,
            "condition_value": 10,
            "condition_extra": "童话",
            "display_order": 30
        },
        {
            "name": "诗词达人",
            "description": "阅读10篇古诗词",
            "category": BadgeCategoryEnum.EXPLORE,
            "condition_type": BadgeConditionTypeEnum.GENRE_COUNT,
            "condition_value": 10,
            "condition_extra": "古诗词",
            "display_order": 31
        },
        {
            "name": "全能选手",
            "description": "阅读过所有文体",
            "category": BadgeCategoryEnum.EXPLORE,
            "condition_type": BadgeConditionTypeEnum.ALL_GENRES,
            "condition_value": 1,
            "display_order": 32
        },
    ]
    
    async with AsyncSessionLocal() as session:
        for badge_data in badges:
            badge = Badge(**badge_data)
            session.add(badge)
        await session.commit()
        print(f"✓ 创建了 {len(badges)} 个勋章")


async def main():
    """执行所有初始化"""
    print("开始初始化数据...")
    await init_tags()
    await init_abilities()
    await init_badges()
    print("✓ 所有基础数据初始化完成！")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 1.7 验收标准

### 1.7.1 数据模型验收

- [ ] 所有模型文件创建完成，无语法错误
- [ ] 模型之间的关系（ForeignKey, relationship）正确定义
- [ ] 枚举类型定义完整
- [ ] 字段注释清晰

### 1.7.2 数据库验收

- [ ] Alembic 迁移文件生成成功
- [ ] 执行 `alembic upgrade head` 无错误
- [ ] 数据库中创建了所有表
- [ ] 表结构与设计一致（字段类型、索引、约束）

### 1.7.3 初始数据验收

- [ ] 运行初始化脚本无错误
- [ ] 标签数据创建成功（验证数量）
- [ ] 能力维度数据创建成功（10个）
- [ ] 勋章数据创建成功（验证数量）

---

## 1.8 单元测试

### 1.8.1 测试文件 (app/tests/test_models.py)

```python
import pytest
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User, GradeEnum
from app.models.article import Article, ArticleStatusEnum, DifficultyEnum
from app.models.tag import Tag, TagCategoryEnum
from app.models.question import Question, QuestionTypeEnum
from app.models.ability import AbilityDimension, AbilityCategoryEnum


@pytest.mark.asyncio
async def test_create_user():
    """测试创建用户"""
    async with AsyncSessionLocal() as session:
        user = User(
            openid="test_openid_123",
            nickname="测试用户",
            grade=GradeEnum.GRADE_3
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        assert user.id is not None
        assert user.openid == "test_openid_123"
        assert user.grade == GradeEnum.GRADE_3
        assert user.total_readings == 0
        
        # 清理
        await session.delete(user)
        await session.commit()


@pytest.mark.asyncio
async def test_create_article_with_questions():
    """测试创建文章及其题目"""
    async with AsyncSessionLocal() as session:
        # 创建文章
        article = Article(
            title="测试文章",
            content="这是测试内容。" * 50,
            word_count=300,
            reading_time=3,
            article_difficulty=DifficultyEnum.EASY,
            status=ArticleStatusEnum.PUBLISHED
        )
        session.add(article)
        await session.commit()
        await session.refresh(article)
        
        # 创建题目
        question = Question(
            article_id=article.id,
            type=QuestionTypeEnum.CHOICE,
            content="这是一道测试题？",
            options=["选项A", "选项B", "选项C", "选项D"],
            answer="A",
            difficulty=DifficultyEnum.EASY
        )
        session.add(question)
        await session.commit()
        
        # 验证关系
        await session.refresh(article)
        assert len(article.questions) == 1
        assert article.questions[0].content == "这是一道测试题？"
        
        # 清理
        await session.delete(article)  # 级联删除题目
        await session.commit()


@pytest.mark.asyncio
async def test_tag_categories():
    """测试标签分类"""
    async with AsyncSessionLocal() as session:
        # 查询年级标签
        result = await session.execute(
            select(Tag).where(Tag.category == TagCategoryEnum.GRADE)
        )
        grade_tags = result.scalars().all()
        
        assert len(grade_tags) == 6  # 1-6年级


@pytest.mark.asyncio
async def test_ability_dimensions():
    """测试能力维度"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(AbilityDimension))
        abilities = result.scalars().all()
        
        assert len(abilities) == 10
        
        # 验证分类
        categories = {a.category for a in abilities}
        assert AbilityCategoryEnum.INFORMATION in categories
        assert AbilityCategoryEnum.COMPREHENSION in categories
        assert AbilityCategoryEnum.ANALYSIS in categories
        assert AbilityCategoryEnum.EXPRESSION in categories
```

### 1.8.2 运行测试

```bash
cd backend
source venv/bin/activate

# 运行数据库相关测试
pytest app/tests/test_models.py -v

# 运行全部测试并生成覆盖率报告
pytest --cov=app/models --cov-report=html
```

---

## 1.9 交付物清单

| 交付物 | 文件路径 | 验收标准 |
|--------|----------|----------|
| 用户模型 | `app/models/user.py` | 包含 User 类 |
| 文章模型 | `app/models/article.py` | 包含 Article, ArticleTag 类 |
| 标签模型 | `app/models/tag.py` | 包含 Tag 类 |
| 题目模型 | `app/models/question.py` | 包含 Question, QuestionAbility 类 |
| 能力维度模型 | `app/models/ability.py` | 包含 AbilityDimension 类 |
| 学习记录模型 | `app/models/progress.py` | 包含 UserProgress, QuestionAnswer 类 |
| 打卡模型 | `app/models/checkin.py` | 包含 CheckIn 类 |
| 勋章模型 | `app/models/badge.py` | 包含 Badge, UserBadge 类 |
| 用户能力模型 | `app/models/user_ability.py` | 包含 UserAbility 类 |
| 数据库配置 | `app/database.py` | 异步会话配置 |
| Alembic 配置 | `alembic/env.py` | 支持异步迁移 |
| 初始迁移 | `alembic/versions/xxx_initial.py` | 创建所有表 |
| 初始数据脚本 | `scripts/init_data.py` | 标签/能力/勋章数据 |
| 单元测试 | `app/tests/test_models.py` | 模型 CRUD 测试 |
