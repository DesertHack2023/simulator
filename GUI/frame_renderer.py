import logging

import dearpygui.dearpygui as dpg

from .boidsimulator import Agent, Edge, Simulation, distance

logger = logging.getLogger("GUI.FrameRenderer")

COLOUR = (255, 255, 255, 255)
THICKNESS = 3
SNAP_DISTANCE = 25


class Canvas:
    """This is meant to draw the contents of a frame"""

    def __init__(self, parent, edges: list[Edge]):
        self.parent = parent
        self.edges = edges
        boids = list(Agent([100, 100], [1, 2]) for _ in range(25))
        self.sim = Simulation(boids)
        logger.debug(edges)
        self._render()
        logger.debug("rendered map")

    @staticmethod
    def draw(edge: Edge, parent):
        dpg.draw_line(
            edge.p1, edge.p2, color=COLOUR, thickness=THICKNESS, parent=parent
        )
        # logger.debug("Drew line")

    def _render(self):
        dpg.add_button(
            label="Boid Sim", parent=self.parent, callback=self.run_simulation
        )
        with dpg.drawlist(600, 450, parent=self.parent) as self.drawlist:
            for edge in self.edges:
                self.draw(edge, self.drawlist)
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

    def run_simulation(self):
        boid_ids = []
        for boid in self.sim.boids:
            i = dpg.draw_circle(
                boid.position, radius=5, color=(255, 0, 0, 25), parent=self.drawlist
            )
            boid_ids.append(i)
        for frame in self.sim.run():
            for x, boid in enumerate(frame):
                dpg.configure_item(boid_ids[x], center=boid.position)
