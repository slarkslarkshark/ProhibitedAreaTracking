import cv2
import numpy as np


class PolygonAnnotator:
    def __init__(self, image, window_name="Video"):
        self.image = image.copy()
        self.working_image = image.copy()
        self.polygons = []
        self.current_polygon = []
        self.drawing = False
        self.window_name = window_name

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if not self.drawing:
                self.drawing = True
                self.current_polygon = [(x, y)]
            else:
                first_point = self.current_polygon[0]
                distance = np.sqrt(
                    (x - first_point[0]) ** 2 + (y - first_point[1]) ** 2
                )
                if distance < 10:
                    if len(self.current_polygon) >= 3:
                        self.polygons.append(
                            np.array(self.current_polygon, dtype=np.int32)
                        )
                        self.drawing = False
                        self.current_polygon = []
                else:
                    self.current_polygon.append((x, y))

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing and self.current_polygon:
                temp_image = self.image.copy()
                for poly in self.polygons:
                    cv2.polylines(
                        temp_image,
                        [poly],
                        isClosed=True,
                        color=(0, 255, 0),
                        thickness=2,
                    )

                if len(self.current_polygon) > 1:
                    cv2.polylines(
                        temp_image,
                        [np.array(self.current_polygon, dtype=np.int32)],
                        isClosed=False,
                        color=(255, 0, 0),
                        thickness=2,
                    )
                cv2.line(temp_image, self.current_polygon[-1], (x, y), (255, 0, 0), 1)

                for point in self.current_polygon:
                    cv2.circle(temp_image, point, 3, (255, 0, 0), -1)

                self.working_image = temp_image
            else:
                temp_image = self.image.copy()
                for poly in self.polygons:
                    cv2.polylines(
                        temp_image,
                        [poly],
                        isClosed=True,
                        color=(0, 255, 0),
                        thickness=2,
                    )
                self.working_image = temp_image

        elif event == cv2.EVENT_LBUTTONUP:
            pass

    def run(self, close_window=True):
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)

        print("Click to draw polygons")
        print(
            "Press 'Enter' to finish polygon, 'c' to clear last polygon, 'q' to quit."
        )

        while True:
            cv2.imshow(self.window_name, self.working_image)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break
            elif key == ord("c"):  # Clear last polygon
                if self.polygons:
                    self.polygons.pop()
                    # Redraw the image without last polygon
                    temp_image = self.image.copy()
                    for poly in self.polygons:
                        cv2.polylines(
                            temp_image,
                            [poly],
                            isClosed=True,
                            color=(0, 255, 0),
                            thickness=2,
                        )
                    self.working_image = temp_image
            # Processing Enter to complete the polygon if not completed by clicking on the first point
            elif key == 13:  # 13 - ASCII=Enter
                if self.drawing and len(self.current_polygon) >= 3:
                    self.polygons.append(np.array(self.current_polygon, dtype=np.int32))
                    self.drawing = False
                    temp_image = self.image.copy()
                    for poly in self.polygons:
                        cv2.polylines(
                            temp_image,
                            [poly],
                            isClosed=True,
                            color=(0, 255, 0),
                            thickness=2,
                        )
                    self.working_image = temp_image
        if close_window:
            cv2.destroyAllWindows()

        return self.polygons
