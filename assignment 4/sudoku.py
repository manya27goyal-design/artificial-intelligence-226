def backtracking_search(variables, domains, adjacencies, assignment=None):
    if assignment is None:
        assignment = {}

    if len(assignment) == len(variables):
        return assignment

    unassigned = [v for v in variables if v not in assignment]
    
    # Optional: MRV Heuristic for faster solving
    var = min(unassigned, key=lambda v: len(domains[v]))

    for value in domains[var]:
        consistent = True
        for neighbor in adjacencies.get(var, []):
            if neighbor in assignment and assignment[neighbor] == value:
                consistent = False
                break
        
        if consistent:
            assignment[var] = value
            result = backtracking_search(variables, domains, adjacencies, assignment)
            if result is not None:
                return result
            del assignment[var]
            
    return None

def solve_sudoku(grid):
    vars = [(r, c) for r in range(9) for c in range(9)]
    
    # Fixed domains to respect pre-filled values
    domains = {v: ([grid[v[0]][v[1]]] if grid[v[0]][v[1]] != 0 else list(range(1, 10))) for v in vars}
    
    adj = {}
    for r, c in vars:
        neighbors = set()
        for i in range(9):
            if i != c: neighbors.add((r, i))
            if i != r: neighbors.add((i, c))
        
        br, bc = 3 * (r // 3), 3 * (c // 3)
        for i in range(br, br + 3):
            for j in range(bc, bc + 3):
                if (i, j) != (r, c):
                    neighbors.add((i, j))
        adj[(r, c)] = list(neighbors)

    # Start with pre-filled values already in the assignment
    initial_assignment = {(r, c): grid[r][c] for r, c in vars if grid[r][c] != 0}
    
    return backtracking_search(vars, domains, adj, initial_assignment)

def print_board(solution):
    for r in range(9):
        if r % 3 == 0 and r != 0:
            print("- " * 11)
        line = ""
        for c in range(9):
            if c % 3 == 0 and c != 0:
                line += "| "
            line += str(solution[(r, c)]) + " "
        print(line)

board = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

result = solve_sudoku(board)
if result:
    print_board(result)