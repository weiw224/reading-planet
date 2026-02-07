import pytest
from datetime import datetime, date, timedelta
from sqlalchemy import select
from app.services.progress_service import ProgressService
from app.models.user import User
from app.models.article import Article, ArticleStatusEnum, DifficultyEnum
from app.models.question import Question, QuestionTypeEnum, QuestionAbility
from app.models.ability import AbilityDimension, AbilityCategoryEnum
from app.models.progress import UserProgress, QuestionAnswer
from app.models.badge import Badge, BadgeConditionTypeEnum, BadgeCategoryEnum
from app.models.user_ability import UserAbility
from app.schemas.progress import (
    StartReadingResponse,
    SubmitAnswerResponse,
    CompleteReadingResponse,
    AbilityScoreItem,
    BadgeUnlock,
    ProgressWithAnswers,
    HistoryItem
)


@pytest.mark.asyncio
async def test_start_reading_success(db_session):
    """Should create progress record when starting reading"""
    user = User(openid="test_user")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    article = Article(
        title="测试文章",
        content="内容",
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.EASY
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)

    question = Question(
        article_id=article.id,
        type=QuestionTypeEnum.CHOICE,
        difficulty=DifficultyEnum.EASY,
        content="测试问题",
        options='{"A": "A", "B": "B"}',
        answer="A"
    )
    db_session.add(question)
    await db_session.commit()

    result = await ProgressService.start_reading(db_session, user.id, article.id)

    assert isinstance(result, StartReadingResponse)
    assert result.progress_id > 0
    assert result.article_id == article.id
    assert result.article_title == "测试文章"
    assert result.question_count == 1

    progress = await db_session.execute(
        select(UserProgress).where(UserProgress.user_id == user.id)
    )
    progress = progress.scalar_one_or_none()
    assert progress is not None
    assert progress.article_id == article.id


@pytest.mark.asyncio
async def test_start_reading_article_not_found(db_session):
    """Should raise error when article doesn't exist"""
    user = User(openid="test_user")
    db_session.add(user)
    await db_session.commit()

    with pytest.raises(ValueError, match="文章不存在"):
        await ProgressService.start_reading(db_session, user.id, 999)


@pytest.mark.asyncio
async def test_submit_answer_correct(db_session):
    """Should submit correct answer and update progress"""
    user = User(openid="test_user")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    article = Article(
        title="测试文章",
        content="内容",
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.EASY
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)

    ability = AbilityDimension(name="细节提取", code="detail", category=AbilityCategoryEnum.INFORMATION)
    db_session.add(ability)
    await db_session.commit()
    await db_session.refresh(ability)

    question = Question(
        article_id=article.id,
        type=QuestionTypeEnum.CHOICE,
        difficulty=DifficultyEnum.EASY,
        content="测试问题",
        options='{"A": "A", "B": "B"}',
        answer="A",
        explanation="解释"
    )
    db_session.add(question)
    await db_session.commit()
    await db_session.refresh(question)

    progress = UserProgress(user_id=user.id, article_id=article.id, total_count=1)
    db_session.add(progress)
    await db_session.commit()
    await db_session.refresh(progress)

    question_ability = QuestionAbility(
        question_id=question.id, ability_id=ability.id
    )
    db_session.add(question_ability)
    await db_session.commit()

    result = await ProgressService.submit_answer(
        db_session, progress.id, user.id, question.id, "A"
    )

    assert isinstance(result, SubmitAnswerResponse)
    assert result.question_id == question.id
    assert result.is_correct == True
    assert result.correct_answer == "A"
    assert result.explanation == "解释"
    assert "细节提取" in result.ability_names

    await db_session.refresh(progress)
    assert progress.correct_count == 1


@pytest.mark.asyncio
async def test_submit_answer_incorrect(db_session):
    """Should submit incorrect answer"""
    user = User(openid="test_user")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    article = Article(
        title="测试文章",
        content="内容",
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.EASY
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)

    question = Question(
        article_id=article.id,
        type=QuestionTypeEnum.CHOICE,
        difficulty=DifficultyEnum.EASY,
        content="测试问题",
        options='{"A": "A", "B": "B"}',
        answer="A"
    )
    db_session.add(question)
    await db_session.commit()
    await db_session.refresh(question)

    progress = UserProgress(user_id=user.id, article_id=article.id, total_count=1)
    db_session.add(progress)
    await db_session.commit()
    await db_session.refresh(progress)

    result = await ProgressService.submit_answer(
        db_session, progress.id, user.id, question.id, "B"
    )

    assert result.is_correct == False

    await db_session.refresh(progress)
    assert progress.correct_count == 0


@pytest.mark.asyncio
async def test_submit_answer_duplicate(db_session):
    """Should reject duplicate answer submission"""
    user = User(openid="test_user")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    article = Article(
        title="测试文章",
        content="内容",
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.EASY
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)

    question = Question(
        article_id=article.id,
        type=QuestionTypeEnum.CHOICE,
        difficulty=DifficultyEnum.EASY,
        content="测试问题",
        options='{"A": "A", "B": "B"}',
        answer="A"
    )
    db_session.add(question)
    await db_session.commit()
    await db_session.refresh(question)

    progress = UserProgress(user_id=user.id, article_id=article.id, total_count=1)
    db_session.add(progress)
    await db_session.commit()
    await db_session.refresh(progress)

    await ProgressService.submit_answer(
        db_session, progress.id, user.id, question.id, "A"
    )

    with pytest.raises(ValueError, match="该题目已提交答案"):
        await ProgressService.submit_answer(
            db_session, progress.id, user.id, question.id, "B"
        )


@pytest.mark.asyncio
async def test_check_answer_choice():
    """Should check choice question correctly"""
    assert ProgressService._check_answer("choice", "A", "A") == True
    assert ProgressService._check_answer("choice", "a", "A") == True
    assert ProgressService._check_answer("choice", "B", "A") == False


@pytest.mark.asyncio
async def test_check_answer_judge():
    """Should check judge question correctly"""
    assert ProgressService._check_answer("judge", "TRUE", "TRUE") == True
    assert ProgressService._check_answer("judge", "true", "TRUE") == True
    assert ProgressService._check_answer("judge", "FALSE", "TRUE") == False


@pytest.mark.asyncio
async def test_check_answer_fill():
    """Should check fill question correctly"""
    assert ProgressService._check_answer("fill", "Paris", "paris") == True
    assert ProgressService._check_answer("fill", "London", "Paris") == False


@pytest.mark.asyncio
async def test_check_answer_short_answer():
    """Should always return True for short answer"""
    assert ProgressService._check_answer("short_answer", "anything", "A") == True


@pytest.mark.asyncio
async def test_complete_reading(db_session):
    """Should complete reading and update stats"""
    user = User(openid="test_user", total_readings=0, streak_days=0, max_streak_days=0)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    article = Article(
        title="测试文章",
        content="内容",
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.EASY
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)

    ability = AbilityDimension(name="细节提取", code="detail", category=AbilityCategoryEnum.INFORMATION)
    db_session.add(ability)
    await db_session.commit()
    await db_session.refresh(ability)

    question = Question(
        article_id=article.id,
        type=QuestionTypeEnum.CHOICE,
        difficulty=DifficultyEnum.EASY,
        content="测试问题",
        options='{"A": "A", "B": "B"}',
        answer="A"
    )
    db_session.add(question)
    await db_session.commit()
    await db_session.refresh(question)

    progress = UserProgress(user_id=user.id, article_id=article.id, total_count=1, correct_count=1)
    db_session.add(progress)
    await db_session.commit()
    await db_session.refresh(progress)

    answer = QuestionAnswer(progress_id=progress.id, question_id=question.id, user_answer="A", is_correct=True)
    db_session.add(answer)
    await db_session.commit()

    question_ability = QuestionAbility(
        question_id=question.id, ability_id=ability.id
    )
    db_session.add(question_ability)
    await db_session.commit()

    result = await ProgressService.complete_reading(db_session, progress.id, user.id, 180)

    assert isinstance(result, CompleteReadingResponse)
    assert result.progress_id == progress.id
    assert result.score == 100
    assert result.correct_count == 1
    assert result.total_count == 1
    assert result.time_spent == 180
    assert result.is_checked_in == True
    assert result.streak_days >= 1

    await db_session.refresh(progress)
    assert progress.score == 100
    assert progress.time_spent == 180
    assert progress.completed_at is not None

    await db_session.refresh(user)
    assert user.total_readings == 1


@pytest.mark.asyncio
async def test_complete_reading_already_completed(db_session):
    """Should reject completing already completed reading"""
    user = User(openid="test_user")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    article = Article(
        title="测试文章",
        content="内容",
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.EASY
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)

    progress = UserProgress(
        user_id=user.id,
        article_id=article.id,
        total_count=1,
        completed_at=datetime.utcnow()
    )
    db_session.add(progress)
    await db_session.commit()

    with pytest.raises(ValueError, match="该阅读已完成"):
        await ProgressService.complete_reading(db_session, progress.id, user.id, 180)


@pytest.mark.asyncio
async def test_update_user_abilities(db_session):
    """Should update user ability scores"""
    user = User(openid="test_user")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    article = Article(
        title="测试文章",
        content="内容",
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.EASY
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)

    ability = AbilityDimension(name="细节提取", code="detail", category=AbilityCategoryEnum.INFORMATION)
    db_session.add(ability)
    await db_session.commit()
    await db_session.refresh(ability)

    question = Question(
        article_id=article.id,
        type=QuestionTypeEnum.CHOICE,
        difficulty=DifficultyEnum.EASY,
        content="测试问题",
        options='{"A": "A", "B": "B"}',
        answer="A"
    )
    db_session.add(question)
    await db_session.commit()
    await db_session.refresh(question)

    progress = UserProgress(user_id=user.id, article_id=article.id, total_count=2, correct_count=1)
    db_session.add(progress)
    await db_session.commit()
    await db_session.refresh(progress)

    answer1 = QuestionAnswer(progress_id=progress.id, question_id=question.id, user_answer="A", is_correct=True)
    answer2 = QuestionAnswer(progress_id=progress.id, question_id=question.id, user_answer="B", is_correct=False)
    db_session.add_all([answer1, answer2])
    await db_session.commit()

    question_ability = QuestionAbility(
        question_id=question.id, ability_id=ability.id
    )
    db_session.add(question_ability)
    await db_session.commit()

    scores = await ProgressService._update_user_abilities(db_session, progress)

    assert len(scores) == 1
    assert scores[0].ability_name == "细节提取"
    assert scores[0].correct_count == 1
    assert scores[0].total_count == 2

    user_abilities = await db_session.execute(
        select(UserAbility).where(UserAbility.user_id == user.id)
    )
    user_ability = user_abilities.scalar_one_or_none()
    assert user_ability is not None
    assert user_ability.correct_count == 1
    assert user_ability.total_count == 2
    assert user_ability.score == 50.0


@pytest.mark.asyncio
async def test_handle_checkin_first_time(db_session):
    """Should handle first-time check-in"""
    user = User(openid="test_user", streak_days=0, max_streak_days=0)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    article = Article(
        title="测试文章",
        content="内容",
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.EASY
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)

    progress = UserProgress(user_id=user.id, article_id=article.id, total_count=1)
    db_session.add(progress)
    await db_session.commit()
    await db_session.refresh(progress)

    is_checked_in, streak = await ProgressService._handle_checkin(db_session, user, progress)

    assert is_checked_in == True
    assert streak == 1

    await db_session.refresh(user)
    assert user.streak_days == 1
    assert user.max_streak_days == 1


@pytest.mark.asyncio
async def test_handle_checkin_already_checked_in(db_session):
    """Should handle already checked in for the day"""
    from app.models.checkin import CheckIn

    user = User(openid="test_user", streak_days=5, max_streak_days=5)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    article = Article(
        title="测试文章",
        content="内容",
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.EASY
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)

    progress = UserProgress(user_id=user.id, article_id=article.id, total_count=1)
    db_session.add(progress)
    await db_session.commit()
    await db_session.refresh(progress)

    checkin = CheckIn(user_id=user.id, check_date=date.today())
    db_session.add(checkin)
    await db_session.commit()

    is_checked_in, streak = await ProgressService._handle_checkin(db_session, user, progress)

    assert is_checked_in == False
    assert streak == 5

    await db_session.refresh(user)
    assert user.streak_days == 5


@pytest.mark.asyncio
async def test_check_badges_first_reading(db_session):
    """Should award first reading badge"""
    user = User(openid="test_user", total_readings=0)
    db_session.add(user)
    await db_session.commit()

    badge = Badge(
        name="阅读新星",
        description="完成第一次阅读",
        category=BadgeCategoryEnum.READING,
        condition_type=BadgeConditionTypeEnum.FIRST_READING,
        condition_value=1
    )
    db_session.add(badge)
    await db_session.commit()

    new_badges = await ProgressService._check_badges(db_session, user)

    assert len(new_badges) == 1
    assert new_badges[0].name == "阅读新星"
    assert new_badges[0].id == badge.id


@pytest.mark.asyncio
async def test_check_badges_streak_days(db_session):
    """Should award streak badge"""
    user = User(openid="test_user", streak_days=3)
    db_session.add(user)
    await db_session.commit()

    badge = Badge(
        name="三日小达人",
        description="连续打卡3天",
        category=BadgeCategoryEnum.PERSISTENCE,
        condition_type=BadgeConditionTypeEnum.STREAK_DAYS,
        condition_value=3
    )
    db_session.add(badge)
    await db_session.commit()

    new_badges = await ProgressService._check_badges(db_session, user)

    assert len(new_badges) == 1
    assert new_badges[0].name == "三日小达人"


@pytest.mark.asyncio
async def test_check_badges_already_owned(db_session):
    """Should not award already owned badges"""
    from app.models.badge import UserBadge

    user = User(openid="test_user", total_readings=0)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    badge = Badge(
        name="阅读新星",
        description="完成第一次阅读",
        category=BadgeCategoryEnum.READING,
        condition_type=BadgeConditionTypeEnum.FIRST_READING,
        condition_value=1
    )
    db_session.add(badge)
    await db_session.commit()
    await db_session.refresh(badge)

    user_badge = UserBadge(user_id=user.id, badge_id=badge.id)
    db_session.add(user_badge)
    await db_session.commit()

    new_badges = await ProgressService._check_badges(db_session, user)

    assert len(new_badges) == 0


@pytest.mark.asyncio
async def test_get_progress_detail(db_session):
    """Should get progress detail with answers"""
    user = User(openid="test_user")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    article = Article(
        title="测试文章",
        content="内容",
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.EASY
    )
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)

    question = Question(
        article_id=article.id,
        type=QuestionTypeEnum.CHOICE,
        difficulty=DifficultyEnum.EASY,
        content="测试问题",
        options='{"A": "A", "B": "B"}',
        answer="A",
        explanation="解释"
    )
    db_session.add(question)
    await db_session.commit()
    await db_session.refresh(question)

    progress = UserProgress(
        user_id=user.id,
        article_id=article.id,
        total_count=1,
        correct_count=1,
        score=100,
        time_spent=180,
        completed_at=datetime.utcnow()
    )
    db_session.add(progress)
    await db_session.commit()
    await db_session.refresh(progress)

    answer = QuestionAnswer(progress_id=progress.id, question_id=question.id, user_answer="A", is_correct=True)
    db_session.add(answer)
    await db_session.commit()

    result = await ProgressService.get_progress_detail(db_session, progress.id, user.id)

    assert isinstance(result, ProgressWithAnswers)
    assert result.id == progress.id
    assert result.article_title == "测试文章"
    assert result.score == 100
    assert len(result.answers) == 1
    assert result.answers[0].question_id == question.id
    assert result.answers[0].is_correct == True


@pytest.mark.asyncio
async def test_get_progress_detail_not_found(db_session):
    """Should return None for non-existent progress"""
    user = User(openid="test_user")
    db_session.add(user)
    await db_session.commit()

    result = await ProgressService.get_progress_detail(db_session, 999, user.id)

    assert result is None


@pytest.mark.asyncio
async def test_get_history(db_session):
    """Should get reading history"""
    user = User(openid="test_user")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    article1 = Article(
        title="文章1",
        content="内容",
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.EASY
    )
    article2 = Article(
        title="文章2",
        content="内容",
        word_count=100,
        reading_time=1,
        status=ArticleStatusEnum.PUBLISHED,
        article_difficulty=DifficultyEnum.EASY
    )
    db_session.add_all([article1, article2])
    await db_session.commit()
    await db_session.refresh(article1)
    await db_session.refresh(article2)

    progress1 = UserProgress(
        user_id=user.id,
        article_id=article1.id,
        total_count=1,
        score=80,
        completed_at=datetime.utcnow()
    )
    progress2 = UserProgress(
        user_id=user.id,
        article_id=article2.id,
        total_count=1,
        score=90,
        completed_at=datetime.utcnow()
    )
    db_session.add_all([progress1, progress2])
    await db_session.commit()

    items, total = await ProgressService.get_history(db_session, user.id, 1, 20)

    assert total == 2
    assert len(items) == 2
    assert all(isinstance(item, HistoryItem) for item in items)


@pytest.mark.asyncio
async def test_get_history_pagination(db_session):
    """Should handle pagination in history"""
    user = User(openid="test_user")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    articles = []
    for i in range(5):
        article = Article(
            title=f"文章{i}",
            content="内容",
            word_count=100,
            reading_time=1,
            status=ArticleStatusEnum.PUBLISHED,
            article_difficulty=DifficultyEnum.EASY
        )
        articles.append(article)
    db_session.add_all(articles)
    await db_session.commit()
    for article in articles:
        await db_session.refresh(article)

    progresses = []
    for i, article in enumerate(articles):
        progress = UserProgress(
            user_id=user.id,
            article_id=article.id,
            total_count=1,
            score=i * 10,
            completed_at=datetime.utcnow()
        )
        progresses.append(progress)
    db_session.add_all(progresses)
    await db_session.commit()

    items, total = await ProgressService.get_history(db_session, user.id, 1, 2)

    assert total == 5
    assert len(items) == 2


@pytest.mark.asyncio
async def test_get_history_empty(db_session):
    """Should return empty history for user with no readings"""
    user = User(openid="test_user")
    db_session.add(user)
    await db_session.commit()

    items, total = await ProgressService.get_history(db_session, user.id, 1, 20)

    assert total == 0
    assert len(items) == 0
