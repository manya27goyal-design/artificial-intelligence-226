from constraint import Problem

def solve_australia():
    problem = Problem()
    states = ['WA', 'NT', 'SA', 'Q', 'NSW', 'V', 'T']
    colors = ['Red', 'Green', 'Blue']
    
    problem.addVariables(states, colors)
    
    # Adjacency constraints
    adjacencies = [
        ('WA', 'NT'), ('WA', 'SA'),
        ('NT', 'SA'), ('NT', 'Q'),
        ('SA', 'Q'), ('SA', 'NSW'), ('SA', 'V'),
        ('Q', 'NSW'),
        ('NSW', 'V')
    ]
    
    for (a, b) in adjacencies:
        problem.addConstraint(lambda x, y: x != y, (a, b))
    
    solution = problem.getSolution()
    print("Australia Map Coloring Solution:", solution)

solve_australia()