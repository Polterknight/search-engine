import math
from typing import List, Dict
from ..models.document import Document, SearchResult

class TFIDFRanker:
    """Ранжирование документов по TF-IDF"""
    
    def rank(self, query_terms: List[str], index, limit: int = 10) -> List[SearchResult]:
        """Ранжирование документов для запроса"""
        scores: Dict[str, float] = {}
        
        for term in query_terms:
            if term not in index.terms:
                continue
                
            # IDF вычисление
            doc_freq = len(index.terms[term])
            idf = math.log(index.total_docs / (doc_freq + 1))
            
            # TF вычисление для каждого документа
            for doc_id, tf in index.terms[term].items():
                doc = index.documents[doc_id]
                tf_score = tf / doc.term_count
                scores[doc_id] = scores.get(doc_id, 0) + tf_score * idf
        
        # Сортировка и формирование результатов
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [
            SearchResult(
                document=index.documents[doc_id],
                score=score,
                snippet=self._generate_snippet(index.documents[doc_id].text, query_terms)
            ) for doc_id, score in sorted_docs
        ]
    
    def _generate_snippet(self, text: str, query_terms: List[str]) -> str:
        """Генерация сниппета с подсветкой запросных терминов"""
        words = text.split()
        if len(words) > 10:  # Берем первые 10 слов
            return ' '.join(words[:10]) + '...'
        return text