# LTX-Video Generator App

A cross-platform (Web, Mobile, Desktop) application for generating videos using the open-source LTX-Video model.

## Architecture

- **Backend:** FastAPI server wrapping the LTX-Video inference logic. Handles job queueing and file serving.
- **Frontend:** Flutter application for all platforms. Provides a user-friendly interface to set parameters and monitor generation progress.

## Prerequisites

- Python 3.10+
- Flutter SDK
- CUDA-compatible GPU (recommended for video generation)
- Git

## Setup

### 1. Clone LTX-Video and Install Dependencies

```bash
git clone https://github.com/Lightricks/LTX-Video.git ltx_video_source
cd ltx_video_source
pip install -e .
pip install imageio[ffmpeg] av torchvision fastapi uvicorn pydantic python-multipart sqlite3
```

### 2. Start the Backend API

```bash
cd ltx_video_api
python main.py
```

The backend will automatically:
- Create `jobs.db` for persistence.
- Scan `ltx_video_source/configs` for available model configurations.
- Create `uploads/` and `outputs/` directories.

The API runs on `http://localhost:8000`.

### 3. Run the Flutter Application

```bash
cd ltx_video_app
flutter run
```

## New Pro Features

- **Persistence:** Jobs are saved in a local SQLite database and survive server restarts.
- **History View:** Access and replay previous generations from the 'History' tab.
- **Integrated Video Player:** Preview results directly in the app using Chewie/VideoPlayer.
- **Model Selection:** Choose between different LTX-Video model variants (e.g., 2b, 13b, distilled, fp8) via a dropdown.
- **Advanced Settings:** Fine-tune seed, resolution, and frames from a collapsable panel.

## Troubleshooting

- **GPU Memory:** If you run out of VRAM, try lowering the resolution or setting `Offload to CPU` to true.
- **CORS:** The backend is configured to allow all origins by default for local development. For production, restrict it to your frontend domain.
