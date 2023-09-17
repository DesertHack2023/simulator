import logging
import time
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

    @property
    def count(self):
        return self.positions.shape[0]

    @classmethod
    def random_from_seed(cls, seed, count=100, edge_length=400, offset=(0, 0)):
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
        self.cohesion = 0.001
        self.separation = 50
        self.alignment = 0.05
        self.num_frames = 120

    def update_agents(self):
        for index, agent in enumerate(self.agents.positions):
            cohesion_alignment_mask = self.mask(agent, self.visibility)
            separation_mask = self.mask(agent, self.separation)
            cohesion_alignment_positions = np.ma.array(
                self.agents.positions, mask=cohesion_alignment_mask
            )
            separation_positions = np.ma.array(
                self.agents.positions, mask=separation_mask
            )
            velocities = np.ma.array(
                self.agents.velocities, mask=cohesion_alignment_mask
            )

            com_velocity = self.cohesion_fn(cohesion_alignment_positions, agent)
            separation_velocty = self.separation_fn(separation_positions, agent)
            alignment_velocity = self.alignment_fn(
                velocities, self.agents.velocities[index]
            )

            self.agents.velocities[index] += (
                separation_velocty + com_velocity + alignment_velocity
            )
        self.bound_positions()
        scale = np.sqrt(np.sum(self.agents.velocities**2, axis=1))
        # self.agents.velocities /= scale[:, np.newaxis]
        # logger.debug(self.agents.velocities)
        self.agents.positions += self.agents.velocities

    def cohesion_fn(self, positions, reference):
        centre = np.mean(positions, axis=0)
        vector_to_centre = (centre - reference) * self.cohesion
        return vector_to_centre

    def alignment_fn(self, velocities, reference):
        mean_velocity = np.mean(velocities, axis=0)
        vector_to_mean_velocity = (mean_velocity - reference) * self.alignment
        return vector_to_mean_velocity

    def separation_fn(self, positions, reference):
        diff = reference - positions
        scale = np.sqrt(np.sum(diff**2, axis=1))
        diff /= scale[:, np.newaxis]
        return np.mean(diff, axis=0)

    def bound_positions(self):
        logger.debug(self.agents.positions)
        logger.debug(self.agents.velocities)

        below_0 = self.agents.positions <= 0
        self.agents.velocities = np.where(
            below_0, self.agents.velocities + 5, self.agents.velocities
        )

        above_bounds = self.agents.positions >= 400
        self.agents.velocities = np.where(
            above_bounds, self.agents.velocities - 5, self.agents.velocities
        )

        logger.debug(self.agents.positions)
        logger.debug(self.agents.velocities)

    def mask(self, reference, range):
        distance_array = np.sqrt(
            np.sum((self.agents.positions - reference) ** 2, axis=1)
        )
        mask = distance_array < range
        return np.stack((mask, mask), axis=1)

    def run(self):
        for i in range(self.num_frames):
            start = time.perf_counter()
            self.update_agents()
            yield self.agents
            t = time.perf_counter() - start
            logger.debug(f"Frame {i + 1}/{self.num_frames} computed in {t:.3f} seconds")


if __name__ == "__main__":
    boids = Agents.random_from_seed(23)
