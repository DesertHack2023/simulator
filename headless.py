from collections import defaultdict

import numpy as np
from matplotlib import pyplot as plt

from Simulation.simulation import Simulation
from Simulation.params import Params
from Simulation.wall import Wall
from Simulation.floorplan import Floorplan

walls = [
	Wall(((0, 0), (50, 0)), 1, (0, 1)),
	Wall(((50, 0), (100, 0)), 1, (0, 2)),
	Wall(((100, 0), (100, 100)), 1, (0, 2)),
	Wall(((100, 100), (50, 100)), 1, (0, 2)),
	Wall(((50, 100), (0, 100)), 1, (0, 1)),
	Wall(((0, 100), (0, 0)), 1, (0, 1)),
	Wall(((50, 0), (50, 45)), 1, (1, 2)),
	Wall(((50, 55), (50, 100)), 1, (1, 2)),
	Wall(((50, 45), (50, 55)), 0, (1, 2)),
]

cells = defaultdict(lambda: [])
for wall in walls:
	cells[wall.connection[0]].append(wall)
	cells[wall.connection[1]].append(wall)

simulation = Simulation(
	Params(), Floorplan([cells[i] for i in range(len(cells))], [0, 0, 100])
)

plt.ion()
fig, ax = plt.subplots()

wall_x, wall_y = [], []
for wall in walls:
	if wall.state == Wall.DOOR:
		continue
	points = (
		(wall.endpoints[0][0], wall.endpoints[1][0]),
		(wall.endpoints[0][1], wall.endpoints[1][1]),
	)
	for i in range(min(points[0]), max(points[0]) + 1):
		for j in range(min(points[1]), max(points[1]) + 1):
			wall_x.append(i)
			wall_y.append(j)

sc = ax.scatter(wall_x, wall_y)
plt.xlim(0, 100)
plt.ylim(0, 100)

for agents in simulation.run():
	# for i in range(len(agents)):
	# print(f"{i}: ", end="")
	# for agent in agents[i]:
	#     print(f"({agent.x}, {agent.y}) ", end="")
	# print()

	x = [agent.x for cell_agents in agents for agent in cell_agents]
	y = [agent.y for cell_agents in agents for agent in cell_agents]
	x += wall_x
	y += wall_y

	sc.set_offsets(np.c_[x, y])
	fig.canvas.draw_idle()
	plt.pause(0.1)

plt.waitforbuttonpress()
