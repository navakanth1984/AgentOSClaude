from sarvamai import SarvamAI
import json
import os
import time

client = SarvamAI(
    api_subscription_key=os.getenv("SARVAM_API_KEY")
)

def process_batch_ocr():
    print("\n--- Processing Full Telugu Revision Batch ---")
    zip_path = "Telugu_FA3_Full_Revision.zip"
    
    # Create job for batch
    job = client.document_intelligence.create_job(
        language="te-IN",
        output_format="html"
    )
    print(f"Job created: {job.job_id}")

    # Upload
    job.upload_file(zip_path)
    print(f"File {zip_path} uploaded")

    # Start
    job.start()
    print("Job started. This might take a minute for 5 pages...")

    # Wait for completion
    status = job.wait_until_complete()
    print(f"Job completed with state: {status.job_state}")

    # Download
    output_zip = "full_telugu_ocr_output.zip"
    job.download_output(output_zip)
    print(f"Output saved to {output_zip}")
    return output_zip

if __name__ == "__main__":
    process_batch_ocr()