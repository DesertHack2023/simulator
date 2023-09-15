import logging
from collections import namedtuple
from dataclasses import astuple, dataclass, field
from math import sqrt

import jax.numpy as np
import numpy as onp
from jax import Array, jit, lax, random, vmap

vectorize = np.vectorize

import base64
from functools import partial

from jax_md import energy, minimize, partition, quantity, simulate, smap, space, util
from jax_md.util import f32

logger = logging.getLogger("GUI.boids")


@vmap
def normal(theta):
    return np.array([np.cos(theta), np.sin(theta)])


def distance(
    p1: tuple[float, float] | list[float], p2: tuple[float, float] | list[float]
):
    return sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


Agents = namedtuple("Agents", ["agent_array", "agent_theta"])


def iter_agents(agents: Agents):
    agent_array, agent_theta = agents
    normals = normal(agent_theta)
    for position, p2 in zip(agent_array, normals):
        yield tuple(position), tuple(position + p2)


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
    def __init__(self, initial_boids: Agents, box_size=800.0):
        self.boids = initial_boids
        self.update = self.dynamics(energy_fn=self.energy_fn(), dt=1e-1, speed=1.0)
        self.state = {"boids": self.boids}
        for x, y in zip(self.boids.agent_theta, self.boids.agent_array):
            logger.debug((x, y))
        self.displacement, self.shift = space.periodic(side=box_size)

    def energy_fn(self):
        @jit
        def func(state):
            boids = state["boids"]
            E_align = partial(self.align_fn, J_align=0.5, D_align=45.0, alpha=3.0)
            # Map the align energy over all pairs of boids. While both applications
            # of vmap map over the displacement matrix, each acts on only one normal.
            E_align = vmap(vmap(E_align, (0, None, 0)), (0, 0, None))

            E_avoid = partial(self.avoid_fn, J_avoid=25.0, D_avoid=30.0, alpha=3.0)
            E_avoid = vmap(vmap(E_avoid))

            E_cohesion = partial(self.cohesion_fn, J_cohesion=0.001, D_cohesion=10.0)

            dR = space.map_product(self.displacement)(
                boids.agent_array, boids.agent_array
            )
            N = normal(boids.agent_theta)
            return 0.5 * np.sum(E_align(dR, N, N) + E_avoid(dR) + E_cohesion(dR, N))

        return func

    @staticmethod
    def align_fn(dR, N_1, N_2, J_align, D_align, alpha):
        dR = lax.stop_gradient(dR)
        dr = space.distance(dR) / D_align
        energy = J_align / alpha * (1.0 - dr) ** alpha * (1 - np.dot(N_1, N_2)) ** 2
        return np.where(dr < 1.0, energy, 0.0)

    @staticmethod
    def avoid_fn(dR, J_avoid, D_avoid, alpha):
        dr = space.distance(dR) / D_avoid
        return np.where(dr < 1.0, J_avoid / alpha * (1 - dr) ** alpha, 0.0)

    @staticmethod
    def cohesion_fn(dR, N, J_cohesion, D_cohesion, eps=1e-7):
        dR = lax.stop_gradient(dR)
        dr = np.linalg.norm(dR, axis=-1, keepdims=True)

        mask = dr < D_cohesion

        N_com = np.where(mask, 1.0, 0)
        dR_com = np.where(mask, dR, 0)
        dR_com = np.sum(dR_com, axis=1) / (np.sum(N_com, axis=1) + eps)
        dR_com = dR_com / np.linalg.norm(dR_com + eps, axis=1, keepdims=True)
        return f32(0.5) * J_cohesion * (1 - np.sum(dR_com * N, axis=1)) ** 2

    def dynamics(self, energy_fn, dt, speed):
        @jit
        def update(_, state):
            R, theta = state["boids"]

            dstate = quantity.force(energy_fn)(state)
            dR, dtheta = dstate["boids"]
            n = normal(state["boids"].agent_theta)

            state["boids"] = Agents(
                self.shift(R, dt * (speed * n + dR)), theta + (dt * dtheta)
            )
            return state

        return update

    def run(self):
        while True:
            # infinite simulation
            self.state = lax.fori_loop(
                1, 50, self.update, self.state
            )  # 50 changes to the state, for each frame
            yield self.state


def test_boids() -> Agents:
    boid_count = 200
    dim = 2  # simulation is in 2D
    edge_length = 800

    # Create RNG state to draw random numbers (see LINK).
    rng = random.PRNGKey(0)

    # Initialize the boids.
    rng, R_rng, theta_rng = random.split(rng, 3)

    boids = Agents(
        agent_array=edge_length * random.uniform(R_rng, (boid_count, dim)),
        agent_theta=random.uniform(theta_rng, (boid_count,), maxval=2.0 * np.pi),
    )
    return boids


if __name__ == "__main__":
    boids = test_boids()
