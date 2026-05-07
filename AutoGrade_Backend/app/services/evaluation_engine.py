import sympy
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List
from ..models.schemas import OCRBlock, QuestionEvaluation, EvaluationResponse, MarkAnnotation, Coordinate

class EvaluationEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.banned_words = {"offensive", "badword", "abuse"} # Expand in production

    def evaluate(self, subject: str, teacher_blocks: List[OCRBlock], student_blocks: List[OCRBlock]) -> EvaluationResponse:
        # 1. Safety Layer
        all_student_text = " ".join([b.text for b in student_blocks])
        if self._contains_profanity(all_student_text):
            return self._generate_safety_rejection()

        results = []
        total_score = 0.0
        max_score = 0.0

        # 2. Semantic Block Matching (Fix for Bug A)
        # We match each teacher block to the BEST student block based on text similarity
        # This allows for skipped questions or extra student notes.
        for t_block in teacher_blocks:
            if t_block.layout_tag not in ['paragraph', 'list_item', 'image']:
                continue
            
            max_score += 1.0
            best_match = self._find_best_match(t_block, student_blocks)
            
            if not best_match:
                results.append(self._generate_empty_result(t_block))
                continue

            # 3. Grade the best match
            score, feedback = self._grade_block(subject, t_block, best_match)
            total_score += score
            
            results.append(QuestionEvaluation(
                question_id=t_block.block_id,
                student_answer=best_match.text,
                marks_awarded=score,
                max_marks=1.0,
                feedback=feedback,
                annotations=[MarkAnnotation(
                    type="tick" if score > 0.7 else "cross" if score < 0.3 else "circle",
                    coordinates=best_match.coordinates
                )]
            ))

        return EvaluationResponse(total_score=total_score, max_score=max_score, results=results)

    def _find_best_match(self, teacher_block: OCRBlock, student_blocks: List[OCRBlock]) -> OCRBlock:
        """Finds the student block that most likely answers the teacher's block."""
        if not student_blocks: return None
        
        t_text = teacher_block.text
        s_texts = [b.text for b in student_blocks]
        
        try:
            tfidf = self.vectorizer.fit_transform([t_text] + s_texts)
            similarities = cosine_similarity(tfidf[0:1], tfidf[1:])
            best_idx = similarities.argmax()
            
            # Threshold: if match is extremely poor, consider it not answered
            if similarities[0][best_idx] < 0.15:
                return None
            return student_blocks[best_idx]
        except:
            return None

    def _grade_block(self, subject: str, t_block: OCRBlock, s_block: OCRBlock):
        if t_block.layout_tag == "image":
            return self._evaluate_diagram(t_block.text, s_block.text)
        if subject.lower() == "math":
            return self._evaluate_math(t_block.text, s_block.text)
        return self._evaluate_semantic(t_block.text, s_block.text)

    def _evaluate_math(self, t_text: str, s_text: str):
        try:
            # Clean symbols (Fix for Bug C)
            def clean(txt):
                txt = re.sub(r'[\$→\(\)]', '', txt.lower())
                return txt.split('=')[-1].strip()

            t_final = clean(t_text)
            s_final = clean(s_text)

            t_expr = sympy.simplify(t_final)
            s_expr = sympy.simplify(s_final)
            
            if (t_expr - s_expr) == 0:
                return 1.0, "Mathematically equivalent."
            return 0.0, "Result mismatch."
        except:
            return (1.0, "String Match") if t_text.strip() == s_text.strip() else (0.0, "Wrong")

    def _evaluate_semantic(self, t_text: str, s_text: str):
        # Hybrid Similarity
        tfidf = self.vectorizer.fit_transform([t_text, s_text])
        sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        
        if sim > 0.75: return 1.0, "Correct."
        if sim > 0.35: return 0.5, "Partial credit (Keyword match)."
        return 0.0, "Incorrect."

    def _evaluate_diagram(self, t_desc: str, s_desc: str):
        t_set = set(t_desc.lower().split())
        s_set = set(s_desc.lower().split())
        overlap = len(t_set.intersection(s_set)) / len(t_set) if t_set else 1.0
        if overlap > 0.6: return 1.0, "Diagram labels match."
        return 0.5, "Incomplete diagram."

    def _contains_profanity(self, text: str) -> bool:
        return not set(text.lower().split()).isdisjoint(self.banned_words)

    def _generate_safety_rejection(self):
        return EvaluationResponse(total_score=0, max_score=0, results=[QuestionEvaluation(
            question_id="ERR", student_answer="", marks_awarded=0, max_marks=0, 
            feedback="REJECTED: Profanity detected.", annotations=[]
        )])

    def _generate_empty_result(self, t_block: OCRBlock):
        return QuestionEvaluation(
            question_id=t_block.block_id, student_answer="NOT FOUND",
            marks_awarded=0, max_marks=1.0, feedback="Question not answered.", annotations=[]
        )
