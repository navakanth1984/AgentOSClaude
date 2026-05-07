from sarvamai import SarvamAI
import json
import os

client = SarvamAI(
    api_subscription_key=os.getenv("SARVAM_API_KEY")
)

def process_science_fa2():
    print("")
    print("--- Processing Science FA2 Revision with Sarvam AI ---")
    zip_path = "science_fa2_revision.zip"
    
    # Create job
    job = client.document_intelligence.create_job(
        language="en-IN",
        output_format="html"
    )
    print(f"Job created: {job.job_id}")

    # Upload
    job.upload_file(zip_path)
    print(f"File {zip_path} uploaded")

    # Start
    job.start()
    print("Job started. Waiting for completion...")

    # Wait
    status = job.wait_until_complete()
    print(f"Job completed with state: {status.job_state}")

    # Download
    output_zip = "science_fa2_output.zip"
    job.download_output(output_zip)
    print(f"Output saved to {output_zip}")

if __name__ == "__main__":
    process_science_fa2()
