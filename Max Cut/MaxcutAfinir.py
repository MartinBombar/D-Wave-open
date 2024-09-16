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

def build_maxcut_qubo(adjacency):

    #Building the Quadratic Unconstrained Binary Model 
    num_items = len(adjacency)
    print("\nBuilding a QUBO for {} nodes.".format(str(num_items)))

    cqm = ConstrainedQuadraticModel()
    obj = BinaryQuadraticModel(vartype='BINARY')
    constraint = QuadraticModel()

    for i in range(num_items):
        # Objective is to maximize the total costs
        obj.add_variable(i)

    for i in range(num_items):
        for j in range(i+1,num_items):
            obj.add_interaction(i, j, -2)  # Add the interaction term -2x_ix_j
            obj.set_linear(i, obj.get_linear(i) + 1)  # Add x_i term
            obj.set_linear(j, obj.get_linear(j) + 1)  # Add x_j term

    # Add the objective to the CQM
    cqm.set_objective(obj)
    return cqm

def main():
    PATH = 'data/adjacency.csv'

    # Initialize solver
    sampler = LeapHybridCQMSampler()

    # Get distance matrix from file
    adjacency_matrix = getDistancesFromDataFile(PATH)
    print("Adjacency matrix:\n", adjacency_matrix)

    # Build the TSP problem from data and parameters
    qubo = build_maxcut_qubo(adjacency_matrix)

    # Submit the problem to the solver
    print("Submitting CQM to solver {}.".format(sampler.solver.name))
    
    sampleset = sampler.sample_cqm(cqm, label='Example - TSP')
    
    print(sampleset)


if __name__ == '__main__':
    main()
