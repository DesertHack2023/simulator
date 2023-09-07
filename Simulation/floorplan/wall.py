from math import sqrt

class Wall:
	'''Stores information and behaviours of the walls of the cells

	Attributes
	----------
	endpoints: Tuple[Tuple[float, float], Tuple[float, float]]
		The end points of the wall
	state: int
		The integer that represents the type of wall
		(open / closed, exit etc.)
	connection: Tuple[float, float]
		The two cells connected through the wall

	Methods
	-------
	__init__(endpoints: Tuple[Tuple[float, float], Tuple[float, float]], state: int, connection: Tuple[float, float])
		Initializes the Wall instance
	orientation(a: Tuple[int, int], b: Tuple[int, int], c, Tuple[int, int]):
		Checks the orientation of any three points
	on_segment(a: Tuple[int, int], b: Tuple[int, int], c, Tuple[int, int]):
		Checks whether point b lies on line segment ac given a, b, c are collinear
	intersects(line: Tuple[Tuple[float, float], Tuple[float, float]]): bool
		Checks whether a line intersects with the wall
	distance_to_door(point: Tuple[int, int]):
		Calculates the distance between the door and a point
	get_perpendicular(point: Tuple[int, int]):
		Returns the perpendicular from a point to the wall
	'''

	# Wall states
	DOOR = 0
	WALL = 1

	def __init__(self, endpoints, state, connection):
		'''Initializes the Wall instance

		Parameters
		----------
		endpoints: Tuple[Tuple[float, float], Tuple[float, float]]
				The end points of the wall
		state: int
				The integer that represents the type of wall
				(open / closed, exit etc.)
		connection: Tuple[float, float]
				The two cells connected through the wall

		Returns
		-------
		None
		'''

		self.endpoints = endpoints
		self.state = state
		self.connection = connection

	def orientation(self, a, b, c):
		'''Checks the orientation of any three points

		Three points A, B, C may have the following orientations:
			- Collinear (0)
			- Clockwise (1)
			- Anti-clockwise (2)

		Parameters
		----------
		a: Tuple[float, float]
		b: Tuple[float, float]
		c: Tuple[float, float]
				Three points in consideration

		Returns
		-------
		int
			An integer representing the type of orientation
		'''

		x = (b[1] - a[1]) * (c[0] - b[0]) - (b[0] - a[0]) * (c[1] - b[1])
		if x < 0:
			# Clockwise
			return 1

		if x > 0:
			# Anti-clockwise
			return 2

		# Collinear
		return 0

	def on_segment(self, a, b, c):
		'''Checks whether point b lies on line segment ac given a, b, c are collinear

		Parameters
		----------
		a: Tuple[float, float]
		b: Tuple[float, float]
		c: Tuple[float, float]
				Three points in consideration

		Returns
		-------
		bool
			Whether b lies on ac
		'''

		return (
			(min(a[0], c[0]) <= b[0] and b[0] <= max(a[0], c[0])) and
			(min(a[1], c[1]) <= b[1] and b[1] <= max(a[1], c[1]))
		)

	def intersects(self, line):
		'''Checks whether a line intersects with the wall

		Parameters
		----------
		line: Tuple[Tuple[float, float], Tuple[float, float]]
				The endpoints of the line

		Returns
		-------
		bool
				Whether the line was intersecting
		'''

		triplets = [
			(line[0], self.endpoints[0], line[1]),
			(line[0], self.endpoints[0], self.endpoints[1])
			(line[1], self.endpoints[1], line[0])
			(line[1], self.endpoints[1], self.endpoints[0])
		]

		orientations = [self.orientation(*i) for i in triplets]

		# General case
		if (orientations[0] != orientations[1]) and (orientations[2] != orientations[3]):
			return True

		# Special cases
		for i in range(len(triplets)):
			if orientations[i] == 0 and self.on_segment(*triplets[i]):
				return True

		# Doesn't intersect
		return False

	def distance_to_door(self, point):
		'''Calculates the distance between the door and a point

		Parameters
		----------
		point: Tuple[int, int]
			The point from which we are measuring

		Returns
		-------
		float
			The distance between the two doors
		'''

		# Find the center points of the two doors
		self_center = (
			(self.endpoints[0][0] + self.endpoints[1][0]) / 2,
			(self.endpoints[0][1] + self.endpoints[1][1]) / 2
		)

		# Return the distance between these two points
		return sqrt(
			(self_center[0] - point[0]) ** 2 +
			(self_center[1] - point[1]) ** 2 
		)
	
	def get_perpendicular(self, point):
		'''Returns the perpendicular from a point to the wall

		'''
