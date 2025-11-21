from shapely import Polygon, box


class Intersector:
    def __init__(self, prohib_areas):
        self.prohib_pols = [Polygon(np_pol) for np_pol in prohib_areas]

    def check_intersection(self, boxes):
        boxes_pols = [box(*np_pol) for np_pol in boxes]
        intersections = {}

        for i, box_pol in enumerate(boxes_pols):
            for j, prohib_pol in enumerate(self.prohib_pols):
                if box_pol.intersects(prohib_pol):
                    if i in intersections:
                        intersections[i].append(j)
                    else:
                        intersections[i] = [j]

        return intersections
