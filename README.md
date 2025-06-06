# 🏦 한국어 금융교재 퀴즈 생성기

GPT 기반 고품질 한국어 금융교재 퀴즈 자동 생성 시스템

## ✨ 주요 기능

- 📚 **다중 교재 지원**: 신탁교재 & 퇴직연금교재
- 🤖 **GPT-4o 통합**: OpenAI 최신 모델 기반 고품질 문제 생성
- 🔍 **RAG 시스템**: 의미 기반 문서 검색으로 정확한 내용 반영
- 📖 **장별/절별 검색**: 세분화된 범위에서 문제 생성
- 🌐 **FastAPI 서버**: RESTful API로 웹 서비스 제공
- 🇰🇷 **한국어 최적화**: 한국어 SentenceTransformer 사용

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 저장소 클론
git clone <your-repo-url>
cd korean-financial-quiz-generator

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate     # Windows

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정

```bash
# OpenAI API 키 설정 (필수)
export OPENAI_API_KEY="your-openai-api-key"

# LangChain 추적 (선택사항)
export LANGCHAIN_TRACING_V2="true"
export LANGCHAIN_PROJECT="Quiz Generator"
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
export LANGCHAIN_API_KEY="your-langchain-api-key"
```

### 3. 실행

```bash
python quiz_generator.py
```

서버가 시작되면 다음 주소에서 확인:
- 🌐 **메인 서버**: http://localhost:8000
- 📖 **API 문서**: http://localhost:8000/docs

## 📁 프로젝트 구조

```
korean-financial-quiz-generator/
├── quiz_generator.py          # 메인 애플리케이션
├── requirements.txt           # Python 패키지 의존성
├── README.md                  # 프로젝트 설명서
├── .gitignore                # Git 무시 파일 설정
├── chroma_db/                # 벡터 데이터베이스 (자동생성)
└── 요약/                      # 교재 원본 파일들
    ├── 신탁교재/              # 절별 신탁교재
    ├── 신탁교재_장별통합/      # 장별 통합 신탁교재
    ├── 퇴직연금교재/          # 절별 퇴직연금교재
    └── 퇴직연금교재_장별통합/  # 장별 통합 퇴직연금교재
```

## 🔧 API 사용법

### 1. 기본 퀴즈 생성

```bash
curl -X POST "http://localhost:8000/generate-quiz" \
  -H "Content-Type: application/json" \
  -d '{
    "textbook": "신탁교재",
    "chapter": "제1장",
    "num_questions": 3
  }'
```

### 2. 절별 퀴즈 생성

```bash
curl -X POST "http://localhost:8000/generate-quiz-section" \
  -H "Content-Type: application/json" \
  -d '{
    "textbook": "신탁교재",
    "chapter": "제1장",
    "section": "제1절",
    "num_questions": 2
  }'
```

### 3. 교재 구조 확인

```bash
curl -X GET "http://localhost:8000/chapters"
```

### 4. 내용 검색

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "신탁의 정의",
    "n_results": 5
  }'
```

## 📊 지원 교재

### 신탁교재
- 제1장: 신탁기초
- 제2장: 금전신탁  
- 제3장: 금전신탁상품
- 제4장: 재산신탁업무
- 제5장: 재산신탁상품
- 제6장: 신탁대출

### 퇴직연금교재  
- 제1장: 퇴직연금제도기초
- 제2장: 퇴직연금제도도입
- 제3장: 퇴직연금적립금운용
- 제4장: 계약관리
- 제5장: 회계세제사업자

## 🎯 퀴즈 품질 특징

- ✅ **실무 중심**: 실제 업무에서 필요한 내용 위주
- ✅ **법규 정확성**: 관련 법령과 규정에 기반한 정확한 내용
- ✅ **난이도 조절**: 전문자격시험 수준의 적절한 난이도
- ✅ **상세 해설**: 정답 근거와 오답 분석 포함
- ✅ **현실적 오답**: 실제로 혼동하기 쉬운 내용으로 구성

## 💰 비용 정보

- **GPT-4o 모델 사용**: 입력 $0.25/1M 토큰, 출력 $1.25/1M 토큰
- **예상 비용**: 퀴즈 1문제당 약 $0.002-0.005
- **월 예상**: 1000문제 생성 시 약 $2-5

## 🛠️ 기술 스택

- **Backend**: Python 3.11+, FastAPI, Uvicorn
- **AI/ML**: OpenAI GPT-4o, SentenceTransformers, ChromaDB
- **Vector Search**: ChromaDB (Persistent Storage)
- **Embedding**: jhgan/ko-sroberta-multitask (한국어 최적화)

## 📝 라이선스

이 프로젝트는 교육 목적으로 개발되었습니다.

## 🤝 기여

버그 리포트나 기능 제안은 Issues에서 환영합니다!

## 📞 문의

프로젝트 관련 문의사항이 있으시면 Issues를 통해 연락해주세요. 