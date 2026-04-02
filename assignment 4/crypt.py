def solve_crypt():
    letters = ['S', 'E', 'N', 'D', 'M', 'O', 'R', 'Y']
    # Each letter can be any digit from 0 to 9
    domains = {l: list(range(10)) for l in letters}
    
    def solve(assigned):
        # Base Case: If all letters are assigned, verify the math
        if len(assigned) == len(letters):
            s, e, n, d = assigned['S'], assigned['E'], assigned['N'], assigned['D']
            m, o, r, y = assigned['M'], assigned['O'], assigned['R'], assigned['Y']
            
            # Constraint: Leading digits (S and M) cannot be 0
            if s == 0 or m == 0: 
                return None
            
            # Convert assigned digits into integers
            send = s*1000 + e*100 + n*10 + d
            more = m*1000 + o*100 + r*10 + e
            money = m*10000 + o*1000 + n*100 + e*10 + y
            
            # Check the arithmetic equation
            if send + more == money:
                return assigned, send, more, money
            return None

        # Recursive Step: Pick the next unassigned variable
        unassigned_vars = [l for l in letters if l not in assigned]
        var = unassigned_vars[0]
        
        for val in domains[var]:
            # Constraint: AllDifferent (no two letters share a digit)
            if val not in assigned.values():
                assigned[var] = val
                
                res = solve(assigned)
                if res: 
                    return res
                
                # Backtrack: Remove the assignment if it didn't lead to a solution
                del assigned[var]
        return None

    # Start the recursive search with an empty dictionary
    result = solve({})
    
    if result:
        assignment, send, more, money = result
        print("Crypt-Arithmetic Solution Found:")
        print(f"Mapping: {assignment}")
        print("-" * 15)
        print(f"  {send} (SEND)")
        print(f"+ {more} (MORE)")
        print("-" * 15)
        print(f" {money} (MONEY)")
    else:
        print("No solution found.")

# Execute the function
if __name__ == "__main__":
    solve_crypt()