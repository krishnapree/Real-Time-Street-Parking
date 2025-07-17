"""
API endpoint tests
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import os

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_supported_formats():
    """Test supported formats endpoint"""
    response = client.get("/api/v1/upload/supported-formats")
    assert response.status_code == 200
    data = response.json()
    assert "supported_formats" in data
    assert "max_file_size" in data


def test_upload_no_file():
    """Test upload endpoint with no file"""
    response = client.post("/api/v1/upload/")
    assert response.status_code == 422  # Validation error


def test_upload_invalid_file():
    """Test upload endpoint with invalid file"""
    # Create a temporary text file
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
        tmp_file.write(b"This is not a video file")
        tmp_file_path = tmp_file.name
    
    try:
        with open(tmp_file_path, "rb") as f:
            response = client.post(
                "/api/v1/upload/",
                files={"file": ("test.txt", f, "text/plain")}
            )
        assert response.status_code == 400
        data = response.json()
        assert "Unsupported file format" in data["detail"]
    finally:
        os.unlink(tmp_file_path)


def test_get_nonexistent_job_status():
    """Test getting status for non-existent job"""
    response = client.get("/api/v1/processing/nonexistent-job-id")
    assert response.status_code == 404


def test_get_nonexistent_results():
    """Test getting results for non-existent job"""
    response = client.get("/api/v1/results/nonexistent-job-id")
    assert response.status_code == 404


def test_get_all_processing_status():
    """Test getting all processing status"""
    response = client.get("/api/v1/processing/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_video_upload_and_processing():
    """Test complete video upload and processing workflow"""
    # This would require a sample video file
    # For now, we'll skip this test
    pytest.skip("Requires sample video file")


if __name__ == "__main__":
    pytest.main([__file__])
