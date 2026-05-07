import os
from sarvamai import SarvamAI

client = SarvamAI(
    api_subscription_key=os.getenv("SARVAM_API_KEY")
)

# Create a document intelligence job
job = client.document_intelligence.create_job(
    language="en-IN",
    output_format="html"
)
print(f"Job created: {job.job_id}")

# Upload document (using the second test PDF)
pdf_path = "test_doc_2.pdf"
job.upload_file(pdf_path)
print(f"File {pdf_path} uploaded")

# Start processing
job.start()
print("Job started")

# Wait for completion
status = job.wait_until_complete()
print(f"Job completed with state: {status.job_state}")

# Get processing metrics
metrics = job.get_page_metrics()
print(f"Page metrics: {metrics}")

# Download output (ZIP file containing the processed document)
job.download_output("./output_pdf.zip")
print("Output saved to ./output_pdf.zip")