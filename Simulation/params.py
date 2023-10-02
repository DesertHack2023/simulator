from dataclasses import dataclass, field


@dataclass
class Basic_Params:
    # Basic model related parameters
    WIDTH: int = 100
    HEIGHT: int = 100
    POPULATION_SIZE: int = 100
    POPULATION_DEMOGRAPHICS: list[int | float] = field(default_factory=list)
    SIMULATION_LENGTH: int = 1000
    MAX_MOVEMENT: float = 0.05
    TRAVEL_RATE: float = 0.1
    RANDOM_SEED: int = 0
    MAX_VELOCITY: int = 1

    def __post_init__(self):
        self.POPULATION_DEMOGRAPHICS = [0.35, 0.8, 0.95, 1]


@dataclass
class Repulsion_Factors:
    CONTACT_RADIUS: float = 0.5
    CONTACT_RADIUS_SQUARED: float = CONTACT_RADIUS**2

    # Forces
    WALL_FORCE_CONSTANT: float = 1
    WALL_FORCE_MARGIN: float = 10
    AGENT_FORCE_CONSTANT: float = 1
    AGENT_FORCE_MARGIN: float = 5
    GOAL_FORCE_CONSTANT: float = 100


@dataclass
class Params:
    # Contact radius
    # The contact radius is a function of the population density
    # CONTACT_RADIUS = 3 / POPULATION_DENSITY
    basic_parameters: Basic_Params = Basic_Params()
    repulsion_factors: Repulsion_Factors = Repulsion_Factors()
