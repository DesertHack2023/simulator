import logging
from collections import defaultdict
from math import inf

from .wall import Wall

logger = logging.getLogger("Simulation.Floorplan")


class Floorplan:
    """Contains information and behaviours regarding the floorplan of the simulation space

    Attributes
    ----------
    num_cells: int
            The number of cells in the simulation space
    cells: List[List[Wall]]
            The list of walls for each cell
    distribution: List[int]
            The intended distribution of each person amongst the cells
    distances: List[List[float]]
            The distances between every pair of doors
    doors: List[List[Wall]]
            THe list of doors for each cell

    Methods
    -------
    __init__(graph: List[List[int]], walls: List[List[int]])
            Initializes the floorplan and stores information
    find_cell(x: int, y: int)
            Given the coordinates of a point, find the cell it lies in
    find_shortest_paths()
            Calculate the shortest path between every pair of door and cell
    """

    def __init__(self, cells, distribution):
        """Initializes the floorplan and stores information

        Parameters
        ----------
        cells: List[List[Wall]]
                        The list of walls for each cell polygon
        distribution: List[int]
                        The intended distribution of each person amongst the cells

        Returns
        -------
        None
        """

        self.num_cells = len(cells)
        self.cells = cells
        self.distribution = distribution

        # Filter list of doors
        self.doors = [
            [wall for wall in walls if wall.state == Wall.DOOR] for walls in self.cells
        ]

        # Find shortest distances between every pair of door and cell
        self.find_shortest_paths()

    def find_shortest_paths(self):
        """Calculate the shortest path between every pair of doors

        This function uses the Flloyd-Warshall algorithm to compute the
        All Pair Shortest Path (APSP) between every pair of doors in the floorplan.

        Parameters
        ----------

        Returns
        -------
        """

        # Find edges of doors
        doors = []
        edges = []
        for cell_no, walls in enumerate(self.cells):
            for i in range(len(self.doors[cell_no])):
                # Assign a node number
                self.doors[cell_no][i].door_node = len(doors) + i

                # Distance between each door and itself is 0
                edges.append((len(doors) + i, len(doors) + i, 0))

                for j in range(i + 1, len(self.doors[cell_no])):
                    # Compute distance between each pair of edges
                    door_center = (
                        (
                            self.doors[cell_no][j].endpoints[0][0]
                            + self.doors[cell_no][j].endpoints[1][0]
                        )
                        / 2,
                        (
                            self.doors[cell_no][j].endpoints[0][1]
                            + self.doors[cell_no][j].endpoints[1][1]
                        )
                        / 2,
                    )
                    edges.append(
                        (
                            len(doors) + i,
                            len(doors) + j,
                            self.doors[cell_no][i].distance_to_door(door_center),
                        )
                    )

            doors += self.doors[cell_no]

        # Compute adjacency matrix of the graph
        num_doors = len(doors)
        self.distances = [[inf] * num_doors for _ in range(num_doors)]
        for u, v, w in edges:
            self.distances[u][v] = w
            self.distances[v][v] = w

        # Flloyd-Warshall's algorithm
        for k in range(num_doors):
            for i in range(num_doors):
                for j in range(num_doors):
                    self.distances[i][j] = min(
                        self.distances[i][j],
                        self.distances[i][k] + self.distances[k][j],
                    )

    def find_cell(self, x, y):
        """Given the coordinates of a point, find the cell it lies in

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
        """
        # for cell_no in range(1, len(self.cells)):
        #     # Check number of walls that intersect with the line
        #     # (0, y) -> (x, y)
        #     intersections = 0
        #     for wall in self.cells[cell_no]:
        #         intersections += wall.intersects(((0, y), (x, y)))
        #
        #     # If the num of intersections is odd, the point is inside the cell
        #     if intersections % 2 == 1:
        #         logger.debug(f"{x, y} lies in cell {cell_no}")
        #         return cell_no
        #
        # logger.debug(f"{x, y} lies in cell 0")
        #
        # # return 1 if x > 50 else 2
        # # Outside all cells
        # return 0
        return (x > 50) + 1

    @classmethod
    def make_default_layout(cls):
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

        return cls([cells[i] for i in range(len(cells))], [0, 0, 50])
