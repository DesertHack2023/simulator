import itertools
import logging
import threading

# import time
from functools import partial

import dearpygui.dearpygui as dpg

import Simulation

from .convexify import ConvexDivider, Edge, distance
from .params import ParameterSelector

logger = logging.getLogger("GUI.FrameRenderer")

COLOUR = (255, 255, 255, 255)
THICKNESS = 3
SNAP_DISTANCE = 25

DEBUG_COLOUR = (0, 0, 255, 255)
DEBUG_THICKNESS = 1
DEBUGING = True


def iter_agents(frame: list[list[Simulation.Agent]]):
    # for cell in frame:
    #     for agent in cell:
    #         yield (agent.x, agent.y), (agent.vx, agent.vy)
    #
    for agent in itertools.chain.from_iterable(frame):
        # logger.debug(agent)
        position = (agent.x, agent.y)
        # velocity = (agent.vx, agent.vy)
        yield position, agent.age


class Canvas:
    """This is meant to draw the contents of a frame"""

    def __init__(
        self, parent, edges: list[Edge], parameter_selector: ParameterSelector
    ):
        self.parent = parent
        self.edges = edges
        self.parameter_selector = parameter_selector
        self.agent_ids = dict()

        self.debug_edges = []

        logger.debug(edges)
        self.setup()
        logger.debug("rendered map")

    def setup(self):
        self.run_button = dpg.add_button(
            label="Run Sim", parent=self.parent, callback=self.start_simulation
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
                    button=dpg.mvMouseButton_Middle, callback=self.draw
                )
            dpg.bind_item_handler_registry(self.plot, registry)

    def snap_suggestion(self, point: tuple[float, float]):
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

    def draw(self, _):
        x, y = dpg.get_plot_mouse_pos()
        suggestion = self.snap_suggestion((x, y))
        if suggestion:
            x, y = suggestion
        new_x, new_y = 0, 0  #  prevents new_? from being unbound
        line = None
        while dpg.is_mouse_button_down(button=dpg.mvMouseButton_Middle):
            new_x, new_y = dpg.get_plot_mouse_pos()
            # logger.debug([x, y, new_x, new_y])
            suggestion = self.snap_suggestion((new_x, new_y))
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

        divider = ConvexDivider(self.edges)

        if DEBUGING:
            for edge in self.debug_edges:
                dpg.delete_item(edge)

            self.debug_edges.clear()

            for edge in divider.convex_hull:
                line = self.draw_edge(
                    edge, color=DEBUG_COLOUR, thickness=DEBUG_THICKNESS
                )
                self.debug_edges.append(line)
                logger.debug(edge)

        # logger.debug(self.edges)

    def draw_edge(self, edge: Edge, color=COLOUR, thickness=THICKNESS):
        line = dpg.draw_line(
            edge.p1, edge.p2, parent=self.plot, color=color, thickness=thickness
        )
        return line

    def start_simulation(self):
        params = self.parameter_selector.get_params()
        floorplan = Simulation.Floorplan.make_default_layout()

        # draws the walls
        for wall in itertools.chain.from_iterable(floorplan.cells):
            edge = Edge.from_wall(wall)
            if edge.edge_type == 1:
                self.draw_edge(edge)

        sim = Simulation.Simulation(params, floorplan)
        task = partial(self.run_simulation, sim)
        thread = threading.Thread(target=task, args=(), daemon=True)

        thread.start()

    def run_simulation(self, sim):
        dpg.hide_item(self.run_button)
        for agent in self.agent_ids.values():
            dpg.delete_item(agent)
        self.agent_ids.clear()
        for agent in iter_agents(sim.frame):
            position, age = agent
            # arrow_head = position + velocity
            i = dpg.draw_circle(
                center=position,
                radius=1.5,
                color=(255, 0, 0, 255),
                fill=(255, 0, 0, 255),
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
        dpg.show_item(self.run_button)
