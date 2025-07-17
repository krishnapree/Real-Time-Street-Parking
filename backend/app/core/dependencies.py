"""
Dependency injection for FastAPI
"""

from app.services.video_processor import VideoProcessor

# Global singleton instance
_video_processor_instance = None

def get_video_processor() -> VideoProcessor:
    """Get the global video processor instance"""
    global _video_processor_instance
    if _video_processor_instance is None:
        _video_processor_instance = VideoProcessor()
        # Initialize the processor
        try:
            _video_processor_instance.initialize()
        except Exception as e:
            print(f"Warning: Failed to initialize video processor: {e}")
            # Continue anyway for basic functionality
    return _video_processor_instance
