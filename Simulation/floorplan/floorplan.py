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
	distances: List[List[float]]
		The distances between every pair of doors

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
		'''Calculate the shortest path between every pair of doors

		This function uses the Flloyd-Warshall algorithm to compute the 
		All Pair Shortest Path (APSP) between every pair of doors in the floorplan.

		Parameters
		----------

		Returns
		-------
		'''

		# Find edges of doors
		doors = []
		edges = []
		for walls in self.cells:
			cell_doors = [wall for wall in walls if wall.state == Wall.DOOR]
			for i in range(len(cell_doors)):
				# Distance between each door and itself is 0
				edges.append((len(doors) + i, len(doors) + i, 0))

				for j in range(i + 1, len(cell_doors)):
					# Compute distance between each pair of edges
					door_center = (
						(cell_doors[j].endpoints[0][0] + cell_doors[j].endpoints[1][0]) / 2,
						(cell_doors[j].endpoints[0][1] + cell_doors[j].endpoints[1][1]) / 2
					)
					edges.append((
						len(doors) + i,
						len(doors) + j, 
						cell_doors[i].distance_to_door(door_center)
					))

			doors += cell_doors

		# Compute adjacency matrix of the graph
		num_doors = len(doors)
		distance = [[inf] * num_doors for _ in range(num_doors)]
		for u, v, w in edges:
			distance[u][v] = w
			distance[v][v] = w

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

