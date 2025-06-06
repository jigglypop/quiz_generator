"""
구조화된 로깅 유틸리티
"""
import sys
from loguru import logger

# 기존 로거 제거
logger.remove()

# 콘솔 로깅 설정
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True
)

# 파일 로깅 설정
logger.add(
    "logs/app.log",
    rotation="1 day",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    encoding="utf-8"
)

# 이모지 로깅 함수들
class EmojiLogger:
    """이모지를 활용한 친근한 로깅"""
    
    @staticmethod
    def startup(message: str):
        """시작 메시지"""
        logger.info(f"🚀 {message}")
    
    @staticmethod
    def success(message: str):
        """성공 메시지"""
        logger.info(f"✅ {message}")
    
    @staticmethod
    def loading(message: str):
        """로딩 메시지"""
        logger.info(f"📚 {message}")
    
    @staticmethod
    def processing(message: str):
        """처리 메시지"""
        logger.info(f"🔧 {message}")
    
    @staticmethod
    def database(message: str):
        """데이터베이스 메시지"""
        logger.info(f"💾 {message}")
    
    @staticmethod
    def ai(message: str):
        """AI 관련 메시지"""
        logger.info(f"🤖 {message}")
    
    @staticmethod
    def quiz(message: str):
        """퀴즈 관련 메시지"""
        logger.info(f"🎲 {message}")
    
    @staticmethod
    def search(message: str):
        """검색 관련 메시지"""
        logger.info(f"🔍 {message}")
    
    @staticmethod
    def api(message: str):
        """API 관련 메시지"""
        logger.info(f"🔗 {message}")
    
    @staticmethod
    def config(message: str):
        """설정 관련 메시지"""
        logger.info(f"🔑 {message}")
    
    @staticmethod
    def stats(message: str):
        """통계 메시지"""
        logger.info(f"📊 {message}")
    
    @staticmethod
    def file(message: str):
        """파일 관련 메시지"""
        logger.info(f"📄 {message}")
    
    @staticmethod
    def folder(message: str):
        """폴더 관련 메시지"""
        logger.info(f"📁 {message}")
    
    @staticmethod
    def chunk(message: str):
        """청킹 관련 메시지"""
        logger.info(f"🔪 {message}")
    
    @staticmethod
    def target(message: str):
        """타겟/목표 메시지"""
        logger.info(f"🎯 {message}")
    
    @staticmethod
    def celebration(message: str):
        """축하 메시지"""
        logger.info(f"🎉 {message}")
    
    @staticmethod
    def warning(message: str):
        """경고 메시지"""
        logger.warning(f"⚠️ {message}")
    
    @staticmethod
    def error(message: str):
        """에러 메시지"""
        logger.error(f"❌ {message}")
    
    @staticmethod
    def debug(message: str):
        """디버그 메시지"""
        logger.debug(f"🐛 {message}")

# 전역 로거 인스턴스
emoji_logger = EmojiLogger() 