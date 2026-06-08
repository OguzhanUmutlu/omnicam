from .base_camera import BaseCamera, resolutions, CameraInfo, calc_focal_length_px


def _v1_v2_fps(camera: BaseCamera) -> float:
    pixels = camera.width * camera.height
    if pixels <= 640 * 480: return 90.0
    if pixels <= 1280 * 720: return 60.0
    if pixels <= 1920 * 1080: return 30.0
    return 15.0


def _v3_fps(camera: BaseCamera) -> float:
    pixels = camera.width * camera.height
    if pixels <= 640 * 480: return 120.0
    if pixels <= 1280 * 720: return 100.0
    if pixels <= 1920 * 1080: return 50.0
    return 30.0


def _hq_fps(camera: BaseCamera) -> float:
    pixels = camera.width * camera.height
    if pixels <= 1280 * 720: return 120.0
    if pixels <= 1920 * 1080: return 50.0
    if pixels <= 2028 * 1520: return 40.0
    return 10.0


_gs_fps = lambda camera: 120.0 if (camera.width * camera.height) <= 1280 * 720 else 60.0
_ai_fps = lambda camera: 30.0 if (camera.width * camera.height) <= 1920 * 1080 else 10.0


class PiCamera(BaseCamera):
    rpi_camera_definitions = [
        CameraInfo(
            name="Camera Module 1", short_names=["OV5647", "1"],
            focal_length_px=calc_focal_length_px((3.60, 3.60), 1.40), pixel_size_um=1.40,
            resolutions=[], max_resolution=(2592, 1944), update_rate=_v1_v2_fps,
            aperture_f=2.9, hfov_deg=53.5, focus_type="Fixed", has_ir_filter=True
        ),
        CameraInfo(
            name="Camera Module 1 NoIR", short_names=["OV5647 NoIR", "1N"],
            focal_length_px=calc_focal_length_px((3.60, 3.60), 1.40), pixel_size_um=1.40,
            resolutions=[], max_resolution=(2592, 1944), update_rate=_v1_v2_fps,
            aperture_f=2.9, hfov_deg=53.5, focus_type="Fixed", has_ir_filter=False
        ),
        CameraInfo(
            name="Camera Module 2", short_names=["IMX219", "2"],
            focal_length_px=calc_focal_length_px((3.04, 3.04), 1.12), pixel_size_um=1.12,
            resolutions=[], max_resolution=(3280, 2464), update_rate=_v1_v2_fps,
            aperture_f=2.0, hfov_deg=62.2, focus_type="Fixed", has_ir_filter=True
        ),
        CameraInfo(
            name="Camera Module 2 NoIR", short_names=["IMX219 NoIR", "2N"],
            focal_length_px=calc_focal_length_px((3.04, 3.04), 1.12), pixel_size_um=1.12,
            resolutions=[], max_resolution=(3280, 2464), update_rate=_v1_v2_fps,
            aperture_f=2.0, hfov_deg=62.2, focus_type="Fixed", has_ir_filter=False
        ),
        CameraInfo(
            name="Camera Module 3 - Standard", short_names=["IMX708 Standard", "3"],
            focal_length_px=calc_focal_length_px((4.74, 4.74), 1.40), pixel_size_um=1.40,
            resolutions=[], max_resolution=(4608, 2592), update_rate=_v3_fps,
            aperture_f=1.8, hfov_deg=66.0, focus_type="Autofocus", has_ir_filter=True
        ),
        CameraInfo(
            name="Camera Module 3 - Standard NoIR", short_names=["IMX708 NoIR", "3N"],
            focal_length_px=calc_focal_length_px((4.74, 4.74), 1.40), pixel_size_um=1.40,
            resolutions=[], max_resolution=(4608, 2592), update_rate=_v3_fps,
            aperture_f=1.8, hfov_deg=66.0, focus_type="Autofocus", has_ir_filter=False
        ),
        CameraInfo(
            name="Camera Module 3 - Wide", short_names=["IMX708 Wide", "3W"],
            focal_length_px=calc_focal_length_px((2.75, 2.75), 1.40), pixel_size_um=1.40,
            resolutions=[], max_resolution=(4608, 2592), update_rate=_v3_fps,
            aperture_f=2.2, hfov_deg=102.0, focus_type="Autofocus", has_ir_filter=True
        ),
        CameraInfo(
            name="Camera Module 3 - Wide NoIR", short_names=["IMX708 Wide NoIR", "3WN"],
            focal_length_px=calc_focal_length_px((2.75, 2.75), 1.40), pixel_size_um=1.40,
            resolutions=[], max_resolution=(4608, 2592), update_rate=_v3_fps,
            aperture_f=2.2, hfov_deg=102.0, focus_type="Autofocus", has_ir_filter=False
        ),
        CameraInfo(
            name="High Quality Camera w/ 6mm Lens", short_names=["IMX477 6mm", "HQ6"],
            focal_length_px=calc_focal_length_px((6.00, 6.00), 1.55), pixel_size_um=1.55,
            resolutions=[], max_resolution=(4056, 3040), update_rate=_hq_fps,
            aperture_f=1.2, hfov_deg=55.0, focus_type="Manual", has_ir_filter=True
        ),
        CameraInfo(
            name="High Quality Camera w/ 16mm Lens", short_names=["IMX477 16mm", "HQ16"],
            focal_length_px=calc_focal_length_px((16.00, 16.00), 1.55), pixel_size_um=1.55,
            resolutions=[], max_resolution=(4056, 3040), update_rate=_hq_fps,
            aperture_f=1.4, hfov_deg=22.2, focus_type="Manual", has_ir_filter=True
        ),
        CameraInfo(
            name="High Quality Camera w/ 35mm Lens", short_names=["IMX477 35mm", "HQ35"],
            focal_length_px=calc_focal_length_px((35.00, 35.00), 1.55), pixel_size_um=1.55,
            resolutions=[], max_resolution=(4056, 3040), update_rate=_hq_fps,
            aperture_f=1.7, hfov_deg=10.1, focus_type="Manual", has_ir_filter=True
        ),
        CameraInfo(
            name="High Quality Camera w/ 8mm M12 Lens", short_names=["IMX477 M12-8mm", "HQ8"],
            focal_length_px=calc_focal_length_px((8.00, 8.00), 1.55), pixel_size_um=1.55,
            resolutions=[], max_resolution=(4056, 3040), update_rate=_hq_fps,
            aperture_f=1.8, hfov_deg=49.0, focus_type="Manual", has_ir_filter=True
        ),
        CameraInfo(
            name="High Quality Camera w/ 25mm M12 Lens", short_names=["IMX477 M12-25mm", "HQ25"],
            focal_length_px=calc_focal_length_px((25.00, 25.00), 1.55), pixel_size_um=1.55,
            resolutions=[], max_resolution=(4056, 3040), update_rate=_hq_fps,
            aperture_f=2.4, hfov_deg=14.4, focus_type="Manual", has_ir_filter=True
        ),
        CameraInfo(
            name="High Quality Camera w/ 2.7mm M12 Fisheye", short_names=["IMX477 M12-Fish", "HQ2.7"],
            focal_length_px=calc_focal_length_px((2.70, 2.70), 1.55), pixel_size_um=1.55,
            resolutions=[], max_resolution=(4056, 3040), update_rate=_hq_fps,
            aperture_f=2.5, hfov_deg=140.0, focus_type="Manual", has_ir_filter=True
        ),
        CameraInfo(
            name="Global Shutter Camera w/ 6mm Lens", short_names=["IMX296 6mm", "HQ6"],
            focal_length_px=calc_focal_length_px((6.00, 6.00), 3.45), pixel_size_um=3.45,
            resolutions=[], max_resolution=(1456, 1088), update_rate=_gs_fps,
            aperture_f=1.2, hfov_deg=45.0, focus_type="Manual", has_ir_filter=True
        ),
        CameraInfo(
            name="Global Shutter Camera w/ 16mm Lens", short_names=["IMX296 16mm", "HQ16"],
            focal_length_px=calc_focal_length_px((16.00, 16.00), 3.45), pixel_size_um=3.45,
            resolutions=[], max_resolution=(1456, 1088), update_rate=_gs_fps,
            aperture_f=1.4, hfov_deg=17.8, focus_type="Manual", has_ir_filter=True
        ),
        CameraInfo(
            name="Raspberry Pi AI Camera", short_names=["IMX500", "PiAI"],
            focal_length_px=calc_focal_length_px((4.74, 4.74), 1.55), pixel_size_um=1.55,
            resolutions=[], max_resolution=(4056, 3040), update_rate=_ai_fps,
            aperture_f=1.79, hfov_deg=66.3, focus_type="Manual", has_ir_filter=True
        )
    ]

    rpi_cameras = {
        key: cam_info
        for cam_info in rpi_camera_definitions
        for key in (cam_info.name, cam_info.short_name)
    }

    def __init__(self, info: "str | CameraInfo | BaseCamera", resolution: "tuple[int, int] | str" = "720p",
                 open=True):
        if isinstance(info, BaseCamera):
            info = info.info
        if not isinstance(info, CameraInfo):
            if info not in PiCamera.rpi_cameras:
                raise ValueError(f"Unsupported: {info}. Supported models: {', '.join(PiCamera.rpi_cameras.keys())}")
            if isinstance(resolution, str) and resolution not in resolutions and resolution not in resolutions.values():
                raise ValueError(
                    f"Unsupported resolution: {resolution}. Supported resolutions: {', '.join(str(r) for r in resolutions.values())}")
            info = PiCamera.rpi_cameras[info]
        if isinstance(resolution, str):
            resolution = resolutions[resolution]
        self.resolution = resolution
        super().__init__(open=open, info=info)

    def _open(self):
        try:
            from picamera2 import Picamera2
        except Exception as e:
            raise ImportError("PiCamera could not be initialized. Is picamera2 installed?") from e
        self.cam = Picamera2()
        self.cam.preview_configuration.main.format = "RGB888"
        self.cam.preview_configuration.main.size = self.resolution
        self.cam.configure("preview")
        self.cam.start()

    def _read(self):
        return self.cam.capture_array()

    def _release(self):
        self.cam.stop()
        self.cam.close()

    def _size(self):
        return self.resolution

    def _focal_length(self):
        if not self.info:
            raise ValueError("Camera info is not set, cannot determine focal length.")
        return self.info.focal_length(self.size)
