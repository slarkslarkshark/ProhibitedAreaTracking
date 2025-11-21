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

    def draw_frame(self, frame_data, boxes, intersection, prohib_areas=None):
        if prohib_areas is not None:
            self.prohib_areas = prohib_areas

        frame = frame_data.frame
        for box in boxes:
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(frame, (x1, y1), (x2, y2), self.color, self.thickness)

        if self.prohib_areas:
            for poly in self.prohib_areas:
                cv2.polylines(
                    frame,
                    [poly],
                    isClosed=True,
                    color=(0, 0, 255),
                    thickness=2,
                )

        if len(intersection) > 0:
            if not self.alarm_timer["status"]:
                self.prj_logger.warning("Someone entered prohibited zone!")
            self.alarm_timer["status"] = True
            self.alarm_timer["timestamp"] = frame_data.timestamp
        elif self.alarm_timer["status"]:
            now = frame_data.timestamp
            if (now - self.alarm_timer["timestamp"]).total_seconds() > self.alarm_dif:
                self.alarm_timer["status"] = False
                self.alarm_timer["timestamp"] = now

        if self.alarm_timer["status"]:
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
        return frame
