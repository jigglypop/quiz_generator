"""
RAG (Retrieval-Augmented Generation) 서비스
"""
import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

from src.config.settings import settings
from src.models.schemas import DocumentChunk
from src.utils.logger import emoji_logger

class RAGService:
    """한국어 금융교재 RAG 시스템"""
    
    def __init__(self):
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        self.document_stats = {}
        
    async def initialize(self) -> None:
        """RAG 시스템 초기화"""
        try:
            emoji_logger.startup("한국어 금융교재 퀴즈 생성기 시작")
            emoji_logger.config(f"OpenAI API 키: {'설정됨' if settings.is_openai_configured else '미설정'}")
            
            # ChromaDB 클라이언트 초기화
            self._initialize_chroma()
            
            # 임베딩 모델 로드
            self._load_embedding_model()
            
            # 데이터베이스 상태 확인
            await self._check_and_load_data()
            
            emoji_logger.success("전체 설정 완료!")
            
        except Exception as e:
            emoji_logger.error(f"RAG 시스템 초기화 실패: {e}")
            raise
    
    def _initialize_chroma(self) -> None:
        """ChromaDB 초기화"""
        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_DB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 컬렉션 가져오기 또는 생성
        try:
            self.collection = self.chroma_client.get_collection(settings.COLLECTION_NAME)
        except:
            self.collection = self.chroma_client.create_collection(
                name=settings.COLLECTION_NAME,
                metadata={"description": "Korean Financial Textbooks"}
            )
    
    def reset_database(self) -> None:
        """데이터베이스 재설정"""
        try:
            emoji_logger.processing("데이터베이스를 재설정합니다...")
            
            # 기존 컬렉션 삭제
            try:
                self.chroma_client.delete_collection(settings.COLLECTION_NAME)
                emoji_logger.success("기존 컬렉션 삭제 완료")
            except:
                pass
            
            # 새 컬렉션 생성
            self.collection = self.chroma_client.create_collection(
                name=settings.COLLECTION_NAME,
                metadata={"description": "Korean Financial Textbooks"}
            )
            
            # 통계 초기화
            self.document_stats = {}
            
            emoji_logger.success("데이터베이스 재설정 완료")
            
        except Exception as e:
            emoji_logger.error(f"데이터베이스 재설정 실패: {e}")
            raise
    
    def _load_embedding_model(self) -> None:
        """임베딩 모델 로드"""
        emoji_logger.ai("임베딩 모델 로딩 중...")
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        emoji_logger.success("임베딩 모델 로드 완료")
    
    async def _check_and_load_data(self) -> None:
        """데이터베이스 상태 확인 및 데이터 로딩"""
        try:
            current_count = self.collection.count()
            emoji_logger.stats(f"현재 데이터베이스 문서 수: {current_count}")
            
            if current_count == 0:
                emoji_logger.processing("데이터베이스가 비어있습니다. 데이터를 다시 로딩합니다...")
                await self._load_textbook_data()
            else:
                # 기존 데이터가 있으면 통계 업데이트
                emoji_logger.processing("기존 데이터베이스에서 통계를 업데이트합니다...")
                self._update_document_stats()
            
        except Exception as e:
            emoji_logger.error(f"데이터 확인 중 오류: {e}")
            raise
    
    async def _load_textbook_data(self) -> None:
        """교재 데이터 로딩"""
        all_chunks = []
        
        emoji_logger.loading("교재 파일 로딩 중...")
        
        for textbook_dir in settings.TEXTBOOK_DIRS:
            if not os.path.exists(textbook_dir):
                emoji_logger.warning(f"디렉토리가 존재하지 않습니다: {textbook_dir}")
                continue
                
            chunks = await self._load_directory_files(textbook_dir)
            all_chunks.extend(chunks)
        
        if not all_chunks:
            emoji_logger.error("로드된 문서가 없습니다!")
            return
        
        emoji_logger.success(f"{len(all_chunks)}개 파일 로딩 완료")
        
        # 문서 청킹
        document_chunks = self._chunk_documents(all_chunks)
        
        # 임베딩 생성 및 저장
        await self._generate_and_store_embeddings(document_chunks)
    
    async def _load_directory_files(self, directory: str) -> List[Dict[str, Any]]:
        """디렉토리의 마크다운 파일들 로딩"""
        chunks = []
        textbook_type = self._get_textbook_type(directory)
        file_type = "장별통합" if "장별통합" in directory else "절별"
        
        emoji_logger.loading(f"{textbook_type} ({file_type}) 파일 로딩 중...")
        
        for file_path in Path(directory).glob("*.md"):
            try:
                content = self._read_markdown_file(file_path)
                if content.strip():
                    metadata = self._extract_metadata(file_path.name, textbook_type, file_type)
                    
                    chunks.append({
                        "content": content,
                        "metadata": metadata
                    })
                    
                    emoji_logger.file(f"{textbook_type} ({file_type}): {metadata['display_name']}")
                    
            except Exception as e:
                emoji_logger.error(f"파일 로딩 실패 {file_path}: {e}")
        
        emoji_logger.folder(f"{textbook_type} ({file_type}): {len(chunks)}개 파일 로드 완료")
        return chunks
    
    def _get_textbook_type(self, directory: str) -> str:
        """디렉토리 경로에서 교재 타입 추출"""
        if "신탁교재" in directory:
            return "신탁교재"
        elif "퇴직연금교재" in directory:
            return "퇴직연금교재"
        return "unknown"
    
    def _read_markdown_file(self, file_path: Path) -> str:
        """마크다운 파일 읽기"""
        encodings = ['utf-8', 'cp949', 'euc-kr']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        raise ValueError(f"파일 인코딩을 인식할 수 없습니다: {file_path}")
    
    def _extract_metadata(self, filename: str, textbook_type: str, file_type: str) -> Dict[str, Any]:
        """파일명에서 메타데이터 추출"""
        # 기본 메타데이터
        metadata = {
            "filename": filename,
            "textbook": textbook_type,
            "file_type": file_type,
            "chapter": "",
            "section": "",
            "display_name": "",
            "chapter_section": ""
        }
        
        # 파일명 패턴 분석
        if file_type == "장별통합":
            # 제1장.md 형태
            chapter_match = re.search(r'제(\d+)장', filename)
            if chapter_match:
                chapter_num = chapter_match.group(1)
                metadata["chapter"] = f"제{chapter_num}장"
                metadata["display_name"] = f"제{chapter_num}장"
                
        else:  # 절별
            # 제1장_제1절_내용.md 형태
            parts = filename.replace('.md', '').split('_')
            if len(parts) >= 2:
                chapter_part = parts[0]  # 제1장
                section_part = parts[1]  # 제1절
                
                metadata["chapter"] = chapter_part
                metadata["section"] = section_part
                metadata["display_name"] = f"{chapter_part} {section_part} - {parts[2] if len(parts) > 2 else ''}"
        
        # chapter_section 조합 생성
        metadata["chapter_section"] = f"{textbook_type} {metadata['chapter']}"
        
        return metadata
    
    def _chunk_documents(self, documents: List[Dict[str, Any]]) -> List[DocumentChunk]:
        """문서를 청크로 분할"""
        emoji_logger.chunk("문서 청킹 중...")
        
        all_chunks = []
        chunk_id = 0
        
        for doc in documents:
            content = doc["content"]
            metadata = doc["metadata"]
            
            # 내용 정리
            cleaned_content = self._clean_content(content)
            
            # 청크 크기별로 분할 (800자씩)
            chunk_size = 800
            overlap = 100
            
            for i in range(0, len(cleaned_content), chunk_size - overlap):
                chunk_content = cleaned_content[i:i + chunk_size]
                
                if len(chunk_content.strip()) < 50:  # 너무 짧은 청크 제외
                    continue
                
                chunk = DocumentChunk(
                    id=f"chunk_{chunk_id}",
                    content=chunk_content,
                    metadata={**metadata, "chunk_index": i // (chunk_size - overlap)}
                )
                
                all_chunks.append(chunk)
                chunk_id += 1
        
        emoji_logger.success(f"{len(all_chunks)}개 청크 생성 완료")
        return all_chunks
    
    def _clean_content(self, content: str) -> str:
        """콘텐츠 정리"""
        # > 주의, > 참고 등 제거
        content = re.sub(r'>\s*(주의|참고|노트|팁)[^\n]*\n?', '', content)
        
        # 여러 줄바꿈을 하나로
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 불필요한 공백 제거
        content = re.sub(r'[ \t]+', ' ', content)
        
        return content.strip()
    
    async def _generate_and_store_embeddings(self, chunks: List[DocumentChunk]) -> None:
        """임베딩 생성 및 벡터 DB 저장"""
        if not chunks:
            return
        
        emoji_logger.ai("임베딩 생성 중...")
        emoji_logger.ai(f"{len(chunks)}개 청크의 임베딩 생성 중...")
        
        # 임베딩 생성
        contents = [chunk.content for chunk in chunks]
        embeddings = self.embedding_model.encode(contents, show_progress_bar=True)
        
        emoji_logger.success("임베딩 생성 완료")
        
        # ChromaDB에 저장
        emoji_logger.database("벡터 DB 저장 중...")
        
        ids = [chunk.id for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        
        # 배치로 저장 (ChromaDB 제한 고려)
        batch_size = 1000
        for i in range(0, len(chunks), batch_size):
            batch_end = min(i + batch_size, len(chunks))
            
            self.collection.add(
                ids=ids[i:batch_end],
                documents=contents[i:batch_end],
                metadatas=metadatas[i:batch_end],
                embeddings=embeddings[i:batch_end].tolist()
            )
        
        emoji_logger.success(f"{len(chunks)}개 청크를 벡터 DB에 저장했습니다.")
        
        # 통계 업데이트
        self._update_document_stats()
    
    def _update_document_stats(self) -> None:
        """문서 통계 업데이트"""
        try:
            results = self.collection.get(include=['metadatas'])
            
            stats = {}
            for metadata in results['metadatas']:
                chapter_section = metadata.get('chapter_section', 'Unknown')
                if chapter_section and chapter_section != 'Unknown':
                    stats[chapter_section] = stats.get(chapter_section, 0) + 1
            
            self.document_stats = stats
            emoji_logger.debug(f"문서 통계 업데이트 완료: {len(stats)}개 챕터")
            
        except Exception as e:
            emoji_logger.error(f"통계 업데이트 실패: {e}")
            self.document_stats = {}
    
    def get_database_stats(self) -> Dict[str, Any]:
        """데이터베이스 통계 반환"""
        total_docs = self.collection.count() if self.collection else 0
        
        return {
            "total_documents": total_docs,
            "chapter_breakdown": self.document_stats,
            "embedding_model": settings.EMBEDDING_MODEL,
            "collection_name": settings.COLLECTION_NAME
        }
    
    async def search_documents(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """문서 검색"""
        try:
            # 쿼리 임베딩 생성
            query_embedding = self.embedding_model.encode([query])
            
            # 유사도 검색
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            return {
                "documents": results["documents"][0] if results["documents"] else [],
                "metadatas": results["metadatas"][0] if results["metadatas"] else [],
                "distances": results["distances"][0] if results["distances"] else []
            }
            
        except Exception as e:
            emoji_logger.error(f"문서 검색 실패: {e}")
            return {"documents": [], "metadatas": [], "distances": []}
    
    def get_chapter_content(self, textbook: str, chapter: str, limit: int = 50) -> List[str]:
        """특정 장의 콘텐츠 가져오기"""
        try:
            chapter_section = f"{textbook} {chapter}"
            
            emoji_logger.search(f"'{chapter_section}' 챕터 데이터 검색 중...")
            emoji_logger.stats(f"전체 문서 수: {self.collection.count()}")
            emoji_logger.stats(f"교재/챕터별 문서 수: {self.document_stats}")
            
            # ChromaDB에서 검색
            results = self.collection.get(
                where={"chapter_section": chapter_section},
                limit=limit,
                include=["documents"]
            )
            
            contents = results.get("documents", [])
            emoji_logger.target(f"'{chapter_section}' 챕터 문서 수: {len(contents)}")
            
            return contents
            
        except Exception as e:
            emoji_logger.error(f"챕터 콘텐츠 검색 실패: {e}")
            return []
    
    def get_section_content(self, textbook: str, chapter: str, section: str, limit: int = 30) -> List[str]:
        """특정 절의 콘텐츠 가져오기"""
        try:
            emoji_logger.search(f"'{textbook} {chapter} {section}' 절별 데이터 검색 중...")
            
            # 절별 파일에서 해당하는 내용 검색
            results = self.collection.get(
                where={
                    "$and": [
                        {"textbook": textbook},
                        {"chapter": chapter},
                        {"section": section}
                    ]
                },
                limit=limit,
                include=["documents"]
            )
            
            contents = results.get("documents", [])
            emoji_logger.target(f"'{textbook} {chapter} {section}' 절 문서 수: {len(contents)}")
            
            return contents
            
        except Exception as e:
            emoji_logger.error(f"절별 콘텐츠 검색 실패: {e}")
            return []

# 전역 RAG 서비스 인스턴스
rag_service = RAGService() 