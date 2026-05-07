from sarvamai import SarvamAI
import json
import os

client = SarvamAI(
    api_subscription_key=os.getenv("SARVAM_API_KEY")
)

def process_science_fa2_te():
    print("")
    print("--- Processing Science FA2 with te-IN to capture all text ---")
    zip_path = "science_fa2_revision.zip"
    
    job = client.document_intelligence.create_job(
        language="te-IN",
        output_format="html"
    )
    print(f"Job created: {job.job_id}")

    job.upload_file(zip_path)
    job.start()
    status = job.wait_until_complete()
    print(f"Job completed with state: {status.job_state}")

    output_zip = "science_fa2_te_output.zip"
    job.download_output(output_zip)
    print(f"Output saved to {output_zip}")

if __name__ == "__main__":
    process_science_fa2_te()
