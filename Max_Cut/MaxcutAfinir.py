import dimod
from dwave.system import EmbeddingComposite, DWaveSampler

def parse_adjacency_matrix(filename):
    """
    Parse a text file containing an adjacency matrix.
    
    :param filename: The path to the file containing the adjacency matrix.
    :return: A list of lists (2D array) representing the adjacency matrix.
    """
    adjacency_matrix = []
    
    with open(filename, 'r') as file:
        for line in file:
            # Split each line by commas and convert each element to an integer
            row = list(map(int, line.strip().split(',')))
            adjacency_matrix.append(row)
    
    return adjacency_matrix

def max_cut_qubo(adjacency_matrix):
    """
    Create a QUBO dictionary for the Max-Cut problem from an adjacency matrix.
    
    :param adjacency_matrix: A list of lists representing the adjacency matrix.
    :return: A QUBO dictionary.
    """
    num_nodes = len(adjacency_matrix)
    Q = {}

    for i in range(num_nodes):
        for j in range(i+1, num_nodes):
            if adjacency_matrix[i][j] == 1:
                Q[(i, i)] = Q.get((i, i), 0) - 1
                Q[(j, j)] = Q.get((j, j), 0) - 1
                Q[(i, j)] = Q.get((i, j), 0) + 2
    
    return Q

def display_solution(solution, cut_value):
    """
    Nicely formats and displays the Max-Cut solution and value.
    
    :param solution: The solution dictionary from the sampler.
    :param cut_value: The energy (Max-Cut value) from the sampler.
    """
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
    filename = 'D-Wave-open/Max_Cutduplicate/data/adjacency.csv'
    
    # Parse the adjacency matrix from the file
    adjacency_matrix = parse_adjacency_matrix(filename)
    
    # Generate the QUBO for the Max-Cut problem
    Q = max_cut_qubo(adjacency_matrix)

    # Solve the problem using D-Wave sampler (or replace with a classical sampler)
    sampler = EmbeddingComposite(DWaveSampler())
    
    # Solve the Max-Cut problem with multiple reads
    response = sampler.sample_qubo(Q, num_reads=100)
    
    # Get the best solution and Max-Cut value
    best_solution = response.first.sample
    best_cut_value = -response.first.energy  # Negate energy to get the Max-Cut value

    # Nicely display the solution
    display_solution(best_solution, best_cut_value)
