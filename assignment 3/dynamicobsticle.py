'''This program will simulate the movement of an Unmanned Ground Vehicle (UGV) through the battlefield
 grid in order for the UGV to go towards the goal while avoiding obstacles in the battlefield grid. 
 The battlefield grid is simulated as a 2D grid where the free spaces in the grid are the open space in 
 the battlefield and the obstacles in the grid are the obstacles in the battlefield. The UGV will use the 
 Breadth-First Search (BFS) algorithm in order for the UGV to find the shortest path from the initial 
 location of the UGV towards the goal location in the battlefield grid. When the UGV moves through the 
 battlefield grid, obstacles in the battlefield grid may appear at any location in the grid, and the UGV 
 needs to replan the route in order for the UGV to move towards the goal in the battlefield grid.'''
import random
from collections import deque
SIZE = 15
def bfs(grid, start, goal):
    q = deque([start])
    visited = {start}
    parent = {}
    while q:
        x,y = q.popleft()
        if (x,y) == goal:
            path = []
            while (x,y) in parent:
                path.append((x,y))
                x,y = parent[(x,y)]
            path.append(start)
            return path[::-1]
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx,ny = x+dx, y+dy
            if 0<=nx<SIZE and 0<=ny<SIZE and grid[nx][ny]==0 and (nx,ny) not in visited:
                q.append((nx,ny))
                visited.add((nx,ny))
                parent[(nx,ny)] = (x,y)
    return None

grid = [[0]*SIZE for _ in range(SIZE)]

for i in range(SIZE):
    for j in range(SIZE):
        if random.random() < 0.15:
            grid[i][j] = 1
start = (0,0)
goal = (SIZE-1,SIZE-1)
grid[start[0]][start[1]] = 0
grid[goal[0]][goal[1]] = 0
curr = start
steps = 0
while curr != goal:
    path = bfs(grid, curr, goal)
    if not path:
        print("No path available")
        break
    nexstep = path[1]
    if random.random() < 0.2:
        x = random.randint(0,SIZE-1)
        y = random.randint(0,SIZE-1)
        grid[x][y] = 1
    if grid[nexstep[0]][nexstep[1]] == 1:
        continue
    curr = nexstep
    steps += 1
print("Steps taken:", steps)
print("Reached Goal:", curr == goal)
path = bfs(grid, start, goal)
print("\nBattlefield Grid")
for i in range(SIZE):
    for j in range(SIZE):
        if (i,j) == start:
            print("S", end=" ")
        elif (i,j) == goal:
            print("G", end=" ")
        elif path and (i,j) in path:
            print("*", end=" ")
        elif grid[i][j] == 1:
            print("#", end=" ")
        else:
            print(".", end=" ")
    print()
