import logging
from bisect import bisect_left
from datetime import datetime
from math import inf, sqrt
from random import random, seed, uniform

logger = logging.getLogger("Simulation.Core")

from .agent import Agent


class Simulation:
    """Controls the flow of the simulation.

    The simulation is an agent based simulation where the 'people' (represented by agents) are free to move within a virtual 2D floorplan. The movement of the agents are controlled by some forces (attractive or repulsive) as well as some random element of free will for each agent. Further more

    Attributes
    ----------
    params: Params
                    Starting simulation parameters
    floorplan: Floorplan
                    The floorplan of the simulation space
    frame: List[List[agents]]
                    The current frame of the simulation

    Methods
    -------
    __init__(self: Simulation, params: Params)
                    Initializes the simulation
    initializeFrame(self: Simulation)
                    Initializes the first frame
    runSimulation(self: Simulation)
                    Runs the simulation
    nextFrame(self: Simulation)
                    Calculates the next frame of the simulation
    """

    def __init__(self, params, floorplan):
        """Initialized the simulation

        Intializes the simulation with some basic properties

        Parameters
        ----------
        params: Params
                        The parameters of the simulation
        floorplan: Floorplan
                        The floorplan of the simulation

        Returns
        -------
        None
        """

        self.params = params
        self.floorplan = floorplan
        self.initializeFrame()

    def initializeFrame(self):
        """Creates the first frame of the simulation

        Parameters
        ----------

        Returns
        -------
        None
        """
        id = 0
        agents = [[] for _ in range(self.floorplan.num_cells)]
        for dest, num_agents in enumerate(self.floorplan.distribution):
            for _ in range(num_agents):
                x = uniform(0, self.params.basic_parameters.WIDTH)
                y = uniform(0, self.params.basic_parameters.HEIGHT)
                cell = self.floorplan.find_cell(x, y)
                # print(x, y, cell, dest)
                # Create agent
                agents[cell].append(Agent(cell, x, y, id, dest))
                id += 1

        # Create frame
        self.frame = agents
        # exit()

    def run(self):
        """Run the simulation.

        Run an agent based simulation based on the
        configuration of the current simulation.

        Parameters
        ----------

        Yields
        ------
        List[List[Agent]]
                Constantly yields frames of simulation as they are calculated

        Returns
        -------
        None
        """

        # Reset random seed to current system time
        # Initalize and save seed
        startTime = datetime.now()
        self.params.basic_parameters.RANDOM_SEED = (
            startTime.hour * 10000 + startTime.minute * 100 + startTime.second
        )
        seed(self.params.basic_parameters.RANDOM_SEED)

        # Yield the first frame
        yield self.frame

        for _ in range(self.params.basic_parameters.SIMULATION_LENGTH):
            # Calculate the next frame and then yield it
            self.nextFrame()
            yield self.frame

    def nextFrame(self):
        """Calculates the next frame of the simulation

        Parameters
        ----------

        Returns
        -------
        None
        """

        self.moveAgents()

    def moveAgents(self):
        """Implements movement of the agents each frame

        Parameters
        ----------

        Returns
        -------
        """

        # Calculate force on each agent
        for cell_no, agents in enumerate(self.frame):
            for agent in agents:
                fx, fy = self.calculateForce(agent)

                # Update velocity
                logger.debug(
                    f"Initial Position: {agent.x, agent.y}, Velocity: {agent.vx, agent.vy}"
                )
                agent.vx += fx
                agent.vy += fy
                v = sqrt(agent.vx**2 + agent.vy**2)
                logger.debug(
                    f"Max Velocity: {self.params.basic_parameters.MAX_VELOCITY}"
                )
                if v > self.params.basic_parameters.MAX_VELOCITY:
                    agent.vx *= self.params.basic_parameters.MAX_VELOCITY / v
                    agent.vy *= self.params.basic_parameters.MAX_VELOCITY / v

                # Update position
                # old_pos = (agent.x, agent.y)
                agent.x += agent.vx
                agent.y += agent.vy
                logger.debug(
                    f"Final Position: {agent.x, agent.y}, Velocity: {agent.vx, agent.vy}"
                )

                # Check for changes in the agent cell
                # for wall in self.floorplan.cells[agent.cell]:
                #     if wall.intersects((old_pos, (agent.x, agent.y))):
                #         # print(
                #         #     agent.cell,
                #         #     wall.connection[wall.connection[0] == agent.cell],
                #         # )
                #         agent.cell = wall.connection[wall.connection[0] == agent.cell]
                agent.cell = (agent.x > 50) + 1

    def calculateForce(self, agent):
        """Calculates the forces acting on a given agent

        Forces are of the following types:
                - Walls (repellant)
                - Other agents (repellant)
                - Goal (attractive)

        Parameters
        ----------
        agent: Agent
                The agent in consideration

        Returns
        -------
        Tuple[int, int]
                The X and Y components of the final force
        """

        fx = 0
        fy = 0

        # Wall forces
        for wall in self.floorplan.cells[agent.cell]:
            # Get the perpendicular
            per = wall.get_perpendicular((agent.x, agent.y))
            if per == (inf, inf):
                # Not in range
                continue

            per_length = sqrt(per[0] ** 2 + per[1] ** 2)
            if (
                per_length != 0
                and per_length <= self.params.repulsion_factors.WALL_FORCE_MARGIN
            ):
                force_per_length = (
                    self.params.repulsion_factors.WALL_FORCE_CONSTANT / per_length
                )
                fx += per[0] * force_per_length
                fy += per[1] * force_per_length

        # Agent-agent forces
        for other_agent in self.frame[agent.cell]:
            # Get the connecting vector
            vec = agent.vec_to_agent(other_agent)

            vec_length = sqrt(vec[0] ** 2 + vec[1] ** 2)
            if (
                vec_length != 0
                and vec_length < self.params.repulsion_factors.AGENT_FORCE_MARGIN
            ):
                logger.debug(f"Vector Length: {vec_length}")
                force_per_length = (
                    self.params.repulsion_factors.AGENT_FORCE_CONSTANT / vec_length**3
                )
                fx += vec[0] * force_per_length
                fy += vec[1] * force_per_length

        if agent.cell == agent.dest:
            # Goal forces are not applicable
            return (fx, fy)

        # Goal forces
        min_door = None
        min_distance = inf
        for next_door in self.floorplan.doors[agent.cell]:
            for dest_door in self.floorplan.doors[agent.dest]:
                # Calculate total distance of the trip
                dist = (
                    next_door.distance_to_door((agent.x, agent.y))
                    + self.floorplan.distances[next_door.door_node][dest_door.door_node]
                )

                if dist < min_distance:
                    # Update closest door
                    min_distance = dist
                    min_door = next_door

        if min_door == None:
            # Single cell floorplan
            # Goal forces not applicable
            return (fx, fy)

        # Calculate attractive force from min_door
        vec = min_door.vec_to_door((agent.x, agent.y))
        vec_length = sqrt(vec[0] ** 2 + vec[1] ** 2)
        if vec_length != 0:
            force_per_length = (
                self.params.repulsion_factors.GOAL_FORCE_CONSTANT / vec_length**3
            )
            fx += vec[0] * force_per_length
            fy += vec[1] * force_per_length

        logger.debug(f"Forces: {fx, fy}")
        return (fx, fy)
