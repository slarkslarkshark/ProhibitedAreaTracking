from reader import VideoReader
import queue
from pathlib import Path
from help_tools.logger_worker import LoggerWorker
from help_tools.data_containers import FrameData
import yaml
import time


def main():
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    video_source = Path(cfg["video_source"])
    prj_logger = LoggerWorker(cfg).logger
    frames_queue = queue.Queue()
    camera = VideoReader(frames_queue=frames_queue, prj_logger=prj_logger)

    camera.start_capture(video_source)
    while True:
        try:
            frame: FrameData = frames_queue.get(timeout=0.1)
            print(frame.timestamp)
        except queue.Empty:
            time.sleep(0.1)


if __name__ == "__main__":
    main()
