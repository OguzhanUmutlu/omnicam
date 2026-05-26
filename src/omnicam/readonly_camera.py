from typing import Tuple

from .base_camera import BaseCamera


class ReadonlyCamera(BaseCamera):
    def __init__(self, cam: BaseCamera):
        self.cam = cam
        super().__init__()

    def _open(self):
        pass

    def _read(self):
        return self.cam._read()

    def _release(self):
        pass

    def _size(self):
        return self.cam._size()

    def _focus(self, rectangle: Tuple[int, int, int, int]):
        self.cam._focus(rectangle)

    def focal_length(self):
        return self.cam.focal_length()
