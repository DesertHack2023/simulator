from floorplan.floorplan import Wall
from math import inf

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
	doorTocell: List[List[float]]
		The distances between every pair of door and cell
	
	Methods
	-------
	__init__(graph: List[List[int]], walls: List[List[int]])
		Initializes the floorplan and stores information
	find_cell(x: int, y: int)
		Given the coordinates of a point, find the cell it lies in
	find_shortest_paths()
		Calculate the shortest path between every pair of door and cell
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

		# Find shortest distances between every pair of door and cell
		self.find_shortest_paths()
	
	def find_shortest_paths(self):
		'''Calculate the shortest path between every pair of door and cell

		This function uses the Flloyd-Warshall algorithm to compute the 
		All Pair Shortest Path (APSP) between every pair of doors in the floorplan.

		Parameters
		----------

		Returns
		-------
		'''

		# Create a list of doors
		doors = [wall for walls in self.cells for wall in walls if wall.state == Wall.DOOR]
		num_doors = len(doors)
		distance = [[inf] * num_doors for _ in range(num_doors)]

		# Distance between each door and itself is 0
		for i in range(num_doors):
			distance[i][i] = 0

		# Distances for doors in the same cell is known

		# Flloyd-Warshall's algorithm
		for k in range(num_doors):
			for i in range(num_doors):
				for j in range(num_doors):
					distance[i][j] = min(
							distance[i][j],
							distance[i][k] + distance[k][j]
						)
	
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

