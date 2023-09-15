import logging
import time

import dearpygui.dearpygui as dpg

from .boidsimulator import Edge, Simulation, distance, iter_agents, test_boids

logger = logging.getLogger("GUI.FrameRenderer")

COLOUR = (255, 255, 255, 255)
THICKNESS = 3
SNAP_DISTANCE = 25


class Canvas:
    """This is meant to draw the contents of a frame"""

    def __init__(self, parent, edges: list[Edge]):
        self.parent = parent
        self.edges = edges

        boids = test_boids()
        self.sim = Simulation(boids)

        logger.debug(edges)
        self._render()
        logger.debug("rendered map")

    def _render(self):
        dpg.add_button(
            label="Boid Sim", parent=self.parent, callback=self.run_simulation
        )
        with dpg.child_window(
            autosize_x=True, autosize_y=True, parent=self.parent
        ) as window:
            self.plot = dpg.add_plot(width=-1, height=-1, parent=window)
            with dpg.item_handler_registry() as registry:
                dpg.add_item_clicked_handler(
                    button=dpg.mvMouseButton_Middle, callback=self._draw
                )
            dpg.bind_item_handler_registry(self.plot, registry)

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
        x, y = dpg.get_plot_mouse_pos()
        suggestion = self._suggestion((x, y))
        if suggestion:
            x, y = suggestion
        new_x, new_y = 0, 0  #  prevents new_? from being unbound
        line = None
        while dpg.is_mouse_button_down(button=dpg.mvMouseButton_Middle):
            new_x, new_y = dpg.get_plot_mouse_pos()
            logger.debug([x, y, new_x, new_y])
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
                    parent=self.plot,
                    color=COLOUR,
                    thickness=THICKNESS,
                )
        if new_x != x or new_y != y:
            edge = Edge((x, y), (new_x, new_y))
            self.edges.append(edge)
        # logger.debug(self.edges)

    def run_simulation(self):
        boid_ids = []
        for boid in iter_agents(self.sim.boids):
            position, arrow_head = boid
            i = dpg.draw_arrow(
                p2=position,
                p1=arrow_head,
                color=(255, 0, 0, 255),
                parent=self.plot,
                thickness=THICKNESS,
            )
            boid_ids.append(i)
        for state in self.sim.run():
            # time.sleep(0.125)
            boids = state["boids"]
            c = 0
            for boid in iter_agents(boids):
                position, arrow_head = boid
                dpg.configure_item(boid_ids[c], p2=position, p1=arrow_head)
                c += 1
