"""
Video processor service tests
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from app.services.video_processor import VideoProcessor
from app.models.video import VideoProcessingRequest, JobStatus


@pytest.fixture
def video_processor():
    """Create video processor instance for testing"""
    return VideoProcessor()


@pytest.fixture
def sample_video_path(tmp_path):
    """Create a sample video file for testing"""
    video_file = tmp_path / "test_video.mp4"
    video_file.write_bytes(b"fake video content")
    return video_file


@pytest.fixture
def processing_config():
    """Create sample processing configuration"""
    return VideoProcessingRequest(
        confidence_threshold=0.5,
        iou_threshold=0.4,
        frame_skip=1,
        output_format="mp4"
    )


class TestVideoProcessor:
    """Test video processor functionality"""
    
    @pytest.mark.asyncio
    async def test_initialization(self, video_processor):
        """Test video processor initialization"""
        assert video_processor.jobs == {}
        assert video_processor.results == {}
        assert video_processor.processing_tasks == {}
        assert not video_processor._model_loaded
    
    @pytest.mark.asyncio
    async def test_start_processing_without_model(self, video_processor, sample_video_path, processing_config):
        """Test starting processing without loaded model"""
        job_id = "test-job-123"
        
        with patch.object(video_processor, 'initialize', new_callable=AsyncMock) as mock_init:
            mock_init.return_value = None
            video_processor._model_loaded = True
            
            result = await video_processor.start_processing(job_id, sample_video_path, processing_config)
            
            assert result is True
            assert job_id in video_processor.jobs
            assert video_processor.jobs[job_id].status == JobStatus.PENDING
            mock_init.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_job_status(self, video_processor):
        """Test getting job status"""
        job_id = "test-job-123"
        
        # Test non-existent job
        status = await video_processor.get_job_status(job_id)
        assert status is None
        
        # Test existing job
        from app.models.video import ProcessingStatus
        from datetime import datetime
        
        test_status = ProcessingStatus(
            job_id=job_id,
            status=JobStatus.PENDING,
            progress=0.0,
            created_at=datetime.utcnow()
        )
        video_processor.jobs[job_id] = test_status
        
        status = await video_processor.get_job_status(job_id)
        assert status == test_status
    
    @pytest.mark.asyncio
    async def test_get_all_job_status(self, video_processor):
        """Test getting all job statuses"""
        # Test empty jobs
        statuses = await video_processor.get_all_job_status()
        assert statuses == []
        
        # Test with jobs
        from app.models.video import ProcessingStatus
        from datetime import datetime
        
        job1 = ProcessingStatus(
            job_id="job1",
            status=JobStatus.PENDING,
            progress=0.0,
            created_at=datetime.utcnow()
        )
        job2 = ProcessingStatus(
            job_id="job2",
            status=JobStatus.PROCESSING,
            progress=50.0,
            created_at=datetime.utcnow()
        )
        
        video_processor.jobs["job1"] = job1
        video_processor.jobs["job2"] = job2
        
        statuses = await video_processor.get_all_job_status()
        assert len(statuses) == 2
        assert job1 in statuses
        assert job2 in statuses
    
    @pytest.mark.asyncio
    async def test_cancel_job(self, video_processor):
        """Test job cancellation"""
        job_id = "test-job-123"
        
        # Test cancelling non-existent job
        result = await video_processor.cancel_job(job_id)
        assert result is False
        
        # Test cancelling existing job
        mock_task = Mock()
        video_processor.processing_tasks[job_id] = mock_task
        
        from app.models.video import ProcessingStatus
        from datetime import datetime
        
        test_status = ProcessingStatus(
            job_id=job_id,
            status=JobStatus.PROCESSING,
            progress=50.0,
            created_at=datetime.utcnow()
        )
        video_processor.jobs[job_id] = test_status
        
        result = await video_processor.cancel_job(job_id)
        assert result is True
        assert video_processor.jobs[job_id].status == JobStatus.FAILED
        assert "cancelled" in video_processor.jobs[job_id].error_message
        mock_task.cancel.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_job_results(self, video_processor, tmp_path):
        """Test deleting job results"""
        job_id = "test-job-123"
        
        # Create test data
        from app.models.video import ProcessingStatus
        from app.models.detection import VideoAnalysisResult
        from datetime import datetime
        
        test_status = ProcessingStatus(
            job_id=job_id,
            status=JobStatus.COMPLETED,
            progress=100.0,
            created_at=datetime.utcnow()
        )
        
        test_result = VideoAnalysisResult(
            job_id=job_id,
            video_info={},
            frames_analyzed=100,
            total_frames=100,
            processing_time=10.0,
            avg_total_spaces=10.0,
            avg_occupied_spaces=5.0,
            avg_available_spaces=5.0,
            avg_occupancy_rate=0.5,
            max_occupancy=0.8,
            min_occupancy=0.2,
            peak_occupied_spaces=8
        )
        
        video_processor.jobs[job_id] = test_status
        video_processor.results[job_id] = test_result
        
        # Create test files
        test_file = tmp_path / f"{job_id}_test.txt"
        test_file.write_text("test content")
        
        with patch('app.services.video_processor.Path') as mock_path:
            mock_path.return_value.glob.return_value = [test_file]
            
            result = await video_processor.delete_job_results(job_id)
            
            assert result is True
            assert job_id not in video_processor.jobs
            assert job_id not in video_processor.results


@pytest.mark.asyncio
async def test_video_processor_integration():
    """Integration test for video processor"""
    processor = VideoProcessor()
    
    # Mock the YOLO detector and parking analyzer
    with patch.object(processor.yolo_detector, 'load_model', new_callable=AsyncMock) as mock_load:
        mock_load.return_value = True
        
        await processor.initialize()
        assert processor._model_loaded is True
        mock_load.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
