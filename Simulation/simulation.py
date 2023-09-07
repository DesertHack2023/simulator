from datetime import now as curr_time
from random import seed, uniform, random
from bisect import bisect_left
from math import sqrt

from floorplan.floorplan import Floorplan
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
				age = bisect_left(self.params.POPULATION_DEMOGRAPHICS, random())

				# Create agent
				agents[cell].append(Agent(cell, x, y, age, dest))

		# Create frame
		self.frame = agents

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
		startTime = curr_time()
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
		for cell_no, agents in enumerate(self.frame.agents):
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
				agent.x += agent.vx
				agent.y += agent.vy
	
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
		pass
