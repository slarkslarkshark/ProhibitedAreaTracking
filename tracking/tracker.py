from ultralytics import YOLO
import yaml


class Tracker:

    def __init__(self, prj_logger, cfg):
        self.prj_logger = prj_logger

        try:
            with open(cfg["DETECTOR_CFG_PATH"], "r", encoding="utf-8") as f:
                self.det_cfg = yaml.safe_load(f)
        except FileNotFoundError:
            self.prj_logger.error("Wrong detector cfg path!")

        self.detector = YOLO(model=self.det_cfg["model"], task=self.det_cfg["task"])
        self.prj_logger.info("Detector has been loaded")

    def detect(self, frame):
        boxes = self.detector(source=frame, **self.det_cfg)[0].boxes
        return boxes.xyxy
            