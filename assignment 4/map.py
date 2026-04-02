def backtracking_search(variables, domains, adjacencies, assignment=None):
    if assignment is None:
        assignment = {}

    # Check if all districts are colored
    if len(assignment) == len(variables):
        return assignment

    # Select the next unassigned district
    unassigned = [v for v in variables if v not in assignment]
    var = unassigned[0]

    for value in domains[var]:
        # Constraint Check: No neighbor can have the same color
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
            
            # Backtrack
            del assignment[var]
            
    return None

# 1. Define all 33 districts
districts = [
    "Adilabad", "Kumuram Bheem Asifabad", "Mancherial", "Nirmal", "Nizamabad",
    "Jagitial", "Peddapalli", "Kamareddy", "Rajanna Sircilla", "Karimnagar",
    "Jayashankar Bhupalpally", "Sangareddy", "Medak", "Siddipet", "Hanamkonda",
    "Mulugu", "Vikarabad", "Hyderabad", "Medchal-Malkajgiri", "Rangareddy",
    "Yadadri Bhuvanagiri", "Jangaon", "Warangal", "Mahabubabad", "Bhadradri Kothagudem",
    "Mahabubnagar", "Narayanpet", "Jogulamba Gadwal", "Wanaparthy", "Nagarkurnool",
    "Nalgonda", "Suryapet", "Khammam"
]

# 2. Define 4 colors (sufficient for any planar map)
colors = ["Red", "Green", "Blue", "Yellow"]
domains = {d: colors for d in districts}

# 3. Define Adjacencies (The Constraints)
# Based on the Telangana state map
adjacencies = {
    "Adilabad": ["Nirmal", "Kumuram Bheem Asifabad"],
    "Kumuram Bheem Asifabad": ["Adilabad", "Nirmal", "Mancherial"],
    "Mancherial": ["Kumuram Bheem Asifabad", "Nirmal", "Jagitial", "Peddapalli", "Jayashankar Bhupalpally"],
    "Nirmal": ["Adilabad", "Kumuram Bheem Asifabad", "Mancherial", "Jagitial", "Nizamabad"],
    "Nizamabad": ["Nirmal", "Jagitial", "Rajanna Sircilla", "Kamareddy"],
    "Jagitial": ["Nirmal", "Nizamabad", "Rajanna Sircilla", "Karimnagar", "Peddapalli", "Mancherial"],
    "Peddapalli": ["Mancherial", "Jagitial", "Karimnagar", "Jayashankar Bhupalpally", "Hanamkonda"],
    "Jayashankar Bhupalpally": ["Mancherial", "Peddapalli", "Hanamkonda", "Mulugu", "Warangal"],
    "Mulugu": ["Jayashankar Bhupalpally", "Warangal", "Mahabubabad", "Bhadradri Kothagudem"],
    "Bhadradri Kothagudem": ["Mulugu", "Mahabubabad", "Khammam"],
    "Khammam": ["Bhadradri Kothagudem", "Mahabubabad", "Suryapet"],
    "Suryapet": ["Khammam", "Mahabubabad", "Jangaon", "Yadadri Bhuvanagiri", "Nalgonda"],
    "Nalgonda": ["Suryapet", "Yadadri Bhuvanagiri", "Rangareddy", "Nagarkurnool"],
    "Nagarkurnool": ["Nalgonda", "Rangareddy", "Mahabubnagar", "Wanaparthy"],
    "Wanaparthy": ["Nagarkurnool", "Mahabubnagar", "Jogulamba Gadwal"],
    "Jogulamba Gadwal": ["Wanaparthy", "Mahabubnagar", "Narayanpet"],
    "Narayanpet": ["Jogulamba Gadwal", "Mahabubnagar", "Vikarabad"],
    "Mahabubnagar": ["Narayanpet", "Jogulamba Gadwal", "Wanaparthy", "Nagarkurnool", "Rangareddy", "Vikarabad"],
    "Vikarabad": ["Narayanpet", "Mahabubnagar", "Rangareddy", "Sangareddy"],
    "Rangareddy": ["Vikarabad", "Mahabubnagar", "Nagarkurnool", "Nalgonda", "Yadadri Bhuvanagiri", "Medchal-Malkajgiri", "Hyderabad", "Sangareddy"],
    "Hyderabad": ["Rangareddy", "Medchal-Malkajgiri"],
    "Medchal-Malkajgiri": ["Hyderabad", "Rangareddy", "Yadadri Bhuvanagiri", "Siddipet", "Sangareddy"],
    "Sangareddy": ["Vikarabad", "Rangareddy", "Medchal-Malkajgiri", "Medak", "Kamareddy"],
    "Medak": ["Sangareddy", "Kamareddy", "Siddipet"],
    "Kamareddy": ["Sangareddy", "Medak", "Siddipet", "Rajanna Sircilla", "Nizamabad"],
    "Rajanna Sircilla": ["Kamareddy", "Nizamabad", "Jagitial", "Karimnagar", "Siddipet"],
    "Karimnagar": ["Rajanna Sircilla", "Jagitial", "Peddapalli", "Hanamkonda", "Siddipet"],
    "Siddipet": ["Medak", "Kamareddy", "Rajanna Sircilla", "Karimnagar", "Hanamkonda", "Jangaon", "Yadadri Bhuvanagiri", "Medchal-Malkajgiri"],
    "Hanamkonda": ["Karimnagar", "Peddapalli", "Jayashankar Bhupalpally", "Warangal", "Jangaon", "Siddipet"],
    "Warangal": ["Hanamkonda", "Jayashankar Bhupalpally", "Mulugu", "Mahabubabad", "Jangaon"],
    "Jangaon": ["Siddipet", "Hanamkonda", "Warangal", "Mahabubabad", "Suryapet", "Yadadri Bhuvanagiri"],
    "Yadadri Bhuvanagiri": ["Siddipet", "Jangaon", "Suryapet", "Nalgonda", "Rangareddy", "Medchal-Malkajgiri"],
    "Mahabubabad": ["Warangal", "Mulugu", "Bhadradri Kothagudem", "Khammam", "Suryapet", "Jangaon"]
}

# 4. Run the solver
solution = backtracking_search(districts, domains, adjacencies)

# 5. Output results
if solution:
    print(f"{'District':<25} | {'Color'}")
    print("-" * 40)
    for district in districts:
        print(f"{district:<25} | {solution[district]}")
else:
    print("No solution found.")