import requests
import os

def test_evaluation():
    url = "http://127.0.0.1:8000/evaluate"
    
    # Using existing images from the project directory
    teacher_img = "2 Science FA2.jpeg"
    student_img = "4 Science FA2.jpeg"
    
    if not os.path.exists(teacher_img) or not os.path.exists(student_img):
        print("Test images not found in current directory.")
        return

    files = {
        'teacher_sheet': open(teacher_img, 'rb'),
        'student_sheet': open(student_img, 'rb')
    }
    
    data = {
        'subject': 'science',
        'language': 'en-IN'
    }

    print(f"Sending request to {url}...")
    response = requests.post(url, files=files, data=data)
    
    if response.status_code == 200:
        print("Evaluation Success!")
        import json
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # Note: Ensure the FastAPI server is running in another terminal before executing this
    # Command to run server: py -m uvicorn app.main:app --reload
    print("This script requires the FastAPI server to be running.")
    test_evaluation()
