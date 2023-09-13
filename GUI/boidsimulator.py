import logging
from dataclasses import dataclass, field
from math import sqrt

logger = logging.getLogger("GUI.boids")


def distance(
    p1: tuple[float, float] | list[float], p2: tuple[float, float] | list[float]
):
    return sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


@dataclass
class Agent:
    position: list[float]
    velocity: list[float]

    @property
    def velocity_vector(self):
        return [
            self.position[i] + self.velocity[i] * 3 / self.speed() for i in range(2)
        ]

    def speed(self):
        return sqrt(sum(i**2 for i in self.velocity))


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
    def __init__(self, initial_boids: list[Agent]):
        self.boids = initial_boids
        self.centre_of_mass_tendency = 0.01
        self.repulsion_radius = 2
        self.fomo_factor = 0.125
        self.v_lim = 2
        self.x_max = 600
        self.x_min = 100
        self.y_max = 300
        self.y_min = 100

    def com_vector(self, boid: Agent):
        num_boids = len(self.boids)
        perceived_centre = (
            sum(boid.position[0] for i in self.boids if i != boid) / (num_boids - 1),
            sum(boid.position[1] for i in self.boids if i != boid) / (num_boids - 1),
        )
        x = (perceived_centre[0] - boid.position[0]) * self.centre_of_mass_tendency
        y = (perceived_centre[1] - boid.position[1]) * self.centre_of_mass_tendency
        return x, y

    def repulsion_vector(self, boid: Agent):
        c_x = 0
        c_y = 0
        for b in self.boids:
            if b != boid:
                if distance(b.position, boid.position) < self.repulsion_radius:
                    c_x -= b.position[0] - boid.position[0]
                    c_y -= b.position[1] - boid.position[1]
        return c_x, c_y

    def fomo_vector(self, boid: Agent):
        # Boids try to match veloocity with nearby boids
        num_boids = len(self.boids)
        perceived_velocity = (
            sum(boid.velocity[0] for i in self.boids if i != boid) / (num_boids - 1),
            sum(boid.velocity[1] for i in self.boids if i != boid) / (num_boids - 1),
        )
        x = (perceived_velocity[0] - boid.velocity[0]) * self.fomo_factor
        y = (perceived_velocity[1] - boid.velocity[1]) * self.fomo_factor
        return x, y

    def limit_velocity(self, boid: Agent):
        speed = boid.speed()
        if speed > self.v_lim:
            boid.velocity[0] = boid.velocity[0] / speed * self.v_lim
            boid.velocity[1] = boid.velocity[1] / speed * self.v_lim

    def bound_position(self, boid: Agent):
        vector = [0, 0]
        if boid.position[0] < self.x_min:
            vector[0] = 10
        elif boid.position[0] > self.x_max:
            vector[0] = -10

        if boid.position[1] < self.y_min:
            vector[1] = 10
        elif boid.position[0] > self.y_max:
            vector[1] = -10
        return vector

    def next_frame(self):
        logger.debug("Calculating frame...")
        for boid in self.boids:
            v1 = self.com_vector(boid)
            v2 = self.repulsion_vector(boid)
            v3 = self.fomo_vector(boid)
            v4 = self.bound_position(boid)

            boid.velocity[0] += v1[0] + v2[0] + v3[0] + v4[0]
            boid.velocity[1] += v1[1] + v2[1] + v3[1] + v4[1]
            self.limit_velocity(boid)

            boid.position[0] += boid.velocity[0]
            boid.position[1] += boid.velocity[1]

    def run(self):
        # figure out a clean cancel mechanism later, ctrl-C for now
        while True:
            self.next_frame()
            yield self.boids


def test_boids():
    import itertools
    import random

    random_positions = list(
        [random.random() * 100 + 100, random.random() * 100 + 100] for _ in range(100)
    )
    random_velocities = list([random.random(), random.random()] for _ in range(100))
    return [
        Agent(p, v)
        for p, v in itertools.zip_longest(random_positions, random_velocities)
    ]


if __name__ == "__main__":
    import time

    boids = list(Agent([100, 100], [0, 0]) for _ in range(25))
    sim = Simulation(boids)
    for frame in sim.run():
        time.sleep(1)
        for boid in frame:
            print(boid)
        print("-" * 30)
