from ultralytics import YOLO
import yaml
import numpy as np
from boxmot import BoostTrack
from pathlib import Path


class Tracker:

    def __init__(self, prj_logger, cfg):
        self.prj_logger = prj_logger
        try:
            with open(cfg["DETECTOR_CFG_PATH"], "r", encoding="utf-8") as f:
                self.det_cfg = yaml.safe_load(f)
        except FileNotFoundError:
            self.prj_logger.error("Wrong detector cfg path!")
            raise FileNotFoundError

        self.detector = YOLO(model=self.det_cfg["model"], task=self.det_cfg["task"])
        self.prj_logger.info("Detector has been loaded")

        try:
            with open(cfg["TRACKER_CFG_PATH"], "r", encoding="utf-8") as f:
                self.track_cfg = yaml.safe_load(f)
                self._reid_weights = Path(self.track_cfg["reid_weights"])
                del self.track_cfg["reid_weights"]
        except FileNotFoundError:
            self.prj_logger.error("Wrong detector cfg path!")
            raise FileNotFoundError

        self.detector = YOLO(model=self.det_cfg["model"], task=self.det_cfg["task"])
        self.prj_logger.info("Detector has been loaded")

        self.tracker = BoostTrack(reid_weights=self._reid_weights, **self.track_cfg)
        self.prj_logger.info("Tracker has been loaded")

    def track(self, frame):
        boxes, metadata = None, None
        results = self.detector(source=frame, **self.det_cfg)[0]
        if results.boxes is None or len(results.boxes) == 0:
            self.tracker.update(np.empty((0, 6)), frame)
            return boxes, metadata
        xyxy = results.boxes.xyxy.cpu().numpy()
        conf = results.boxes.conf.cpu().numpy()
        cls = results.boxes.cls.cpu().numpy()
        dets = np.concatenate([xyxy, conf[:, None], cls[:, None]], axis=1)

        tracks = self.tracker.update(dets, frame)

        if tracks.shape[0] > 0:
            boxes = tracks[:, :4].astype(np.float32)
            metadata = {
                "track_id": tracks[:, 4].astype(np.int32),
                "conf": tracks[:, 5].astype(np.float32),
                "cls": tracks[:, 6].astype(np.int32),
                "ind": tracks[:, 7].astype(np.int32),
            }

        return boxes, metadata
