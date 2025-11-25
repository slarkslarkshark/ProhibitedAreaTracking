from frames_processing import VideoReader, WindowDrawer
from tracking import Tracker, Intersector
import queue
from pathlib import Path
from help_tools.logger_worker import LoggerWorker
from help_tools.data_containers import FrameData
import yaml
import time
import cv2


def main():
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    video_source = Path(cfg["video_source"])
    prj_logger = LoggerWorker(cfg).logger
    frames_queue = queue.Queue(maxsize=cfg["QUEUE_MAX_SIZE"])
    camera = VideoReader(frames_queue=frames_queue, prj_logger=prj_logger)
    tracker = Tracker(prj_logger, cfg)

    prohib_areas = camera.get_prohib_areas(video_source, cfg)
    intersector = Intersector(prohib_areas)
    drawer = WindowDrawer(prj_logger, cfg, prohib_areas)

    camera.start_capture(video_source)
    while True:
        try:
            frame_data: FrameData = frames_queue.get(timeout=0.1)
            boxes, metadata = tracker.track(frame_data.frame)
            if boxes is None:
                boxes = []
            intersection = intersector.check_intersection(boxes)
            drawn_frame = drawer.draw_frame(
                frame_data, boxes, intersection, metadata=metadata
            )
            cv2.imshow("Video", drawn_frame)
        except queue.Empty:
            time.sleep(0.01)

        if cv2.waitKey(25) & 0xFF == ord("q"):
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
