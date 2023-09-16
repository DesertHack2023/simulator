import logging
from dataclasses import dataclass, field
from math import sqrt
from typing import ClassVar

import numpy as np

logger = logging.getLogger("GUI.boids")


def distance(
    p1: tuple[float, float] | list[float], p2: tuple[float, float] | list[float]
):
    return sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


@dataclass
class Agents:
    positions: np.ndarray
    velocities: np.ndarray
    random_generator: ClassVar = None

    def iter_agents(self):
        for position, velocity in zip(self.positions, self.velocities):
            yield position, velocity

    @classmethod
    def random_from_seed(cls, seed, count=200, edge_length=800, offset=(0, 0)):
        logger.debug(f"Generated {count} agents with random seed: {seed}")
        if not cls.random_generator:
            cls.random_generator = np.random.default_rng(seed)
        positions = cls.random_generator.random(size=(count, 2)) * edge_length + offset
        velocities = cls.random_generator.random(size=(count, 2))
        return cls(positions, velocities)


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

    def foot_of_the_perpendicular(self, point: tuple[float, float]):
        dot = (point[0] - self.p1[0]) * self.unit_vector[0] + (
            point[1] - self.p1[1]
        ) * self.unit_vector[1]
        if dot >= 0 and dot < self.length:
            return (
                self.p1[0] + dot * self.unit_vector[0],
                self.p1[1] + dot * self.unit_vector[1],
            )


class Simulation:
    def __init__(self, initial_boids: Agents):
        self.agents = initial_boids
        self.visibility = 50
        self.com_strength = 0.01

    def update_agents(self):
        for agent in self.agents.positions:
            mask = self.mask(agent)
            positions = np.ma.array(self.agents.positions, mask=mask)
            # velocities = np.ma.array(self.agents.velocities, mask=mask)
            com_velocity = self.com_velocity(positions)
            self.agents.velocities -= com_velocity
        scale = np.sqrt(np.sum(self.agents.velocities**2, axis=1))
        self.agents.velocities /= scale[:, np.newaxis]

        # logger.debug(self.agents.velocities)
        self.agents.positions += self.agents.velocities

    def com_velocity(self, positions):
        centre = np.mean(positions, axis=0)
        vector_to_centre = (positions - centre) * self.com_strength
        return vector_to_centre

    def mask(self, reference):
        distance_array = np.sqrt(
            np.sum((self.agents.positions - reference) ** 2, axis=1)
        )
        mask = distance_array < self.visibility
        return np.stack((mask, mask), axis=1)

    def run(self):
        while True:
            self.update_agents()
            yield self.agents


if __name__ == "__main__":
    boids = Agents.random_from_seed(23)
