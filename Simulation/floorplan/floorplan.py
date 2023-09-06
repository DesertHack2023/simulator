from floorplan.floorplan import Wall

class Floorplan:
	'''Contains information and behaviours regarding the floorplan of the simulation space

	Attributes
	----------
	num_cells: int
			The number of cells in the simulation space
	graph: List[List[int]]
			The adjacency list representation of the connections between cells
	cells: List[List[Wall]]
			The list of walls for each cell polygon
	distribution: List[int]
			The intended distribution of each person amongst the cells
	
	Methods
	-------
	__init__(graph: List[List[int]], walls: List[List[int]])
			Initializes the floorplan and stores information
	find_cell(x: int, y: int)
			Given the coordinates of a point, find the cell it lies in
	'''

	def __init__(self, graph, cells, distribution):
		'''Initializes the floorplan and stores information

		Parameters
		----------
		graph: List[List[int]]
				The adjacency list representation of the connections between cells
		cells: List[List[Wall]]
				The list of walls for each cell polygon
		distribution: List[int]
				The intended distribution of each person amongst the cells

		Returns
		-------
		None
		'''

		self.num_cells = len(graph)
		self.graph = graph
		self.cells = cells
		self.distribution = distribution
	
	def find_cell(self, x, y):
		'''Given the coordinates of a point, find the cell it lies in
		
		Parameters
		----------
		x: int
			The X-coordinate of the point
		y: int
			The Y-coordinate of the point

		Returns
		-------
		int
			The cell no. that the point belongs to
		'''

		for cell_no, walls in enumerate(self.cells):
			# Check number of walls that intersect with the line
			# (0, y) -> (x, y)
			intersections = 0
			for wall in walls:
				intersections += wall.intersects(((0, y), (x, y)))

			# If the num of intersections is odd, the point is inside the cell
			if intersections % 2 == 1:
				return cell_no

