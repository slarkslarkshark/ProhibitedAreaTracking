from reader import VideoReader
from tracking import Tracker
import queue
from pathlib import Path
from help_tools.logger_worker import LoggerWorker
from help_tools.data_containers import FrameData
import yaml
import time
import cv2
from ast import literal_eval


def _draw_boxes(frame, boxes, cfg):
    color = literal_eval(cfg["BOXES_COLOR"])
    thickness = cfg["BOXES_THICKNESS"]
    for box in boxes:
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

    return frame


def main():
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    video_source = Path(cfg["video_source"])
    prj_logger = LoggerWorker(cfg).logger
    frames_queue = queue.Queue(maxsize=cfg["QUEUE_MAX_SIZE"])
    camera = VideoReader(frames_queue=frames_queue, prj_logger=prj_logger)
    tracker = Tracker(prj_logger, cfg)

    camera.start_capture(video_source)
    while True:
        try:
            frame_data: FrameData = frames_queue.get(timeout=0.1)
            boxes = tracker.detect(frame_data.frame)
            drawed_frame = _draw_boxes(frame_data.frame, boxes, cfg)
            cv2.imshow("Video", drawed_frame)
        except queue.Empty:
            time.sleep(0.01)

        if cv2.waitKey(25) & 0xFF == ord("q"):
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
