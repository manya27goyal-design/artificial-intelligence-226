'''This program simulates an Unmanned Ground Vehicle (UGV) navigating through a battlefield grid 
to find the shortest path from a start node to a goal node while avoiding obstacles.
The battlefield is represented as a 20 × 20 grid (which can be changed to 70 × 70) where 0 
represents free space and 1 represents obstacles. Obstacles are generated randomly with low, medium, 
or high density. The program uses the Breadth-First Search (BFS) algorithm, which explores neighbouring
cells level by level using a queue and guarantees the shortest path when all moves have equal cost.
To run the program, save the code in a Python file (e.g., bfsnavigation.py)
and execute it using python bfsnavigation.py. The program outputs the start and goal
positions, whether a path was found, the shortest path, path length, number of nodes expanded,
 and execution time, which serve as the Measures of Effectiveness for evaluating the UGV navigation performance.'''
import random

from collections import deque
import time
SIZE = 20
densities = {
    "low": 0.1,
    "medium": 0.2,
    "high": 0.35
}
def gridgen(size, density):
    grid = [[0 for _ in range(size)] for _ in range(size)]
    for i in range(size):
        for j in range(size):
            if random.random() < density:
                grid[i][j] = 1
    return grid

def bfs(grid, start, goal):
    rows = len(grid)
    cols = len(grid[0])

    queue = deque([start])
    visited = set([start])
    parent = {}

    directions = [(1,0),(-1,0),(0,1),(0,-1)]
    expnodes = 0

    while queue:
        curr = queue.popleft()
        expnodes += 1

        if curr == goal:
            path = []
            while curr in parent:
                path.append(curr)
                curr = parent[curr]
            path.append(start)
            path.reverse()
            return path, expnodes

        for d in directions:
            neighbor = (curr[0] + d[0], curr[1] + d[1])

            if (0 <= neighbor[0] < rows and
                0 <= neighbor[1] < cols and
                grid[neighbor[0]][neighbor[1]] == 0 and
                neighbor not in visited):

                queue.append(neighbor)
                visited.add(neighbor)
                parent[neighbor] = curr

    return None, expnodes
denlev = "low"
density = densities[denlev]
grid = gridgen(SIZE, density)
start = (0, 0)
goal = (SIZE-1, SIZE-1)
grid[start[0]][start[1]] = 0
grid[goal[0]][goal[1]] = 0
starttime = time.time()
path, nodes = bfs(grid, start, goal)
endtime = time.time()
print("Start:", start)
print("Goal:", goal)
print("Density Level:", denlev)
if path:
    print("Path Found")
    print("Path:", path)
    print("Path Length:", len(path))
else:
    print("No Path Found")

print("\nMeasures of Effectiveness")
print("Nodes Expanded:", nodes)
print("Execution Time:", endtime - starttime, "seconds")
