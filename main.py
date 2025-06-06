"""
한국어 금융교재 퀴즈 생성기 - 메인 애플리케이션

GPT-4o 기반 고품질 퀴즈 생성 시스템
실시간 핫리로딩 지원, 모듈화된 구조
"""

import asyncio
import uvicorn
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings
from src.models import (
    SearchRequest, SearchResponse,
    QuizRequest, QuizSectionRequest, QuizResponse,
    ChaptersResponse, HealthResponse
)
from src.services import rag_service, quiz_service
from src.utils import emoji_logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작 시 초기화
    emoji_logger.startup("금융교재 퀴즈 생성기가 시작됩니다...")
    emoji_logger.api("지원 교재: 신탁교재, 퇴직연금교재")
    emoji_logger.api(f"서버 주소: http://localhost:{settings.PORT}")
    emoji_logger.api(f"API 문서: http://localhost:{settings.PORT}/docs")
    emoji_logger.ai("GPT 기반 고품질 퀴즈 생성")
    
    try:
        # RAG 시스템 초기화
        await rag_service.initialize()
        
        yield
        
    except Exception as e:
        emoji_logger.error(f"애플리케이션 시작 실패: {e}")
        raise
    finally:
        # 종료 시 정리
        emoji_logger.success("애플리케이션이 종료되었습니다.")

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="한국어 금융교재 퀴즈 생성기",
    description="AI 기반 신탁교재 및 퇴직연금교재 퀴즈 생성 시스템",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    """시스템 상태 확인"""
    try:
        db_stats = rag_service.get_database_stats()
        
        return HealthResponse(
            message="🎉 한국어 금융교재 퀴즈 생성기가 정상 작동 중입니다!",
            supported_textbooks=["신탁교재", "퇴직연금교재"],
            features=[
                "📚 46개 교재 파일 지원",
                "🤖 GPT-4o 기반 퀴즈 생성", 
                "🔍 의미론적 문서 검색",
                "📊 장별/절별 퀴즈 생성",
                "⚡ 실시간 핫리로딩"
            ],
            api_docs=f"http://localhost:{settings.PORT}/docs",
            database_status=db_stats
        )
        
    except Exception as e:
        emoji_logger.error(f"상태 확인 실패: {e}")
        raise HTTPException(status_code=500, detail="시스템 상태 확인에 실패했습니다.")

@app.get("/chapters", response_model=ChaptersResponse)
async def get_chapters() -> ChaptersResponse:
    """지원하는 교재 및 챕터 목록 조회"""
    try:
        chapters_data = quiz_service.get_available_chapters()
        
        return ChaptersResponse(data=chapters_data)
        
    except Exception as e:
        emoji_logger.error(f"챕터 정보 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="챕터 정보를 가져올 수 없습니다.")

@app.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest) -> SearchResponse:
    """문서 검색"""
    try:
        results = await rag_service.search_documents(
            query=request.query,
            n_results=request.n_results
        )
        
        return SearchResponse(
            query=request.query,
            results=results,
            count=len(results.get("documents", []))
        )
        
    except Exception as e:
        emoji_logger.error(f"문서 검색 실패: {e}")
        raise HTTPException(status_code=500, detail="문서 검색에 실패했습니다.")

@app.post("/generate-quiz", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest) -> QuizResponse:
    """장별 퀴즈 생성"""
    try:
        # 요청 검증
        if request.num_questions > settings.MAX_QUESTIONS_PER_REQUEST:
            raise HTTPException(
                status_code=400, 
                detail=f"최대 {settings.MAX_QUESTIONS_PER_REQUEST}개까지만 생성 가능합니다."
            )
        
        # 퀴즈 생성
        quizzes = await quiz_service.generate_chapter_quiz(request)
        
        if not quizzes:
            raise HTTPException(
                status_code=404,
                detail=f"{request.textbook} {request.chapter}에서 퀴즈를 생성할 수 없습니다."
            )
        
        return QuizResponse(
            textbook=request.textbook,
            chapter=request.chapter,
            section=None,
            chapter_section=f"{request.textbook} {request.chapter}",
            num_questions=len(quizzes),
            quizzes=quizzes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        emoji_logger.error(f"퀴즈 생성 실패: {e}")
        raise HTTPException(status_code=500, detail="퀴즈 생성에 실패했습니다.")

@app.post("/generate-quiz-section", response_model=QuizResponse)
async def generate_quiz_section(request: QuizSectionRequest) -> QuizResponse:
    """절별 퀴즈 생성 (신규 엔드포인트)"""
    try:
        # 요청 검증
        if request.num_questions > settings.MAX_QUESTIONS_PER_REQUEST:
            raise HTTPException(
                status_code=400, 
                detail=f"최대 {settings.MAX_QUESTIONS_PER_REQUEST}개까지만 생성 가능합니다."
            )
        
        # 절별 퀴즈 생성
        quizzes = await quiz_service.generate_section_quiz(request)
        
        if not quizzes:
            section_info = f" {request.section}" if request.section else ""
            raise HTTPException(
                status_code=404,
                detail=f"{request.textbook} {request.chapter}{section_info}에서 퀴즈를 생성할 수 없습니다."
            )
        
        # 응답 생성
        section_suffix = f" {request.section}" if request.section else ""
        chapter_section = f"{request.textbook} {request.chapter}{section_suffix}"
        
        return QuizResponse(
            textbook=request.textbook,
            chapter=request.chapter,
            section=request.section,
            chapter_section=chapter_section,
            num_questions=len(quizzes),
            quizzes=quizzes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        emoji_logger.error(f"절별 퀴즈 생성 실패: {e}")
        raise HTTPException(status_code=500, detail="절별 퀴즈 생성에 실패했습니다.")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """전역 예외 처리"""
    emoji_logger.error(f"예상치 못한 오류: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "서버 내부 오류가 발생했습니다."}
    )

async def main():
    """메인 실행 함수"""
    try:
        # 서버 설정
        config = uvicorn.Config(
            app="main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.RELOAD,  # 핫리로딩 활성화
            reload_dirs=["src/", "."],  # 감시할 디렉토리
            reload_includes=["*.py"],  # 감시할 파일 패턴
            log_level="info" if settings.DEBUG else "warning",
            loop="asyncio"
        )
        
        # 서버 실행
        server = uvicorn.Server(config)
        await server.serve()
        
    except KeyboardInterrupt:
        emoji_logger.success("사용자에 의해 서버가 종료되었습니다.")
    except Exception as e:
        emoji_logger.error(f"서버 실행 실패: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 