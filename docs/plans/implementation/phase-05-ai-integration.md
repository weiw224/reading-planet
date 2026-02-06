# Phase 5: AI 功能集成

> **预估工时**: 3-4 人天  
> **前置依赖**: Phase 2 (后端 API)  
> **产出物**: AI 内容生成、自动标签、题目生成功能

---

## 5.1 目标概述

本阶段完成 AI 功能集成，包括：
- AI 文章内容审核与优化
- AI 自动标签推荐
- AI 自动题目生成
- AI 简答题评分（可选）

---

## 5.2 AI 服务架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Admin Panel                            │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────┐ │
│  │ 导入文章 │  │ 自动标签 │  │ 生成题目 │  │ 内容审核/优化  │ │
│  └────┬────┘  └────┬────┘  └────┬────┘  └───────┬─────────┘ │
└───────┼───────────┼───────────┼────────────────┼───────────┘
        │           │           │                │
        ▼           ▼           ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend API                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    AI Service                         │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌───────────────┐ │  │
│  │  │ PromptBuilder│ │ AI Client   │  │ ResponseParser│ │  │
│  │  └─────────────┘  └─────────────┘  └───────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   SiliconFlow   │
                    │   Qwen3-8B API  │
                    └─────────────────┘
```

---

## 5.3 AI 服务实现 (services/ai_service.py)

```python
import json
import httpx
from typing import List, Dict, Optional, Tuple
from app.config import settings


class AIService:
    """AI 服务"""
    
    def __init__(self):
        self.api_url = settings.AI_API_URL
        self.api_key = settings.AI_API_KEY
        self.model = settings.AI_MODEL
        
    async def _call_api(self, messages: List[Dict], temperature: float = 0.7) -> str:
        """调用 AI API"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.api_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": 4096,
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def suggest_tags(self, title: str, content: str) -> Dict[str, List[str]]:
        """
        根据文章内容推荐标签
        
        返回: {
            "grade": ["3年级", "4年级"],
            "genre": ["童话"],
            "theme": ["勇气", "友谊"],
            "culture": ["西方经典"],
        }
        """
        prompt = f"""你是一个儿童阅读内容分类专家。请根据以下文章内容，推荐合适的标签。

文章标题: {title}

文章内容:
{content[:2000]}

请从以下维度推荐标签（每个维度可选1-3个最合适的）：

1. 年级适配（grade）: 1年级, 2年级, 3年级, 4年级, 5年级, 6年级
2. 文体类型（genre）: 童话, 寓言, 科普, 散文, 古诗词, 文言文, 神话传说, 历史故事
3. 主题标签（theme）: 勇气, 友谊, 诚实, 善良, 智慧, 自然, 科学, 亲情
4. 文化来源（culture）: 中国传统, 西方经典, 日本故事, 印度寓言

请以 JSON 格式返回，例如:
{{
    "grade": ["3年级", "4年级"],
    "genre": ["童话"],
    "theme": ["勇气", "友谊"],
    "culture": ["西方经典"]
}}

只返回 JSON，不要其他内容。"""

        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = await self._call_api(messages, temperature=0.3)
            # 解析 JSON
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            return json.loads(response)
        except Exception as e:
            print(f"AI 标签推荐失败: {e}")
            return {}
    
    async def generate_questions(
        self, 
        title: str, 
        content: str, 
        difficulty: int = 2,
        count: int = 5
    ) -> List[Dict]:
        """
        根据文章内容自动生成题目
        
        返回题目列表，每个题目包含:
        - type: 题目类型 (choice/judge/fill/short_answer)
        - content: 题干
        - options: 选项（选择题）
        - answer: 正确答案
        - hint: 温柔提示
        - explanation: 答案解析
        - ability_codes: 涉及的能力维度代码列表
        """
        difficulty_desc = {1: "简单", 2: "中等", 3: "较难"}[difficulty]
        
        prompt = f"""你是一个专业的儿童阅读理解题目设计专家。请根据以下文章内容，设计{count}道阅读理解题目。

文章标题: {title}

文章内容:
{content}

要求：
1. 难度级别: {difficulty_desc}
2. 题目数量: {count}道
3. 题目类型分布:
   - 选择题 (choice): 2-3道
   - 判断题 (judge): 1道
   - 填空题 (fill): 1道（如适用）
   - 简答题 (short_answer): 0-1道

4. 能力维度覆盖（从以下选择1-2个）:
   - detail_extraction: 细节提取
   - key_info_location: 关键信息定位
   - main_idea: 主旨概括
   - vocabulary: 词语理解
   - paragraph_summary: 段落大意
   - character_analysis: 人物分析
   - emotion_understanding: 情感理解
   - logical_inference: 逻辑推理
   - cause_effect: 因果关系
   - opinion_expression: 观点表达

5. 每道题必须包含"温柔提示"，引导学生思考而不直接给出答案

请以 JSON 数组格式返回，例如:
[
    {{
        "type": "choice",
        "content": "文中的小兔子为什么感到害怕？",
        "options": ["因为天黑了", "因为遇到了大灰狼", "因为迷路了", "因为下雨了"],
        "answer": "B",
        "hint": "再读一读第二段，看看小兔子遇到了谁？",
        "explanation": "文中第二段提到小兔子在森林里遇到了大灰狼，所以感到害怕。",
        "ability_codes": ["detail_extraction"]
    }},
    {{
        "type": "judge",
        "content": "小兔子最后成功回到了家。",
        "options": null,
        "answer": "true",
        "hint": "故事的结局是什么呢？",
        "explanation": "文章最后一段写道小兔子在小鸟的帮助下找到了回家的路。",
        "ability_codes": ["main_idea"]
    }}
]

只返回 JSON 数组，不要其他内容。"""

        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = await self._call_api(messages, temperature=0.5)
            # 解析 JSON
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            return json.loads(response)
        except Exception as e:
            print(f"AI 生成题目失败: {e}")
            return []
    
    async def review_content(self, content: str) -> Dict:
        """
        审核文章内容
        
        返回:
        - is_appropriate: 是否适合儿童阅读
        - issues: 问题列表
        - suggestions: 修改建议
        - improved_content: 优化后的内容（可选）
        """
        prompt = f"""你是一个儿童内容审核专家。请审核以下文章是否适合小学生（6-12岁）阅读。

文章内容:
{content}

请检查以下方面:
1. 是否包含暴力、恐怖内容
2. 是否包含不适当的语言
3. 是否包含复杂的成人话题
4. 是否存在价值观问题
5. 语言是否适合儿童理解

请以 JSON 格式返回:
{{
    "is_appropriate": true/false,
    "score": 1-10 (10分最适合儿童),
    "issues": ["问题1", "问题2"],
    "suggestions": ["建议1", "建议2"],
    "improved_content": "如果需要修改，提供修改后的内容，否则为null"
}}

只返回 JSON，不要其他内容。"""

        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = await self._call_api(messages, temperature=0.3)
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            return json.loads(response)
        except Exception as e:
            print(f"AI 内容审核失败: {e}")
            return {"is_appropriate": True, "issues": [], "suggestions": []}
    
    async def split_story_collection(self, content: str, source_book: str) -> List[Dict]:
        """
        将故事集自动拆分为独立故事
        
        返回故事列表:
        - title: 故事标题
        - content: 故事内容
        """
        prompt = f"""你是一个文本处理专家。请将以下故事集拆分为独立的故事。

来源: {source_book}

原文内容:
{content[:8000]}

请识别每个独立的故事，并提取标题和内容。

以 JSON 数组格式返回:
[
    {{
        "title": "故事标题1",
        "content": "故事内容1..."
    }},
    {{
        "title": "故事标题2",
        "content": "故事内容2..."
    }}
]

注意:
1. 保持原文内容，不要修改
2. 如果原文没有明确标题，根据内容推断一个合适的标题
3. 只返回 JSON 数组

只返回 JSON，不要其他内容。"""

        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = await self._call_api(messages, temperature=0.3)
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            return json.loads(response)
        except Exception as e:
            print(f"AI 拆分故事失败: {e}")
            return []
    
    async def extract_excerpt(
        self, 
        content: str, 
        target_length: int = 500,
        source_info: str = ""
    ) -> Dict:
        """
        从长文本中智能截取适合阅读的片段
        
        返回:
        - excerpt: 截取的内容
        - start_context: 上文概述
        - end_context: 下文概述（可选）
        """
        prompt = f"""你是一个文本编辑专家。请从以下长文本中截取一个适合小学生阅读的精彩片段。

来源: {source_info}

原文内容:
{content}

要求:
1. 截取长度约 {target_length} 字左右
2. 选择情节完整、有意义的段落
3. 避免截取在句子中间
4. 优先选择有教育意义或趣味性的片段

请以 JSON 格式返回:
{{
    "excerpt": "截取的内容...",
    "start_context": "本段之前的故事概述（一句话）",
    "selection_reason": "选择这段的原因"
}}

只返回 JSON，不要其他内容。"""

        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = await self._call_api(messages, temperature=0.5)
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            return json.loads(response)
        except Exception as e:
            print(f"AI 截取失败: {e}")
            return {"excerpt": content[:target_length], "start_context": ""}
    
    async def score_short_answer(
        self,
        question: str,
        reference_answer: str,
        user_answer: str
    ) -> Dict:
        """
        AI 评分简答题
        
        返回:
        - score: 得分 (0-100)
        - feedback: 评语
        - is_correct: 是否基本正确
        """
        prompt = f"""你是一个温和的阅读理解老师。请评价学生的简答题回答。

题目: {question}

参考答案要点: {reference_answer}

学生答案: {user_answer}

请给出评价:
1. 评分标准: 内容理解、表达完整性、语言组织
2. 评分范围: 0-100分
3. 给出鼓励性的评语

以 JSON 格式返回:
{{
    "score": 85,
    "is_correct": true,
    "feedback": "你理解得很好！答案抓住了主要内容。如果能再补充一下...就更完美了！"
}}

只返回 JSON，不要其他内容。"""

        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = await self._call_api(messages, temperature=0.3)
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            return json.loads(response)
        except Exception as e:
            print(f"AI 评分失败: {e}")
            return {"score": 60, "is_correct": True, "feedback": "回答已收到，继续加油！"}


ai_service = AIService()
```

---

## 5.4 AI 管理接口 (api/v1/admin/ai.py)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional

from app.database import get_db
from app.api.deps import get_admin_user
from app.schemas.common import ResponseModel
from app.services.ai_service import ai_service
from app.services.admin.article_service import admin_article_service
from app.services.admin.question_service import admin_question_service
from app.models.tag import Tag
from app.models.ability import AbilityDimension

router = APIRouter()


class SuggestTagsRequest(BaseModel):
    title: str
    content: str


class GenerateQuestionsRequest(BaseModel):
    article_id: int
    difficulty: int = 2
    count: int = 5


class ReviewContentRequest(BaseModel):
    content: str


class ImportStoriesRequest(BaseModel):
    content: str
    source_book: str


@router.post("/suggest-tags", response_model=ResponseModel)
async def suggest_tags(
    request: SuggestTagsRequest,
    admin: dict = Depends(get_admin_user)
):
    """
    AI 推荐标签
    
    根据文章标题和内容，自动推荐合适的标签
    """
    suggestions = await ai_service.suggest_tags(request.title, request.content)
    return ResponseModel(data=suggestions)


@router.post("/generate-questions", response_model=ResponseModel)
async def generate_questions(
    request: GenerateQuestionsRequest,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    """
    AI 生成题目
    
    根据文章内容自动生成阅读理解题目
    返回生成的题目列表（待管理员审核后保存）
    """
    # 获取文章内容
    article = await admin_article_service.get_article_detail(db, request.article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    questions = await ai_service.generate_questions(
        article.title,
        article.content,
        request.difficulty,
        request.count
    )
    
    return ResponseModel(data=questions)


@router.post("/review-content", response_model=ResponseModel)
async def review_content(
    request: ReviewContentRequest,
    admin: dict = Depends(get_admin_user)
):
    """
    AI 审核内容
    
    检查内容是否适合儿童阅读
    """
    result = await ai_service.review_content(request.content)
    return ResponseModel(data=result)


@router.post("/import-stories", response_model=ResponseModel)
async def import_stories(
    request: ImportStoriesRequest,
    admin: dict = Depends(get_admin_user)
):
    """
    AI 拆分故事集
    
    将故事集自动拆分为独立故事
    """
    stories = await ai_service.split_story_collection(
        request.content,
        request.source_book
    )
    return ResponseModel(data=stories)


@router.post("/save-generated-questions", response_model=ResponseModel)
async def save_generated_questions(
    article_id: int,
    questions: List[dict],
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_admin_user)
):
    """
    保存 AI 生成的题目
    
    管理员审核后，批量保存题目到数据库
    """
    from sqlalchemy import select
    from app.schemas.admin.question import QuestionCreateRequest, AbilityWeight
    
    saved_count = 0
    
    for i, q in enumerate(questions):
        # 查找能力维度 ID
        ability_weights = []
        for code in q.get("ability_codes", []):
            ability_result = await db.execute(
                select(AbilityDimension).where(AbilityDimension.code == code)
            )
            ability = ability_result.scalar_one_or_none()
            if ability:
                ability_weights.append(AbilityWeight(ability_id=ability.id, weight=1))
        
        # 创建题目
        try:
            question_data = QuestionCreateRequest(
                article_id=article_id,
                type=q["type"],
                content=q["content"],
                options=q.get("options"),
                answer=q["answer"],
                hint=q.get("hint"),
                explanation=q.get("explanation"),
                difficulty=2,  # 默认中等难度
                display_order=i,
                abilities=ability_weights
            )
            
            await admin_question_service.create_question(db, question_data)
            saved_count += 1
        except Exception as e:
            print(f"保存题目失败: {e}")
            continue
    
    return ResponseModel(data={"saved_count": saved_count})
```

---

## 5.5 验收标准

### AI 功能验收

- [ ] AI 标签推荐返回合理的标签建议
- [ ] AI 题目生成质量符合预期
  - 题目清晰、答案正确
  - 能力维度标注准确
  - 温柔提示有引导性
- [ ] AI 内容审核能识别不适当内容
- [ ] AI 故事拆分能正确分割故事集
- [ ] AI 简答题评分给出合理分数和评语

### 集成验收

- [ ] 管理后台可以调用 AI 推荐标签
- [ ] 管理后台可以一键生成题目
- [ ] 生成的题目可以编辑后保存
- [ ] API 调用有超时和重试机制

---

## 5.6 交付物清单

| 交付物 | 文件路径 | 验收标准 |
|--------|----------|----------|
| AI 服务 | `app/services/ai_service.py` | 所有方法实现 |
| AI 接口 | `app/api/v1/admin/ai.py` | 5个接口可用 |
| 前端集成 | `admin/src/views/articles/ArticleEdit.vue` | AI 按钮可用 |
