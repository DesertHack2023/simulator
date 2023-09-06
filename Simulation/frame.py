from agent import Agent


class Frame:
	"""Stores information about each frame in the simulation

	Attributes
	----------
	agents: List[List[Agent]]
			List of people in each cell of the simulation space

	Methods
	-------
	__init__(self: Frame, agents: List[List[Agent]])
	"""

	def __init__(self, agents):
		'''Initializes the Agents within the frame

		Parameters
		----------
		agents: List[List[Agents]]
				List of people in each cell of the simulation space

		Returns
		-------
		None
		'''

		self.agents = agents
