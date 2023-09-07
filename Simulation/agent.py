class Agent:
	"""Defines characteristic attributes and behaviours for the agent

	Attributes
	----------
	cell: int
		The current cell that the agent is in
	x: float
		X-coordinate of the agent
	y: float
		Y-coordinate of the agent
	vx: float
		X-component of the velocity of the agent
	vy: float
		Y-component of the velocity of the agent
	age: int
		The age of the agent

	Methods
	-------
	__init__(self: Agent, cell: int, x: float, y: float, age: int)
		Initialize the agent with some properties
	vec_to_agent(other: Agent)
		Calculates the vector of the line segment between two agents
	"""

	def __init__(self, cell, x, y, age, dest):
		"""Sets some initial parameters for the person

		Parameters
		----------
		cell: int
			The starting cell of the agent
		x: int
			The starting X-coordinate
		y: int
			The starting Y-coordinate
		age: int
			The age of the agent
		dest: int
			The destination cell of the agent

		Returns
		-------
		None
		"""

		self.cell = cell
		self.x = x
		self.y = y
		self.vx = 0
		self.vy = 0
		self.age = age
		self.dest = dest
	
	def vec_to_agent(self, other):
		'''Calculates the vector of the line segment between two agents
		
		Parameters
		----------
		other: Agent
			The other agent in consideration

		Returns
		-------
		Tuple[float, float]
			The vector of the directed line segment between the two agents
		'''

		return (
			self.x - other.x,
			self.y - other.y
		)
