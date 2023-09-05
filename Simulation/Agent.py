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
    age: int
            The age of the agent

    Methods
    -------
    __init__(self: Agent, cell: int, x: float, y: float, age: int)
            Initialize the agent with some properties
    """

    def __init__(self, cell, x, y, age):
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

        Returns
        -------
        None
        """

        self.cell = cell
        self.x = x
        self.y = y
        self.age = age
