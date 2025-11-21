from datetime import datetime
import queue
from threading import Thread
from typing import Union
import cv2
from pathlib import Path
from help_tools.data_containers import FrameData
from frames_processing.polygon_annotator import PolygonAnnotator
import time


class VideoReader:
    """Class for taking frames from Video or RTSP."""

    def __init__(self, frames_queue, prj_logger) -> None:

        self.prj_logger = prj_logger
        self.capture: Union[cv2.VideoCapture, None] = None
        self.frames_queue: queue.Queue = frames_queue
        self.rtsp_mode = False
        self.stopped = True

    def _get_one_frame(self, frame_source: Union[int, str, Path]):
        capture = cv2.VideoCapture(frame_source)
        self.prj_logger.info(f"Connected to source {frame_source}.")
        captured, frame = capture.read()
        capture.release()
        self.prj_logger.info(f"Released source {frame_source}.")

        frame_data = FrameData(
            source=frame_source,
            frame_exist=captured,
            frame=frame,
            timestamp=datetime.now(),
        )
        return frame_data

    def get_prohib_areas(self, video_source, cfg):
        prohib_areas = []

        frame_data: FrameData = self._get_one_frame(video_source)
        if frame_data.frame_exist:
            annotator = PolygonAnnotator(frame_data.frame, cfg["WINDOW_NAME"])
            prohib_areas = annotator.run(close_window=False)
        return prohib_areas

    def start_capture(self, frames_source: Union[int, str, Path]) -> None:
        self.capture = cv2.VideoCapture(frames_source)
        self.rtsp_mode = "rtsp://" in str(frames_source)
        if not self.capture.isOpened():
            self.prj_logger.error(f"Can't connect to {frames_source}.")
            raise ValueError("Can't start frame capture.")

        self.stopped = False
        start_thread = Thread(
            target=self._capture_frames, args=(frames_source,), daemon=True
        )
        start_thread.start()
        self.prj_logger.info(f"Connected to source {frames_source}.")

    def stop_capture(self, frames_source) -> bool:
        self.stopped = True
        time.sleep(0.05)
        if self.capture:
            self.capture.release()
            self.prj_logger.info(f"Released source {frames_source}.")
        return self.stopped

    def _capture_frames(self, frames_source):
        frames_missed = 0
        total_frames = 0
        block_stream = not self.rtsp_mode
        while not self.stopped:
            try:
                frame = None
                captured = False

                captured, frame = self.capture.read()

                if captured and frame is not None:
                    total_frames += 1

                    frame_data = FrameData(
                        source=frames_source,
                        frame_exist=True,
                        frame=frame,
                        timestamp=datetime.now(),
                    )
                    while True:
                        try:
                            self.frames_queue.put(
                                frame_data, block=block_stream, timeout=1
                            )
                            break
                        except queue.Full:
                            # skip frame if it is rtsp
                            if self.rtsp_mode:
                                frames_missed += 1
                                break
                            else:
                                # keep all frames if it is video
                                time.sleep(0.01)

                elif self.rtsp_mode:
                    frames_missed += 1
                else:
                    self.stop_capture(frames_source)

            except Exception as error:
                self.prj_logger.error(str(error))
        self.prj_logger.info(
            f"Reading frames is finished. Total frames {total_frames}. Frames missed {frames_missed}"
        )
