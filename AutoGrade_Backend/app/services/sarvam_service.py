from sarvamai import SarvamAI
import os
import zipfile
import shutil
from typing import List
from ..models.schemas import OCRBlock, Coordinate

class SarvamService:
    def __init__(self):
        self.api_key = os.getenv("SARVAM_API_KEY")
        self.client = SarvamAI(api_subscription_key=self.api_key)

    async def extract_text(self, file_path: str, language: str = "en-IN") -> List[OCRBlock]:
        """
        Uploads a file (must be zipped if image) to Sarvam AI and returns structured OCR blocks.
        """
        # 1. Ensure file is a ZIP (Sarvam constraint for images)
        if not file_path.endswith('.zip'):
            zip_path = file_path + ".zip"
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                zipfile_name = os.path.basename(file_path)
                zipf.write(file_path, arcname=zipfile_name)
            file_to_upload = zip_path
        else:
            file_to_upload = file_path

        # 2. Create and run job
        job = self.client.document_intelligence.create_job(
            language=language,
            output_format="html"
        )
        job.upload_file(file_to_upload)
        job.start()
        
        # Non-blocking wait (Fix for Bug B)
        import asyncio
        while True:
            status = job.get_status()
            if status.job_state == "Completed":
                break
            if status.job_state in ["Failed", "Cancelled"]:
                raise Exception(f"Sarvam AI job terminated with state: {status.job_state}")
            await asyncio.sleep(2) # Poll every 2 seconds

        # 3. Download and parse results
        output_dir = "temp_sarvam_output"
        os.makedirs(output_dir, exist_ok=True)
        job.download_output(os.path.join(output_dir, "output.zip"))
        
        with zipfile.ZipFile(os.path.join(output_dir, "output.zip"), 'r') as zip_ref:
            zip_ref.extractall(output_dir)

        # 4. Parse the first page JSON for blocks
        import json
        metadata_file = os.path.join(output_dir, "metadata", "page_001.json")
        with open(metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        blocks = []
        for b in data.get('blocks', []):
            blocks.append(OCRBlock(
                block_id=b['block_id'],
                text=b['text'],
                coordinates=Coordinate(**b['coordinates']),
                layout_tag=b['layout_tag'],
                confidence=b['confidence']
            ))

        # Cleanup
        shutil.rmtree(output_dir)
        if not file_path.endswith('.zip'):
            os.remove(file_to_upload)

        return blocks
