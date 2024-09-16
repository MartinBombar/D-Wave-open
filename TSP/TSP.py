import os
import itertools
import click
import pandas as pd
import dwave
from dwave.system import LeapHybridCQMSampler
from dimod import ConstrainedQuadraticModel, BinaryQuadraticModel, QuadraticModel


def getDistancesFromDataFile(PATH):
    with open(PATH, mode='r') as file:
        # Read the distance matrix from the CSV file
        distance_matrix = []
        for line in file:
            row = list(map(int, line.strip().split(',')))
            distance_matrix.append(row)
    return distance_matrix

def build_tsp_cqm(distances):
    num_cities = len(distances)
    print("\nBuilding a CQM for TSP with {} cities.".format(num_cities))

    # Initialize the CQM
    cqm = ConstrainedQuadraticModel()

    # Binary variables x[i,j] where i is the city and j is the position in the tour
    x = {}
    for i in range(num_cities):
        for j in range(num_cities):
            x[(i, j)] = BinaryQuadraticModel(vartype='BINARY')
            x[(i, j)].add_variable(i * num_cities + j)

    # Objective: Minimize the total distance
    obj = BinaryQuadraticModel(vartype='BINARY')
    for i in range(num_cities):
        for j in range(num_cities):
            for k in range(num_cities):
                if i != k:
                    obj.set_quadratic(i * num_cities + j, k * num_cities + (j + 1) % num_cities, distances[i][k])
    cqm.set_objective(obj)

    # Constraints:
    # 1. Each city must be visited exactly once.
    for i in range(num_cities):
        constraint = QuadraticModel()
        for j in range(num_cities):
            constraint.add_variable('BINARY', i * num_cities + j)
            constraint.set_linear(i * num_cities + j, 1)
        cqm.add_constraint(constraint, sense="==", rhs=1, label=f'visit_once_{i}')

    # 2. Each position in the tour must be filled by exactly one city.
    for j in range(num_cities):
        constraint = QuadraticModel()
        for i in range(num_cities):
            constraint.add_variable('BINARY', i * num_cities + j)
            constraint.set_linear(i * num_cities + j, 1)
        cqm.add_constraint(constraint, sense="==", rhs=1, label=f'one_city_per_pos_{j}')

    return cqm

def main():
    client = dwave.cloud.Client(endpoint='https://my.dwave.system.com/sapi',  token='', permissive_ssl=True)
    PATH = 'data/distances.csv'

    # Initialize solver
    sampler = LeapHybridCQMSampler()

    # Get distance matrix from file
    distances = getDistancesFromDataFile(PATH)
    print("Distance matrix:\n", distances)

    # Build the TSP problem from data and parameters
    cqm = build_tsp_cqm(distances)

    # Submit the problem to the solver
    print("Submitting CQM to solver {}.".format(sampler.solver.name))
    sampleset = sampler.sample_cqm(cqm, label='Example - TSP')
    print(sampleset)


if __name__ == '__main__':
    main()
