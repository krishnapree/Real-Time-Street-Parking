# Backend - Real-Time Street Parking Detection API

FastAPI-based backend service for processing parking detection videos using OpenCV and YOLO.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or conda

### Installation

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download YOLO Model** (if not included)
   ```bash
   # The app will automatically download YOLOv8 on first run
   # Or manually place your model in assets/models/
   ```

4. **Run the Server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── endpoints/
│   │       │   ├── __init__.py
│   │       │   ├── upload.py      # Video upload endpoints
│   │       │   ├── processing.py  # Processing status endpoints
│   │       │   └── results.py     # Results retrieval endpoints
│   │       └── api.py       # API router
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Configuration settings
│   │   └── security.py      # Security utilities
│   ├── models/
│   │   ├── __init__.py
│   │   ├── video.py         # Video-related models
│   │   └── detection.py     # Detection result models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── video_processor.py    # Video processing service
│   │   ├── yolo_detector.py      # YOLO detection service
│   │   └── parking_analyzer.py   # Parking analysis service
│   └── utils/
│       ├── __init__.py
│       ├── file_handler.py  # File handling utilities
│       └── logger.py        # Logging configuration
├── tests/                   # Test files
├── uploads/                 # Uploaded video files
├── processed/               # Processed video outputs
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# File Storage
UPLOAD_DIR=uploads
PROCESSED_DIR=processed
MAX_FILE_SIZE=100MB

# YOLO Configuration
YOLO_MODEL_PATH=assets/models/yolov8n.pt
CONFIDENCE_THRESHOLD=0.5
IOU_THRESHOLD=0.4

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_video_processor.py -v
```

## 🚢 Deployment

### Docker Deployment

```bash
# Build image
docker build -t parking-detection-api .

# Run container
docker run -p 8000:8000 parking-detection-api
```

### Render.com Deployment

1. Connect your GitHub repository
2. Create a new Web Service
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**: Set as needed

## 📚 API Documentation

Once running, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔍 Key Features

- **Async Processing**: Non-blocking video processing
- **File Validation**: Comprehensive file type and size validation
- **Error Handling**: Robust error handling and logging
- **CORS Support**: Configurable CORS for frontend integration
- **Auto Documentation**: Automatic API documentation generation
- **Type Safety**: Full Pydantic model validation
