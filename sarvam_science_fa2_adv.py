from sarvamai import SarvamAI
import json
import os

client = SarvamAI(
    api_subscription_key=os.getenv("SARVAM_API_KEY")
)

def process_science_fa2_advanced():
    print("")
    print("--- Advanced Processing Science FA2 (Markdown + te-IN) ---")
    zip_path = "science_fa2_revision.zip"
    
    # Try with Telugu + English combined or auto
    job = client.document_intelligence.create_job(
        language="auto",
        output_format="markdown"
    )
    print(f"Job created: {job.job_id}")

    job.upload_file(zip_path)
    job.start()
    print("Job started...")

    status = job.wait_until_complete()
    print(f"Job completed with state: {status.job_state}")

    output_zip = "science_fa2_advanced_output.zip"
    job.download_output(output_zip)
    print(f"Output saved to {output_zip}")

if __name__ == "__main__":
    process_science_fa2_advanced()
