import dimod
from dwave.system import EmbeddingComposite, DWaveSampler

def parse_adjacency_matrix(filename): 
    with open(filename, 'r') as file:
        # Read the first line 
        first_line = file.readline().strip().split()
        n = int(first_line[0])  # number of nodes
        
        # Initialize an n x n adjacency matrix with 0 (or float('inf') for no edge)
        adjacency_matrix = [[0 for _ in range(n)] for _ in range(n)]
        
        # Read the remaining lines which contain the arcs information
        for line in file:
            u, v, weight = line.strip().split()
            u = int(u) - 1  # convert to 0-based index
            v = int(v) - 1  
            weight = float(weight)  
            
            # Update the adjacency matrix 
            adjacency_matrix[u][v] = weight
            
    return adjacency_matrix



def max_cut_qubo(adjacency_matrix): 
    num_nodes = len(adjacency_matrix)
    Q = {}

    for i in range(num_nodes):
        for j in range(i+1, num_nodes):
            if adjacency_matrix[i][j] != 0:  # Check if there is an edge
                weight = adjacency_matrix[i][j]
                Q[(i, i)] = Q.get((i, i), 0) - weight
                Q[(j, j)] = Q.get((j, j), 0) - weight
                Q[(i, j)] = Q.get((i, j), 0) + 2 * weight  # Account for the weight in the QUBO matrix
    
    return Q


def display_solution(solution, cut_value):
    
    # Extract node assignments into a list for better readability
    partition_0 = [node for node, val in solution.items() if val == 0]
    partition_1 = [node for node, val in solution.items() if val == 1]
    
    # Display the solution in a user-friendly way
    print("\nMax-Cut Problem Solution:")
    print(f"Partition 0 (Set A): {partition_0}")
    print(f"Partition 1 (Set B): {partition_1}")
    print(f"\nMax-Cut value: {cut_value}\n")


if __name__ == "__main__":
    # File containing the adjacency matrix
    #filename = 'D-Wave-open/Max_Cut/data/easy.csv'
    filename = 'D-Wave-open/Max_Cut/data/Bipart.csv'
    #filename = 'culberson/culberson1.csv'
    print("pass1")

    # Parse the adjacency matrix from the file
    adjacency_matrix = parse_adjacency_matrix(filename)
    print("pass2")

    # Generate the QUBO for the Max-Cut problem
    Q = max_cut_qubo(adjacency_matrix)
    print("pass3")

    # Solve the problem using D-Wave sampler (or replace with a classical sampler)
    sampler = EmbeddingComposite(DWaveSampler())
    print("pass4")
    
    # Solve the Max-Cut problem with multiple reads
    response = sampler.sample_qubo(Q, num_reads=100,label='Max cut')
    print("pass5")
    
    # Get the best solution and Max-Cut value
    best_solution = response.first.sample
    best_cut_value = -response.first.energy  # Negate energy to get the Max-Cut value
    print("pass6")

    display_solution(best_solution, best_cut_value)
    print("pass7")
