import pytest
from app.schemas.question import QuestionTypeEnum, DifficultyEnum, AbilityInfo, QuestionItem, QuestionWithAnswer, QuestionListResponse


def test_question_type_enum():
    """QuestionTypeEnum should have correct values"""
    assert QuestionTypeEnum.CHOICE.value == "choice"
    assert QuestionTypeEnum.JUDGE.value == "judge"
    assert QuestionTypeEnum.FILL.value == "fill"
    assert QuestionTypeEnum.SHORT_ANSWER.value == "short_answer"


def test_difficulty_enum():
    """DifficultyEnum should have correct values"""
    assert DifficultyEnum.EASY.value == 1
    assert DifficultyEnum.MEDIUM.value == 2
    assert DifficultyEnum.HARD.value == 3


def test_ability_info():
    """AbilityInfo should serialize correctly"""
    ability = AbilityInfo(
        id=1,
        name="细节提取",
        code="detail_extraction"
    )
    assert ability.id == 1
    assert ability.name == "细节提取"
    assert ability.code == "detail_extraction"


def test_question_item_with_choice():
    """QuestionItem should work for choice questions with options list"""
    question = QuestionItem(
        id=1,
        type=QuestionTypeEnum.CHOICE,
        content="What is the capital of France?",
        options=["A. Paris", "B. London", "C. Berlin", "D. Rome"],
        hint="Think about European capitals",
        difficulty=DifficultyEnum.EASY,
        abilities=[
            AbilityInfo(id=1, name="细节提取", code="detail_extraction")
        ]
    )
    assert question.id == 1
    assert question.type == QuestionTypeEnum.CHOICE
    assert question.content == "What is the capital of France?"
    assert question.options == ["A. Paris", "B. London", "C. Berlin", "D. Rome"]
    assert question.hint == "Think about European capitals"
    assert question.difficulty == DifficultyEnum.EASY
    assert len(question.abilities) == 1
    assert question.abilities[0].name == "细节提取"
    assert "answer" not in question.model_fields
    assert "explanation" not in question.model_fields


def test_question_item_without_options():
    """QuestionItem should work for fill/short_answer without options"""
    question = QuestionItem(
        id=2,
        type=QuestionTypeEnum.FILL,
        content="The capital of France is ____.",
        options=None,
        hint=None,
        difficulty=DifficultyEnum.MEDIUM,
        abilities=[]
    )
    assert question.id == 2
    assert question.type == QuestionTypeEnum.FILL
    assert question.content == "The capital of France is ____."
    assert question.options is None
    assert question.hint is None
    assert question.difficulty == DifficultyEnum.MEDIUM
    assert len(question.abilities) == 0


def test_question_with_answer():
    """QuestionWithAnswer should extend QuestionItem with answer and explanation"""
    question = QuestionWithAnswer(
        id=1,
        type=QuestionTypeEnum.CHOICE,
        content="What is the capital of France?",
        options=["A. Paris", "B. London", "C. Berlin", "D. Rome"],
        hint="Think about European capitals",
        difficulty=DifficultyEnum.EASY,
        abilities=[
            AbilityInfo(id=1, name="细节提取", code="detail_extraction")
        ],
        answer="A",
        explanation="Paris is the capital of France"
    )
    assert question.id == 1
    assert question.answer == "A"
    assert question.explanation == "Paris is the capital of France"
    assert "answer" in question.model_fields
    assert "explanation" in question.model_fields


def test_question_list_response():
    """QuestionListResponse should serialize correctly"""
    response = QuestionListResponse(
        article_id=1,
        article_title="Test Article",
        questions=[
            QuestionItem(
                id=1,
                type=QuestionTypeEnum.CHOICE,
                content="Question 1",
                options=["A", "B"],
                hint=None,
                difficulty=DifficultyEnum.EASY,
                abilities=[]
            ),
            QuestionItem(
                id=2,
                type=QuestionTypeEnum.SHORT_ANSWER,
                content="Question 2",
                options=None,
                hint="Think about it",
                difficulty=DifficultyEnum.MEDIUM,
                abilities=[]
            )
        ],
        total=2
    )
    assert response.article_id == 1
    assert response.article_title == "Test Article"
    assert len(response.questions) == 2
    assert response.total == 2
    assert response.questions[0].type == QuestionTypeEnum.CHOICE
    assert response.questions[1].type == QuestionTypeEnum.SHORT_ANSWER


def test_question_item_multiple_abilities():
    """QuestionItem should support multiple abilities"""
    question = QuestionItem(
        id=1,
        type=QuestionTypeEnum.CHOICE,
        content="Test question",
        options=["A", "B"],
        hint=None,
        difficulty=DifficultyEnum.HARD,
        abilities=[
            AbilityInfo(id=1, name="细节提取", code="detail_extraction"),
            AbilityInfo(id=2, name="推理判断", code="inference"),
            AbilityInfo(id=3, name="主旨概括", code="main_idea")
        ]
    )
    assert len(question.abilities) == 3
    assert question.abilities[0].code == "detail_extraction"
    assert question.abilities[1].code == "inference"
    assert question.abilities[2].code == "main_idea"


def test_question_item_judge_type():
    """QuestionItem should work for judge questions"""
    question = QuestionItem(
        id=1,
        type=QuestionTypeEnum.JUDGE,
        content="The sky is blue. True or False?",
        options=None,
        hint="Think about the weather",
        difficulty=DifficultyEnum.EASY,
        abilities=[]
    )
    assert question.type == QuestionTypeEnum.JUDGE
    assert question.options is None
