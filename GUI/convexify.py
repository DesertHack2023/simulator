import logging
from dataclasses import dataclass, field
from itertools import chain
from math import sqrt

import Simulation

logger = logging.getLogger("GUI.Convexifier")


def distance(
    p1: tuple[float, float] | list[float], p2: tuple[float, float] | list[float]
):
    return sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


@dataclass
class Edge:
    p1: tuple[float, float]
    p2: tuple[float, float]
    edge_type: int = 1
    length: float = 0
    unit_vector: tuple[float, float] = field(init=False)

    def __post_init__(self):
        vector = [self.p2[0] - self.p1[0], self.p2[1] - self.p1[1]]
        magnitude = sqrt(vector[0] ** 2 + vector[1] ** 2)
        self.unit_vector = tuple(i / magnitude for i in vector)
        self.length = distance(self.p1, self.p2)
        x1, y1 = self.p1
        x2, y2 = self.p2
        self.a = y2 - y1
        self.b = x1 - x2
        self.c = x2 * y1 - x1 * y2

    def foot_of_the_perpendicular(self, point: tuple[float, float]):
        dot = (point[0] - self.p1[0]) * self.unit_vector[0] + (
            point[1] - self.p1[1]
        ) * self.unit_vector[1]
        if dot >= 0 and dot < self.length:
            return (
                self.p1[0] + dot * self.unit_vector[0],
                self.p1[1] + dot * self.unit_vector[1],
            )

    def which_side(self, coordinate: list[float] | tuple[float, float]):
        x, y = coordinate
        f = self.a * x + self.b * y + self.c
        if f < 0:
            return "right"
        elif f > 0:
            return "left"
        else:
            return "on-the-line"

    def orthogonal_distance(self, point: list[float] | tuple[float, float]):
        x, y = point
        return abs(self.a * x + self.b * y + self.c)

    @classmethod
    def from_wall(cls, wall: Simulation.Wall):
        p1, p2 = wall.endpoints
        edge_type = wall.state
        return cls(p1, p2, edge_type)


class ConvexDivider:
    def __init__(self, edges: list[Edge]):
        self.edges = edges
        self.convex_hull = []
        self.find_convex_hull()

    def find_convex_hull(self):
        # uses Divide and Conquer

        points = list(chain.from_iterable((edge.p1, edge.p2) for edge in self.edges))
        sorted_coordinates = sorted(points)

        A = sorted_coordinates[0]
        B = sorted_coordinates[-1]

        AB = Edge(A, B)
        BA = Edge(B, A)

        ABright = []
        BAright = []

        for coordinate in sorted_coordinates:
            coordinate_side = AB.which_side(coordinate)
            if coordinate_side == "right":
                ABright.append(coordinate)
            if coordinate_side == "left":
                BAright.append(coordinate)
            else:
                pass

        self.convex_hull.append(AB)
        self.convex_hull.append(BA)

        self.find_hull(ABright, AB)
        self.find_hull(BAright, BA)

    def find_hull(self, partition, edge: Edge):
        if len(partition) == 0:
            return
        else:
            C = (0, 0)
            farthest_distance = -1
            for coordinate in partition:
                orthogonal_distance = edge.orthogonal_distance(coordinate)
                if orthogonal_distance > farthest_distance:
                    farthest_distance = orthogonal_distance
                    C = coordinate

            AC = Edge(edge.p1, C)
            CB = Edge(C, edge.p2)

            self.convex_hull.remove(edge)
            self.convex_hull.append(AC)
            self.convex_hull.append(CB)

            partition.remove(C)

            ACright = [c for c in partition if AC.which_side(c) == "right"]
            CBright = [c for c in partition if CB.which_side(c) == "right"]

            self.find_hull(ACright, AC)
            self.find_hull(CBright, CB)
