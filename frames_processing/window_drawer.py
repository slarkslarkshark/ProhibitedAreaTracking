from ast import literal_eval
import cv2
from datetime import datetime


class WindowDrawer:
    def __init__(self, prj_logger, cfg, prohib_areas=None):
        self.prj_logger = prj_logger
        self.color = literal_eval(cfg["BOXES_COLOR"])
        self.thickness = cfg["BOXES_THICKNESS"]
        self.alarm_dif = cfg["ALARM_TIME"]
        self.alarm_timer = {"status": False, "timestamp": datetime.now()}
        self.prohib_areas = prohib_areas

    def draw_frame(
        self, frame_data, boxes, intersection, metadata=None, prohib_areas=None
    ):
        if prohib_areas is not None:
            self.prohib_areas = prohib_areas

        self._update_alarm_state(frame_data.timestamp, intersection)
        frame = frame_data.frame.copy()

        self._draw_boxes(frame, boxes)
        self._draw_track_ids(frame, boxes, metadata)
        self._draw_prohibited_areas(frame)
        self._draw_alarm_overlay(frame)

        return frame

    def _draw_boxes(self, frame, boxes):
        for box in boxes:
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(frame, (x1, y1), (x2, y2), self.color, self.thickness)

    def _draw_track_ids(self, frame, boxes, metadata):
        if metadata is None or "track_id" not in metadata:
            return

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2

        for i, box in enumerate(boxes):
            track_id = int(metadata["track_id"][i])
            label = f"ID:{track_id}"

            x1, y1, x2, y2 = map(int, box)
            (text_w, text_h), baseline = cv2.getTextSize(
                label, font, font_scale, thickness
            )

            text_x = x1
            text_y = y1 - 10 if y1 - 10 > 10 else y1 + text_h + 10
            cv2.putText(
                frame,
                label,
                (text_x, text_y - baseline),
                font,
                font_scale,
                (255, 255, 255),
                thickness,
            )

    def _draw_prohibited_areas(self, frame):
        if not self.prohib_areas:
            return
        for poly in self.prohib_areas:
            cv2.polylines(
                frame,
                [poly],
                isClosed=True,
                color=(0, 0, 255),
                thickness=2,
            )

    def _update_alarm_state(self, timestamp, intersection):
        if len(intersection) > 0:
            if not self.alarm_timer["status"]:
                self.prj_logger.warning("Someone entered prohibited zone!")
            self.alarm_timer["status"] = True
            self.alarm_timer["timestamp"] = timestamp
        elif self.alarm_timer["status"]:
            now = timestamp
            if (now - self.alarm_timer["timestamp"]).total_seconds() > self.alarm_dif:
                self.alarm_timer["status"] = False
                self.alarm_timer["timestamp"] = now

    def _draw_alarm_overlay(self, frame):
        if not self.alarm_timer["status"]:
            return

        height, width = frame.shape[:2]
        font_scale = min(width, height) / 512
        thickness = max(2, int(font_scale * 3))
        text = "ALARM!"
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = (width - text_size[0]) // 2
        text_y = (height + text_size[1]) // 2
        padding = 20

        cv2.rectangle(
            frame,
            (text_x - padding, text_y - text_size[1] - padding),
            (text_x + text_size[0] + padding, text_y + padding),
            (0, 0, 0),
            -1,
        )
        cv2.putText(
            frame, text, (text_x, text_y), font, font_scale, (0, 0, 255), thickness
        )
