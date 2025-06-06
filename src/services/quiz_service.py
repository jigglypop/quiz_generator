"""
퀴즈 생성 서비스
"""
import json
import random
from typing import Dict, List, Optional, Any
from openai import OpenAI

from src.config.settings import settings
from src.models.schemas import QuizQuestion, QuizRequest, QuizSectionRequest
from src.prompts.quiz_prompts import (
    SYSTEM_PROMPT, 
    QUIZ_GENERATION_PROMPT, 
    SECTION_QUIZ_GENERATION_PROMPT,
    ERROR_PROMPT
)
from src.services.rag_service import rag_service
from src.utils.logger import emoji_logger

class QuizService:
    """퀴즈 생성 서비스"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def generate_chapter_quiz(self, request: QuizRequest) -> List[QuizQuestion]:
        """장별 퀴즈 생성"""
        emoji_logger.quiz(f"'{request.textbook} {request.chapter}' 챕터에서 {request.num_questions}개 퀴즈 생성 시도...")
        
        # 챕터 콘텐츠 가져오기
        contents = rag_service.get_chapter_content(
            request.textbook, 
            request.chapter, 
            limit=settings.CHUNK_LIMIT
        )
        
        if not contents:
            emoji_logger.error(f"'{request.textbook} {request.chapter}' 챕터의 콘텐츠를 찾을 수 없습니다.")
            return []
        
        emoji_logger.search(f"가져온 컨텐츠 청크 수: {len(contents)}")
        
        # 퀴즈 생성
        quizzes = []
        for i in range(request.num_questions):
            quiz = await self._generate_single_quiz(
                contents=contents,
                textbook=request.textbook,
                chapter=request.chapter,
                quiz_index=i+1
            )
            
            if quiz:
                quizzes.append(quiz)
        
        emoji_logger.celebration(f"총 {len(quizzes)}개 퀴즈 생성 완료!")
        return quizzes
    
    async def generate_section_quiz(self, request: QuizSectionRequest) -> List[QuizQuestion]:
        """절별 퀴즈 생성"""
        if not request.section:
            # 절이 지정되지 않은 경우 장별 퀴즈로 처리
            chapter_request = QuizRequest(
                textbook=request.textbook,
                chapter=request.chapter,
                num_questions=request.num_questions
            )
            return await self.generate_chapter_quiz(chapter_request)
        
        emoji_logger.quiz(f"'{request.textbook} {request.chapter} {request.section}' 절에서 {request.num_questions}개 퀴즈 생성 시도...")
        
        # 절별 콘텐츠 가져오기
        contents = rag_service.get_section_content(
            request.textbook,
            request.chapter,
            request.section,
            limit=30
        )
        
        if not contents:
            emoji_logger.warning(f"절별 콘텐츠를 찾을 수 없어 장별 콘텐츠로 대체합니다.")
            # 절별 콘텐츠가 없으면 장별 콘텐츠로 대체
            contents = rag_service.get_chapter_content(
                request.textbook,
                request.chapter,
                limit=settings.CHUNK_LIMIT
            )
        
        if not contents:
            emoji_logger.error(f"'{request.textbook} {request.chapter} {request.section}' 콘텐츠를 찾을 수 없습니다.")
            return []
        
        emoji_logger.search(f"가져온 절별 컨텐츠 청크 수: {len(contents)}")
        
        # 절별 퀴즈 생성
        quizzes = []
        for i in range(request.num_questions):
            quiz = await self._generate_single_section_quiz(
                contents=contents,
                textbook=request.textbook,
                chapter=request.chapter,
                section=request.section,
                quiz_index=i+1
            )
            
            if quiz:
                quizzes.append(quiz)
        
        emoji_logger.celebration(f"총 {len(quizzes)}개 절별 퀴즈 생성 완료!")
        return quizzes
    
    async def _generate_single_quiz(
        self, 
        contents: List[str], 
        textbook: str, 
        chapter: str, 
        quiz_index: int
    ) -> Optional[QuizQuestion]:
        """단일 퀴즈 생성 (장별)"""
        try:
            # 랜덤하게 콘텐츠 선택
            selected_content = random.choice(contents)
            
            emoji_logger.ai(f"{quiz_index}번째 퀴즈 GPT 생성 중... (청크 길이: {len(selected_content)})")
            
            # GPT 프롬프트 생성
            prompt = QUIZ_GENERATION_PROMPT.format(
                content=selected_content,
                textbook=textbook,
                chapter=chapter
            )
            
            # OpenAI API 호출
            response = await self._call_openai(prompt)
            
            if response:
                quiz_data = json.loads(response)
                quiz = QuizQuestion(**quiz_data)
                emoji_logger.success(f"{quiz_index}번째 퀴즈 생성 완료")
                return quiz
            
        except Exception as e:
            emoji_logger.error(f"{quiz_index}번째 퀴즈 생성 실패: {e}")
        
        return None
    
    async def _generate_single_section_quiz(
        self,
        contents: List[str],
        textbook: str,
        chapter: str,
        section: str,
        quiz_index: int
    ) -> Optional[QuizQuestion]:
        """단일 퀴즈 생성 (절별)"""
        try:
            # 랜덤하게 콘텐츠 선택
            selected_content = random.choice(contents)
            
            emoji_logger.ai(f"{quiz_index}번째 절별 퀴즈 GPT 생성 중... (청크 길이: {len(selected_content)})")
            
            # 절별 GPT 프롬프트 생성
            prompt = SECTION_QUIZ_GENERATION_PROMPT.format(
                content=selected_content,
                textbook=textbook,
                chapter=chapter,
                section=section
            )
            
            # OpenAI API 호출
            response = await self._call_openai(prompt)
            
            if response:
                quiz_data = json.loads(response)
                quiz = QuizQuestion(**quiz_data)
                emoji_logger.success(f"{quiz_index}번째 절별 퀴즈 생성 완료")
                return quiz
            
        except Exception as e:
            emoji_logger.error(f"{quiz_index}번째 절별 퀴즈 생성 실패: {e}")
        
        return None
    
    async def _call_openai(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """OpenAI API 호출"""
        for attempt in range(max_retries):
            try:
                response = self.openai_client.chat.completions.create(
                    model=settings.GPT_MODEL,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=settings.TEMPERATURE,
                    max_tokens=settings.MAX_TOKENS
                )
                
                content = response.choices[0].message.content.strip()
                
                # JSON 형식 검증
                json.loads(content)  # JSON 파싱 테스트
                
                return content
                
            except json.JSONDecodeError as e:
                emoji_logger.warning(f"JSON 파싱 실패 (시도 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    emoji_logger.error("최대 재시도 횟수 초과")
                    
            except Exception as e:
                emoji_logger.error(f"OpenAI API 호출 실패 (시도 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    break
        
        return None
    
    def get_available_chapters(self) -> Dict[str, Dict[str, Any]]:
        """사용 가능한 챕터 정보 반환"""
        try:
            stats = rag_service.get_database_stats()
            chapter_breakdown = stats.get("chapter_breakdown", {})
            
            # 교재별로 정리
            textbook_data = {}
            
            for chapter_section, count in chapter_breakdown.items():
                parts = chapter_section.split(" ")
                if len(parts) >= 2:
                    textbook = parts[0]
                    chapter = parts[1]
                    
                    if textbook not in textbook_data:
                        textbook_data[textbook] = {}
                    
                    if chapter not in textbook_data[textbook]:
                        textbook_data[textbook][chapter] = {
                            "sections": [],
                            "file_types": [],
                            "document_count": 0
                        }
                    
                    textbook_data[textbook][chapter]["document_count"] += count
            
            # 절별 정보 추가 (절별 파일에서)
            self._add_section_info(textbook_data)
            
            return textbook_data
            
        except Exception as e:
            emoji_logger.error(f"챕터 정보 가져오기 실패: {e}")
            return {}
    
    def _add_section_info(self, textbook_data: Dict[str, Dict[str, Any]]) -> None:
        """절별 정보 추가"""
        try:
            # ChromaDB에서 절별 메타데이터 가져오기
            results = rag_service.collection.get(
                include=['metadatas'],
                where={"file_type": "절별"}
            )
            
            section_info = {}
            for metadata in results.get('metadatas', []):
                textbook = metadata.get('textbook', '')
                chapter = metadata.get('chapter', '')
                section = metadata.get('section', '')
                
                if textbook and chapter and section:
                    key = f"{textbook}_{chapter}"
                    if key not in section_info:
                        section_info[key] = set()
                    section_info[key].add(section)
            
            # 절 정보를 textbook_data에 추가
            for key, sections in section_info.items():
                textbook, chapter = key.split('_', 1)
                if textbook in textbook_data and chapter in textbook_data[textbook]:
                    textbook_data[textbook][chapter]["sections"] = sorted(list(sections))
            
        except Exception as e:
            emoji_logger.error(f"절별 정보 추가 실패: {e}")

# 전역 퀴즈 서비스 인스턴스
quiz_service = QuizService() 