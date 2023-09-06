from datetime import now as curr_time
from random import seed, uniform, random
from bisect import bisect_left

from floorplan.floorplan import Floorplan
from frame import Frame
from params import Params
from agent import Agent

class Simulation:
	"""Controls the flow of the simulation.

	The simulation is an agent based simulation where the "people" (represented by agents) are free to move within a virtual 2D floorplan. The movement of the agents are controlled by some forces (attractive or repulsive) as well as some random element of free will for each agent. Further more

	Attributes
	----------
	params: Params
			Starting simulation parameters
	floorplan: Floorplan
			The floorplan of the simulation space
	frame: Frame
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
	"""

	def __init__(self, params, floorplan):
		"""Initialized the simulation

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
		"""

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

		agents = []
		for dest, num_agents in enumerate(self.floorplan.distribution):
			for _ in range(num_agents):
				x = uniform(0, self.params.WIDTH)
				y = uniform(0, self.params.HEIGHT)
				cell = self.floorplan.find_cell(x, y)
				age = bisect_left(self.params.POPULATION_DEMOGRAPHICS, random())

				# Create agent
				agents.append(Agent(cell, x, y, age, dest))

		# Create frame
		self.frame = Frame(agents)

	def runSimulation(self):
		"""Run the simulation.

		Run an agent based simulation based on the
		configuration of the current simulation.

		Parameters
		----------

		Yields
		------
		Frame
			Constantly yields frames of simulation as they are calculated

		Returns
		-------
		None
		"""

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
