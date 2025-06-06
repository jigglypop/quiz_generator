"""
애플리케이션 설정 관리
"""
import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Settings:
    """애플리케이션 설정"""
    
    # API 키
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2", "false")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "Korean-Financial-Quiz-Generator")
    LANGCHAIN_ENDPOINT: str = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    RELOAD: bool = True
    
    # 교재 디렉토리
    TEXTBOOK_DIRS: List[str] = [
        "요약/신탁교재_장별통합", 
        "요약/신탁교재", 
        "요약/퇴직연금교재_장별통합", 
        "요약/퇴직연금교재"
    ]
    
    # AI 모델 설정
    EMBEDDING_MODEL: str = "jhgan/ko-sroberta-multitask"
    GPT_MODEL: str = "gpt-4o"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 1200
    
    # 벡터 DB 설정
    CHROMA_DB_PATH: str = "./chroma_db"
    COLLECTION_NAME: str = "korean_financial_textbooks"
    
    # 퀴즈 설정
    DEFAULT_NUM_QUESTIONS: int = 5
    MAX_QUESTIONS_PER_REQUEST: int = 10
    CHUNK_LIMIT: int = 50
    
    @property
    def is_openai_configured(self) -> bool:
        """OpenAI API 키가 설정되었는지 확인"""
        return bool(self.OPENAI_API_KEY)
    
    def validate(self) -> None:
        """설정 유효성 검사"""
        if not self.is_openai_configured:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다. .env 파일을 확인해주세요.")

# 전역 설정 인스턴스
settings = Settings()

# 설정 검증
settings.validate() 