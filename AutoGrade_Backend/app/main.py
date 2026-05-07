from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from .services.sarvam_service import SarvamService
from .services.evaluation_engine import EvaluationEngine
from .models.schemas import EvaluationResponse
import os
import uuid

app = FastAPI(title="AutoGrade AI API")
sarvam = SarvamService()
engine = EvaluationEngine()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"status": "AutoGrade AI Backend is Live"}

@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_papers(
    subject: str = Form(...),
    language: str = Form("en-IN"),
    teacher_sheet: UploadFile = File(...),
    student_sheet: UploadFile = File(...)
):
    """
    Takes two images, runs OCR on both using Sarvam AI, and then evaluates the student sheet.
    """
    try:
        # 1. Save uploaded files
        teacher_path = os.path.join(UPLOAD_DIR, f"teacher_{uuid.uuid4()}_{teacher_sheet.filename}")
        student_path = os.path.join(UPLOAD_DIR, f"student_{uuid.uuid4()}_{student_sheet.filename}")
        
        with open(teacher_path, "wb") as f:
            f.write(await teacher_sheet.read())
        with open(student_path, "wb") as f:
            f.write(await student_sheet.read())

        # 2. Extract Text via Sarvam AI
        print(f"Extracting teacher sheet: {teacher_path}")
        teacher_ocr = await sarvam.extract_text(teacher_path, language=language)
        
        print(f"Extracting student sheet: {student_path}")
        student_ocr = await sarvam.extract_text(student_path, language=language)

        # 3. Run Evaluation Engine
        print("Running evaluation logic...")
        evaluation_results = engine.evaluate(subject, teacher_ocr, student_ocr)

        # Cleanup
        os.remove(teacher_path)
        os.remove(student_path)

        return evaluation_results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
