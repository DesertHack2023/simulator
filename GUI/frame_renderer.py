import itertools
import logging
import threading
import time
from dataclasses import dataclass, field
from functools import partial
from math import sqrt

import dearpygui.dearpygui as dpg

import Simulation

from .params import ParameterSelector

logger = logging.getLogger("GUI.FrameRenderer")

COLOUR = (255, 255, 255, 255)
THICKNESS = 3
SNAP_DISTANCE = 25


def distance(
    p1: tuple[float, float] | list[float], p2: tuple[float, float] | list[float]
):
    return sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def iter_agents(frame: list[list[Simulation.Agent]]):
    # for cell in frame:
    #     for agent in cell:
    #         yield (agent.x, agent.y), (agent.vx, agent.vy)
    #
    for agent in itertools.chain.from_iterable(frame):
        # logger.debug(agent)
        position = (agent.x, agent.y)
        velocity = (agent.vx, agent.vy)
        yield position, agent.age


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

    def foot_of_the_perpendicular(self, point: tuple[float, float]):
        dot = (point[0] - self.p1[0]) * self.unit_vector[0] + (
            point[1] - self.p1[1]
        ) * self.unit_vector[1]
        if dot >= 0 and dot < self.length:
            return (
                self.p1[0] + dot * self.unit_vector[0],
                self.p1[1] + dot * self.unit_vector[1],
            )

    @classmethod
    def from_wall(cls, wall: Simulation.Wall):
        p1, p2 = wall.endpoints
        edge_type = wall.state
        return cls(p1, p2, edge_type)


class Canvas:
    """This is meant to draw the contents of a frame"""

    def __init__(
        self, parent, edges: list[Edge], parameter_selector: ParameterSelector
    ):
        self.parent = parent
        self.edges = edges
        self.parameter_selector = parameter_selector
        self.agent_ids = dict()

        logger.debug(edges)
        self._render()
        logger.debug("rendered map")

    def _render(self):
        dpg.add_button(
            label="Boid Sim", parent=self.parent, callback=self.start_simulation
        )
        with dpg.child_window(
            autosize_x=True, autosize_y=True, parent=self.parent
        ) as window:
            with dpg.plot(
                width=-1, height=-1, parent=window, equal_aspects=True
            ) as self.plot:
                axis = dpg.add_plot_axis(dpg.mvYAxis)
                dpg.add_bar_series([0, 100, 200], [0, 0, 0], weight=1, parent=axis)
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
            # logger.debug([x, y, new_x, new_y])
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

    def _draw_edge(self, edge: Edge):
        if edge.edge_type == 1:
            dpg.draw_line(
                edge.p1, edge.p2, parent=self.plot, color=COLOUR, thickness=THICKNESS
            )
        self.edges.append(edge)

    def start_simulation(self):
        # TODO: This function should create a parameter selector prompt

        params = self.parameter_selector.get_params()
        floorplan = Simulation.Floorplan.make_default_layout()

        # draws the walls
        for wall in itertools.chain.from_iterable(floorplan.cells):
            edge = Edge.from_wall(wall)
            self._draw_edge(edge)

        sim = Simulation.Simulation(params, floorplan)
        task = partial(self.run_simulation, sim)
        thread = threading.Thread(target=task, args=(), daemon=True)

        thread.start()

    def run_simulation(self, sim):
        for agent in self.agent_ids.values():
            dpg.delete_item(agent)
        self.agent_ids.clear()
        for agent in iter_agents(sim.frame):
            position, age = agent
            # arrow_head = position + velocity
            i = dpg.draw_circle(
                center=position,
                radius=3,
                color=(255, 0, 0, 255),
                parent=self.plot,
                thickness=THICKNESS,
            )
            self.agent_ids[age] = i

        logger.debug(len(self.agent_ids))

        for i, frame in enumerate(sim.run()):
            # time.sleep(0.06)
            c = 0
            for agent in iter_agents(frame):
                position, age = agent
                # logger.debug(f"fame count: {i} position: {position}, velocity: {age}")
                dpg.configure_item(self.agent_ids[age], center=position)
            c += 1
