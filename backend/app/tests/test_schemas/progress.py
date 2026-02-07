import pytest
from datetime import datetime
from app.schemas.progress import (
    StartReadingRequest,
    StartReadingResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    CompleteReadingRequest,
    AbilityScoreItem,
    BadgeUnlock,
    CompleteReadingResponse,
    ProgressDetail,
    AnswerDetail,
    ProgressWithAnswers,
    HistoryItem,
    HistoryResponse
)


def test_start_reading_request():
    """StartReadingRequest should validate correctly"""
    request = StartReadingRequest(article_id=1)
    assert request.article_id == 1


def test_start_reading_response():
    """StartReadingResponse should serialize correctly"""
    response = StartReadingResponse(
        progress_id=1,
        article_id=1,
        article_title="测试文章",
        question_count=5
    )
    assert response.progress_id == 1
    assert response.article_id == 1
    assert response.article_title == "测试文章"
    assert response.question_count == 5


def test_submit_answer_request():
    """SubmitAnswerRequest should validate correctly"""
    request = SubmitAnswerRequest(
        question_id=1,
        user_answer="A"
    )
    assert request.question_id == 1
    assert request.user_answer == "A"


def test_submit_answer_response():
    """SubmitAnswerResponse should serialize correctly"""
    response = SubmitAnswerResponse(
        question_id=1,
        is_correct=True,
        correct_answer="A",
        explanation="这是正确答案",
        ability_names=["细节提取", "推理判断"]
    )
    assert response.question_id == 1
    assert response.is_correct == True
    assert response.correct_answer == "A"
    assert response.explanation == "这是正确答案"
    assert response.ability_names == ["细节提取", "推理判断"]


def test_submit_answer_response_minimal():
    """SubmitAnswerResponse should work without optional fields"""
    response = SubmitAnswerResponse(
        question_id=1,
        is_correct=False,
        correct_answer="B"
    )
    assert response.question_id == 1
    assert response.is_correct == False
    assert response.correct_answer == "B"
    assert response.explanation is None
    assert response.ability_names == []


def test_complete_reading_request_valid():
    """CompleteReadingRequest should validate positive time_spent"""
    request = CompleteReadingRequest(time_spent=180)
    assert request.time_spent == 180


def test_complete_reading_request_zero():
    """CompleteReadingRequest should allow time_spent=0"""
    request = CompleteReadingRequest(time_spent=0)
    assert request.time_spent == 0


def test_complete_reading_request_negative():
    """CompleteReadingRequest should reject negative time_spent"""
    with pytest.raises(ValueError):
        CompleteReadingRequest(time_spent=-1)


def test_ability_score_item():
    """AbilityScoreItem should serialize correctly"""
    item = AbilityScoreItem(
        ability_id=1,
        ability_name="细节提取",
        correct_count=8,
        total_count=10,
        score=80.0
    )
    assert item.ability_id == 1
    assert item.ability_name == "细节提取"
    assert item.correct_count == 8
    assert item.total_count == 10
    assert item.score == 80.0


def test_badge_unlock():
    """BadgeUnlock should serialize correctly"""
    badge = BadgeUnlock(
        id=1,
        name="阅读新星",
        description="完成第一次阅读"
    )
    assert badge.id == 1
    assert badge.name == "阅读新星"
    assert badge.description == "完成第一次阅读"
    assert badge.icon_url is None


def test_badge_unlock_with_icon():
    """BadgeUnlock should work with icon_url"""
    badge = BadgeUnlock(
        id=1,
        name="阅读新星",
        description="完成第一次阅读",
        icon_url="https://example.com/badge.png"
    )
    assert badge.icon_url == "https://example.com/badge.png"


def test_complete_reading_response():
    """CompleteReadingResponse should serialize correctly"""
    response = CompleteReadingResponse(
        progress_id=1,
        score=80,
        correct_count=8,
        total_count=10,
        time_spent=300,
        ability_scores=[
            AbilityScoreItem(
                ability_id=1,
                ability_name="细节提取",
                correct_count=5,
                total_count=6,
                score=83.3
            )
        ],
        is_checked_in=True,
        streak_days=3,
        new_badges=[
            BadgeUnlock(
                id=1,
                name="阅读新星",
                description="完成第一次阅读"
            )
        ]
    )
    assert response.progress_id == 1
    assert response.score == 80
    assert response.correct_count == 8
    assert response.total_count == 10
    assert response.time_spent == 300
    assert len(response.ability_scores) == 1
    assert response.ability_scores[0].ability_name == "细节提取"
    assert response.is_checked_in == True
    assert response.streak_days == 3
    assert len(response.new_badges) == 1
    assert response.new_badges[0].name == "阅读新星"


def test_progress_detail():
    """ProgressDetail should serialize correctly"""
    now = datetime.utcnow()
    detail = ProgressDetail(
        id=1,
        article_id=1,
        article_title="测试文章",
        score=80,
        correct_count=8,
        total_count=10,
        time_spent=300,
        completed_at=now,
        created_at=now
    )
    assert detail.id == 1
    assert detail.article_id == 1
    assert detail.article_title == "测试文章"
    assert detail.score == 80
    assert detail.correct_count == 8
    assert detail.total_count == 10
    assert detail.time_spent == 300
    assert detail.completed_at == now
    assert detail.created_at == now


def test_progress_detail_incomplete():
    """ProgressDetail should work with None for incomplete progress"""
    now = datetime.utcnow()
    detail = ProgressDetail(
        id=1,
        article_id=1,
        article_title="测试文章",
        score=None,
        correct_count=0,
        total_count=10,
        time_spent=None,
        completed_at=None,
        created_at=now
    )
    assert detail.score is None
    assert detail.time_spent is None
    assert detail.completed_at is None


def test_answer_detail():
    """AnswerDetail should serialize correctly"""
    detail = AnswerDetail(
        question_id=1,
        question_content="测试题目",
        question_type="choice",
        user_answer="A",
        correct_answer="A",
        is_correct=True,
        explanation="正确答案"
    )
    assert detail.question_id == 1
    assert detail.question_content == "测试题目"
    assert detail.question_type == "choice"
    assert detail.user_answer == "A"
    assert detail.correct_answer == "A"
    assert detail.is_correct == True
    assert detail.explanation == "正确答案"


def test_answer_detail_no_answer():
    """AnswerDetail should work without user_answer"""
    detail = AnswerDetail(
        question_id=1,
        question_content="测试题目",
        question_type="choice",
        user_answer=None,
        correct_answer="A",
        is_correct=None,
        explanation=None
    )
    assert detail.user_answer is None
    assert detail.is_correct is None
    assert detail.explanation is None


def test_progress_with_answers():
    """ProgressWithAnswers should extend ProgressDetail with answers"""
    now = datetime.utcnow()
    progress = ProgressWithAnswers(
        id=1,
        article_id=1,
        article_title="测试文章",
        score=80,
        correct_count=8,
        total_count=10,
        time_spent=300,
        completed_at=now,
        created_at=now,
        answers=[
            AnswerDetail(
                question_id=1,
                question_content="题目1",
                question_type="choice",
                user_answer="A",
                correct_answer="A",
                is_correct=True,
                explanation="解析1"
            ),
            AnswerDetail(
                question_id=2,
                question_content="题目2",
                question_type="fill",
                user_answer="答案",
                correct_answer="答案",
                is_correct=True,
                explanation=None
            )
        ]
    )
    assert len(progress.answers) == 2
    assert progress.answers[0].question_id == 1
    assert progress.answers[1].question_id == 2
    assert "answers" in progress.model_fields


def test_progress_with_answers_empty():
    """ProgressWithAnswers should work with empty answers list"""
    now = datetime.utcnow()
    progress = ProgressWithAnswers(
        id=1,
        article_id=1,
        article_title="测试文章",
        score=80,
        correct_count=8,
        total_count=10,
        time_spent=300,
        completed_at=now,
        created_at=now,
        answers=[]
    )
    assert len(progress.answers) == 0


def test_history_item():
    """HistoryItem should serialize correctly"""
    now = datetime.utcnow()
    item = HistoryItem(
        id=1,
        article_id=1,
        article_title="测试文章",
        score=80,
        completed_at=now
    )
    assert item.id == 1
    assert item.article_id == 1
    assert item.article_title == "测试文章"
    assert item.score == 80
    assert item.completed_at == now


def test_history_item_incomplete():
    """HistoryItem should work with None for incomplete progress"""
    now = datetime.utcnow()
    item = HistoryItem(
        id=1,
        article_id=1,
        article_title="测试文章",
        score=None,
        completed_at=None
    )
    assert item.score is None
    assert item.completed_at is None


def test_history_response():
    """HistoryResponse should serialize correctly"""
    now = datetime.utcnow()
    response = HistoryResponse(
        items=[
            HistoryItem(
                id=1,
                article_id=1,
                article_title="文章1",
                score=80,
                completed_at=now
            ),
            HistoryItem(
                id=2,
                article_id=2,
                article_title="文章2",
                score=90,
                completed_at=now
            )
        ],
        total=2,
        page=1,
        page_size=20
    )
    assert len(response.items) == 2
    assert response.total == 2
    assert response.page == 1
    assert response.page_size == 20


def test_history_response_empty():
    """HistoryResponse should work with empty items"""
    response = HistoryResponse(
        items=[],
        total=0,
        page=1,
        page_size=20
    )
    assert len(response.items) == 0
    assert response.total == 0
