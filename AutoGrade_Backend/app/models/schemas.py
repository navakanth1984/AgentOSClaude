from pydantic import BaseModel
from typing import List, Optional, Dict

class Coordinate(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

class OCRBlock(BaseModel):
    block_id: str
    text: str
    coordinates: Coordinate
    layout_tag: str
    confidence: float

class EvaluationRequest(BaseModel):
    subject: str # math, science, social
    teacher_ocr_data: List[OCRBlock]
    student_ocr_data: List[OCRBlock]

class MarkAnnotation(BaseModel):
    type: str # tick, cross, circle
    coordinates: Coordinate
    comment: Optional[str] = None

class QuestionEvaluation(BaseModel):
    question_id: str
    student_answer: str
    marks_awarded: float
    max_marks: float
    feedback: str
    annotations: List[MarkAnnotation]

class EvaluationResponse(BaseModel):
    total_score: float
    max_score: float
    results: List[QuestionEvaluation]
