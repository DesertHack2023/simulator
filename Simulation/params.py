from dataclasses import dataclass
from typing import NamedTuple


@dataclass
class Params:
    # Basic model related parameters
    WIDTH = 100
    HEIGHT = 100
    POPULATION_SIZE = 100
    POPULATION_DEMOGRAPHICS = [0.35, 0.8, 0.95, 1]
    SIMULATION_LENGTH = 1000
    MAX_MOVEMENT = 0.05
    TRAVEL_RATE = 0.1
    RANDOM_SEED = 0
    MAX_VELOCITY = 1

    # Contact radius
    # The contact radius is a function of the population density
    # CONTACT_RADIUS = 3 / POPULATION_DENSITY
    CONTACT_RADIUS = 0.5
    CONTACT_RADIUS_SQUARED = CONTACT_RADIUS**2

    # Forces
    WALL_FORCE_CONSTANT = 0.1
    WALL_FORCE_MARGIN = 1
    AGENT_FORCE_CONSTANT = 1
    AGENT_FORCE_MARGIN = 1
    GOAL_FORCE_CONSTANT = 1
