import platform

from .base_camera import CameraInfo
from .cv_camera_base import CVCameraBase


class SimpleCamera(CVCameraBase):
    def __init__(self, index=0, open=True, info: CameraInfo = None):
        try:
            import cv2
        except Exception as exc:
            raise ImportError(
                "OpenCV is required for this feature. Install with 'pip install omnicam[opencv]'."
            ) from exc
        args = [index, cv2.CAP_DSHOW] if platform.system() == "Windows" else [index, cv2.CAP_V4L2]
        try:
            super().__init__(args, open=open, info=info)
        except Exception as e:
            raise RuntimeError(f"Camera with index {index} could not be opened: {e}") from e
        self.index = index
