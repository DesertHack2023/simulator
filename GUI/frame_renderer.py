import logging
from dataclasses import dataclass, field
from math import sqrt

import dearpygui.dearpygui as dpg

logger = logging.getLogger("GUI.FrameRenderer")

COLOUR = (255, 255, 255, 255)
THICKNESS = 3
SNAP_DISTANCE = 25


def distance(p1: tuple[float, float], p2: tuple[float, float]):
    return sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


@dataclass
class Edge:
    p1: tuple[float, float]
    p2: tuple[float, float]
    edge_type: int = 0
    length: float = 0
    unit_vector: tuple[float, float] = field(init=False)

    def __post_init__(self):
        vector = [self.p2[0] - self.p1[0], self.p2[1] - self.p1[1]]
        magnitude = sqrt(vector[0] ** 2 + vector[1] ** 2)
        self.unit_vector = tuple(i / magnitude for i in vector)
        self.length = distance(self.p1, self.p2)

    def draw(self, parent):
        dpg.draw_line(
            self.p1, self.p2, color=COLOUR, thickness=THICKNESS, parent=parent
        )
        # logger.debug("Drew line")

    def foot_of_the_perpendicular(self, point: tuple[float, float]):
        dot = (point[0] - self.p1[0]) * self.unit_vector[0] + (
            point[1] - self.p1[1]
        ) * self.unit_vector[1]
        if dot >= 0 and dot < self.length:
            return (
                self.p1[0] + dot * self.unit_vector[0],
                self.p1[1] + dot * self.unit_vector[1],
            )


class Frame:
    """This is meant to draw the contents of a frame"""

    def __init__(self, parent, edges: list[Edge]):
        self.parent = parent
        self.edges = edges
        logger.debug(edges)
        self._render()
        logger.debug("rendered map")

    def _render(self):
        with dpg.drawlist(600, 450, parent=self.parent) as self.drawlist:
            for edge in self.edges:
                edge.draw(self.drawlist)
            with dpg.item_handler_registry() as registry:
                dpg.add_item_clicked_handler(
                    button=dpg.mvMouseButton_Left, callback=self._draw
                )
            dpg.bind_item_handler_registry(self.drawlist, registry)

    def _suggestion(self, point: tuple[float, float]):
        candidates = []
        for edge in self.edges:
            # logger.debug(f"Checking {edge}")
            foot = edge.foot_of_the_perpendicular(point)
            if not foot:
                continue
            d = distance(foot, point)
            # logger.debug(f"Perpendicular distance {d}")
            if d < SNAP_DISTANCE:
                # dpg.draw_circle(edge.p1, radius=2, color=(0, 0, 255, 255), parent=self.drawlist)
                candidates.append((foot, d))
        if candidates:
            return min(candidates, key=lambda x: x[1])[0]

    def _draw(self, _):
        x, y = dpg.get_mouse_pos()
        suggestion = self._suggestion((x, y))
        if suggestion:
            x, y = suggestion
        new_x, new_y = 0, 0  #  prevents new_? from being unbound
        line = None
        while dpg.is_mouse_button_down(button=dpg.mvMouseButton_Left):
            new_x, new_y = dpg.get_mouse_pos()
            suggestion = self._suggestion((new_x, new_y))
            if suggestion:
                new_x, new_y = suggestion
                # logger.debug(f"Suggested Point {(new_x, new_y)}")
                # dpg.draw_circle((new_x, new_y), radius=2, color=(255, 0, 0, 255), parent=self.drawlist)
            if line:
                dpg.configure_item(line, p2=(new_x, new_y))
            else:
                line = dpg.draw_line(
                    (x, y),
                    (new_x, new_y),
                    parent=self.drawlist,
                    color=COLOUR,
                    thickness=THICKNESS,
                )
        if new_x != x or new_y != y:
            edge = Edge((x, y), (new_x, new_y))
            self.edges.append(edge)
        # logger.debug(self.edges)
