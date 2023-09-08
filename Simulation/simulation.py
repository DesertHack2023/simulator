from datetime import datetime
from random import seed, uniform, random
from bisect import bisect_left
from math import sqrt, inf

from floorplan import Floorplan
from params import Params
from agent import Agent

class Simulation:
	'''Controls the flow of the simulation.

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
	'''

	def __init__(self, params, floorplan):
		'''Initialized the simulation

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
		'''

		self.params  = params
		self.floorplan = floorplan
		self.initializeFrame()

	def initializeFrame(self):
		'''Creates the first frame of the simulation

		Parameters
		----------

		Returns
		-------
		None
		'''

		agents = [[] for _ in range(self.floorplan.num_cells)]
		for dest, num_agents in enumerate(self.floorplan.distribution):
			for _ in range(num_agents):
				x = uniform(0, self.params.WIDTH)
				y = uniform(0, self.params.HEIGHT)
				cell = self.floorplan.find_cell(x, y)
				print(x, y, cell, dest)
				age = bisect_left(self.params.POPULATION_DEMOGRAPHICS, random())

				# Create agent
				agents[cell].append(Agent(cell, x, y, age, dest))

		# Create frame
		self.frame = agents
		# exit()

	def runSimulation(self):
		'''Run the simulation.

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
		'''

		# Reset random seed to current system time
		# Initalize and save seed
		startTime = datetime.now()
		self.params.RANDOM_SEED = (
			startTime.hour * 10000 + startTime.minute * 100 + startTime.second
		)
		seed(self.params.RANDOM_SEED)

		# Yield the first frame
		yield self.frame

		for _ in range(self.params.SIMULATION_LENGTH):
			# Calculate the next frame and then yield it
			self.nextFrame()
			yield self.frame


	def nextFrame(self):
		'''Calculates the next frame of the simulation

		Parameters
		----------

		Returns
		-------
		None
		'''

		self.moveAgents()

	def moveAgents(self):
		'''Implements movement of the agents each frame

		Parameters
		----------

		Returns
		-------
		'''

		# Calculate force on each agent
		for cell_no, agents in enumerate(self.frame):
			for agent in agents:
				fx, fy = self.calculateForce(agent)

				# Update velocity
				agent.vx += fx
				agent.vy += fy
				v = sqrt(agent.vx ** 2 + agent.vy ** 2)
				if v > self.params.MAX_VELOCITY:
					agent.vx *= self.params.MAX_VELOCITY / v
					agent.vy *= self.params.MAX_VELOCITY / v

				# Update position
				old_pos = (agent.x, agent.y)
				agent.x += agent.vx
				agent.y += agent.vy

				# Check for changes in the agent cell
				for wall in self.floorplan.cells[agent.cell]:
					if wall.intersects((old_pos, (agent.x, agent.y))):
						print(agent.cell, wall.connection[wall.connection[0] == agent.cell])
						agent.cell = wall.connection[wall.connection[0] == agent.cell]
	
	def calculateForce(self, agent):
		'''Calculates the forces acting on a given agent

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
		'''

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
			if per_length != 0 and per_length <= self.params.WALL_FORCE_MARGIN:
				force_per_length = self.params.WALL_FORCE_CONSTANT / per_length ** 3
				fx += per[0] * force_per_length
				fy += per[1] * force_per_length

		# Agent-agent forces
		for other_agent in self.frame[agent.cell]:
			# Get the connecting vector
			vec = agent.vec_to_agent(other_agent)

			vec_length = sqrt(vec[0] ** 2 + vec[1] ** 2)
			if vec_length != 0 and vec_length < self.params.AGENT_FORCE_MARGIN:
				force_per_length = self.params.AGENT_FORCE_CONSTANT / vec_length ** 3
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
					next_door.distance_to_door((agent.x, agent.y)) + 
					self.floorplan.distances[next_door.door_node][dest_door.door_node]
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
			force_per_length = self.params.GOAL_FORCE_CONSTANT / vec_length ** 3
			fx += vec[0] * force_per_length
			fy += vec[1] * force_per_length
		
		return (fx, fy)

if __name__ == '__main__':
	from matplotlib import pyplot as plt
	import numpy as np
	from collections import defaultdict
	from wall import Wall

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
		Params(),
		Floorplan([cells[i] for i in range(len(cells))] , [0, 0, 100])
	)

	plt.ion()
	fig, ax = plt.subplots()
	
	wall_x, wall_y = [], []
	for wall in walls:
		if wall.state == Wall.DOOR:
			continue
		points = ((wall.endpoints[0][0], wall.endpoints[1][0]), (wall.endpoints[0][1], wall.endpoints[1][1]))
		for i in range(min(points[0]), max(points[0]) + 1):
			for j in range(min(points[1]), max(points[1]) + 1):
				wall_x.append(i)
				wall_y.append(j)

	sc = ax.scatter(wall_x, wall_y)
	plt.xlim(0, 100)
	plt.ylim(0, 100)

	for agents in simulation.runSimulation():
		for i in range(len(agents)):
			print(f'{i}: ', end = '')
			for agent in agents[i]:
				print(f'({agent.x}, {agent.y}) ', end = '')
			print()

		x = [agent.x for cell_agents in agents for agent in cell_agents]
		y = [agent.y for cell_agents in agents for agent in cell_agents]
		x += wall_x
		y += wall_y

		sc.set_offsets(np.c_[x, y])
		fig.canvas.draw_idle()
		plt.pause(0.1)
	
	plt.waitforbuttonpress()
