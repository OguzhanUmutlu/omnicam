from typing import Optional, Tuple

import numpy as np

from .base_camera import BaseCamera


class ScreenCapture(BaseCamera):
    # region: {"top": int, "left": int, "width": int, "height": int}
    def __init__(self, index=1, region: "dict[str, int] | None" = None, open=True,
                 focal_length: Optional[Tuple[float, float]] = None):
        try:
            import mss
            self.mss = mss
        except Exception as e:
            raise ImportError("mss is required for this feature. Install with 'pip install omnicam[screen]'.") from e
        super().__init__(open=open)
        self.index = index
        self.region = region
        self._focal_length = focal_length

    def _open(self):
        self.cap = self.mss.mss()
        self.monitor = self.cap.monitors[self.index]
        self.region = self.region if self.region is not None else self.monitor

    def _read(self):
        return np.array(self.cap.grab(
            {
                "top": self.monitor["top"] + self.region["top"],
                "left": self.monitor["left"] + self.region["left"],
                "width": self.region["width"],
                "height": self.region["height"]
            } if self.region is not None else self.monitor))

    def _release(self):
        self.cap.close()

    def _size(self):
        if self.region is not None:
            return self.region["width"], self.region["height"]
        return self.monitor["width"], self.monitor["height"]

    def focal_length(self):
        if self._focal_length is None:
            raise ValueError("Focal length not set for ScreenCapture")
        return self._focal_length
