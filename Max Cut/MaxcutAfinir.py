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
        adjacency_matrix = []
        for line in file:
            row = list(map(int, line.strip().split(',')))
            adjacency_matrix.append(row)
    return adjacency_matrix

def build_maxcut_qubo(distances):
    num_nodes = len(distances)
    print("\nBuilding a qubo for maxCut with {} nodes.".format(num_nodes))

    # Initialize the CQM
    cqm = ConstrainedQuadraticModel()

    # Binary variables x[i] where i is the number of the node     
    x = {}
    for i in range(num_nodes):
        x[i] = BinaryQuadraticModel(vartype='BINARY')
        x[i].add_variable(i)

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
    adjacency_matrix = getDistancesFromDataFile(PATH)
    print("Adjacency matrix:\n", adjacency_matrix)

    # Build the TSP problem from data and parameters
    qubo = build_maxcut_qubo(adjacency_matrix)

    # Submit the problem to the solver
    print("Submitting CQM to solver {}.".format(sampler.solver.name))
    #
    # sampleset = sampler.sample_cqm(cqm, label='Example - TSP')
    print(sampleset)


if __name__ == '__main__':
    main()
