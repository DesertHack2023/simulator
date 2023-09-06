from floorplan.floorplan import wall

class Floorplan:
	'''Contains information and behaviours regarding the floorplan of the simulation space

	Attributes
	----------
	num_cells: int
			The number of cells in the simulation space
	graph: List[List[Tuple[int, List[Wall]]]]
			The adjacency list representation of the connections between cells
			with the information about shared walls
	cells: List[List[Wall]]
			The list of walls for each cell polygon
	
	Methods
	-------
	__init__(self: Floorplan, graph: List[List[int]], walls: List[List[int]])
			Initializes the floorplan and stores information
	'''


	def __init__(self, graph, cells):
		'''Initializes the floorplan and stores information

		Parameters
		----------
		graph: List[List[int]]
				The adjacency list representation of the connections between cells
		cells: List[List[Wall]]
				The list of walls for each cell polygon

		Returns
		-------
		None
		'''

		self.num_cells = len(graph)
		self.graph = graph
		self.cells = cells
