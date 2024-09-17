import os
import pandas as pd
from dwave.system import LeapHybridCQMSampler
from dimod import ConstrainedQuadraticModel, Binary

def getDistancesFromDataFile(PATH):
    # Read the distance matrix from the CSV file
    try:
        distance_matrix = pd.read_csv(PATH, header=None).values.tolist()
        return distance_matrix
    except Exception as e:
        raise ValueError(f"Error reading distance file: {e}")

def build_tsp_cqm(distances):
    num_cities = len(distances)
    print(f"\nBuilding a CQM for TSP with {num_cities} cities.")

    # Initialize the CQM
    cqm = ConstrainedQuadraticModel()

    # Binary variables x[i, j] where i is the city and j is the position in the tour
    x = {(i, j): Binary(f'x_{i}_{j}') for i in range(num_cities) for j in range(num_cities)}

    # Objective: Minimize the total distance
    obj = 0
    for i in range(num_cities):
        for j in range(num_cities):
            for k in range(num_cities):
                if i != k:
                    obj += distances[i][k] * x[i, j] * x[k, (j + 1) % num_cities]
    cqm.set_objective(obj)

    # Constraints:
    # 1. Each city must be visited exactly once.
    for i in range(num_cities):
        cqm.add_constraint(sum(x[i, j] for j in range(num_cities)) == 1, label=f'visit_once_{i}')

    # 2. Each position in the tour must be filled by exactly one city.
    for j in range(num_cities):
        cqm.add_constraint(sum(x[i, j] for i in range(num_cities)) == 1, label=f'one_city_per_pos_{j}')

    return cqm

def main():
    PATH = 'D-Wave-open/TSP/data/distances.csv'  # Use the appropriate relative or absolute path

    # Initialize solver
    sampler = LeapHybridCQMSampler()

    # Get distance matrix from file
    distances = getDistancesFromDataFile(PATH)
    print("Distance matrix:\n", distances)

    # Build the TSP problem from data and parameters
    cqm = build_tsp_cqm(distances)

    # Submit the problem to the solver
    print("Submitting CQM to solver.")
    sampleset = sampler.sample_cqm(cqm, label='Example - TSP')

    # Display results
    best_sample = sampleset.first.sample
    print(f"Best sample: {best_sample}")
    print(f"Energy: {sampleset.first.energy}")
    print(f"Feasible: {sampleset.first.is_feasible}")

    # Check feasibility of solution
    if not sampleset.first.is_feasible:
        print("Infeasible solution found. Constraints are violated.")
    else:
        print("Feasible solution found.")
        # Optionally: Extract and display the tour
        tour = []
        for j in range(len(distances)):
            for i in range(len(distances)):
                if best_sample[f'x_{i}_{j}'] == 1:
                    tour.append(i)
                    break
        print(f"The tour is: {tour}")

if __name__ == '__main__':
    main()


