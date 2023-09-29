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
class Params:
    visibility: int = 50
    cohesion: float = 0.001
    separation: int = 50
    alignment: float = 0.05
    duration: int = 120


class Simulation:
    def __init__(self, initial_boids: Agents, params: Params):
        self.agents = initial_boids
        self.params = params
        self.running = False

    def update_agents(self):
        for index, agent in enumerate(self.agents.positions):
            cohesion_alignment_mask = self.mask(agent, self.params.visibility)
            separation_mask = self.mask(agent, self.params.separation)
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
        # self.bound_positions()
        scale = np.sqrt(np.sum(self.agents.velocities**2, axis=1))
        self.agents.velocities /= scale[:, np.newaxis]
        # logger.debug(self.agents.velocities)
        self.agents.positions += self.agents.velocities

    def cohesion_fn(self, positions, reference):
        centre = np.mean(positions, axis=0)
        vector_to_centre = (centre - reference) * self.params.cohesion
        return vector_to_centre

    def alignment_fn(self, velocities, reference):
        mean_velocity = np.mean(velocities, axis=0)
        vector_to_mean_velocity = (mean_velocity - reference) * self.params.alignment
        return vector_to_mean_velocity

    def separation_fn(self, positions, reference):
        diff = reference - positions
        scale = np.sqrt(np.sum(diff**2, axis=1)) ** 2
        diff /= scale[:, np.newaxis]
        return np.mean(diff, axis=0)

    def avoid_walls(self):
        logger.debug(self.agents.positions)
        logger.debug(self.agents.velocities)

        below_0 = self.agents.positions <= 0
        self.agents.velocities = np.where(
            below_0, self.agents.velocities + 1, self.agents.velocities
        )

        above_bounds = self.agents.positions >= 400
        self.agents.velocities = np.where(
            above_bounds, self.agents.velocities - 1, self.agents.velocities
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
        for i in range(self.params.duration):
            start = time.perf_counter()
            self.update_agents()
            yield self.agents
            t = time.perf_counter() - start
            logger.debug(
                f"Frame {i + 1}/{self.params.duration} computed in {t:.3f} seconds"
            )
