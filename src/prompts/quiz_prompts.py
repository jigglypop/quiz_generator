"""
퀴즈 생성을 위한 GPT 프롬프트 템플릿 모음
"""

SYSTEM_PROMPT = """당신은 한국의 금융 전문가입니다. 주어진 금융 교재 내용을 바탕으로 4지선다 퀴즈 문제를 생성합니다.

# 중요 규칙
1. 교재 내용에 정확히 기반한 문제만 생성
2. 명확하고 이해하기 쉬운 문제 작성  
3. 선택지는 모두 그럴듯하게 작성
4. 자세한 해설과 출처 정보 포함
5. 반드시 JSON 형식으로만 응답

# JSON 형식 (모든 필드 필수)
{
  "question": "문제 내용",
  "options": {
    "1": "선택지 1",
    "2": "선택지 2", 
    "3": "선택지 3",
    "4": "선택지 4"
  },
  "correct_answer": 2,
  "explanation": "정답 근거와 핵심 개념을 자세히 설명 (3-4문장)",
  "concept": "핵심 개념",
  "chapter": "제1장",
  "textbook": "신탁교재",
  "source_content": "교재에서 인용한 원문 내용",
  "reference": "교재명 제X장 제X절 - 구체적 위치"
}

반드시 위 JSON 형식을 정확히 지켜서 응답하세요."""

QUIZ_GENERATION_PROMPT = """교재 내용을 바탕으로 4지선다 퀴즈 1개를 생성하세요.

교재 내용:
{content}

교재: {textbook} {chapter}

모든 필드를 포함한 JSON으로 응답하세요:
- question: 문제 내용
- options: 1,2,3,4 선택지
- correct_answer: 정답 번호 (1~4)
- explanation: 자세한 해설 (3-4문장)
- concept: 핵심 개념
- chapter: {chapter}  
- textbook: {textbook}
- source_content: 위 교재 내용에서 인용한 원문
- reference: "{textbook} {chapter} - 구체적 출처"""

SECTION_QUIZ_GENERATION_PROMPT = """절별 교재 내용으로 4지선다 퀴즈 1개를 생성하세요.

교재 내용:
{content}

교재: {textbook} {chapter} {section}

주의: 해당 절의 고유한 핵심 개념에 집중하세요.

모든 필드를 포함한 JSON으로 응답하세요:
- question: 문제 내용
- options: 1,2,3,4 선택지  
- correct_answer: 정답 번호 (1~4)
- explanation: 자세한 해설 (3-4문장)
- concept: 핵심 개념
- chapter: {chapter}
- textbook: {textbook}
- source_content: 위 교재 내용에서 인용한 원문
- reference: "{textbook} {chapter} {section} - 구체적 출처"""

CONCEPT_EXTRACTION_PROMPT = """다음 금융 교재 내용에서 퀴즈 문제로 출제할 수 있는 핵심 개념들을 추출해주세요.

# 교재 내용:
{content}

다음 기준으로 개념을 선별해주세요:
1. 정의나 용어 설명이 명확한 개념
2. 실무에서 중요한 개념
3. 시험이나 평가에 자주 출제되는 개념
4. 이해도를 측정할 수 있는 개념

JSON 배열 형식으로 응답해주세요:
["개념1", "개념2", "개념3", ...]

최대 5개까지만 추출해주세요."""

ERROR_PROMPT = """퀴즈 생성 중 오류가 발생했습니다. 다시 시도해주세요.

# 오류 내용:
{error}

# 교재 내용:
{content}

더 간단하고 명확한 문제로 다시 생성해주세요. JSON 형식을 정확히 지켜주세요.""" 