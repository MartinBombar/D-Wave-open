#File to solve knappsack problem, inspired from Dwave example but implemented my own way

import os
import itertools
import click
import pandas as pd
import dwave
from dwave.system import LeapHybridCQMSampler
from dimod import ConstrainedQuadraticModel, BinaryQuadraticModel, QuadraticModel


def getValuesFromDataFile(PATH):

    with open(PATH, mode='r') as file:
        # Skip the header line
        next(file)
        
        costs=[]
        weights=[]
        # Read each line, split it by comma, and store the values in respective lists
        for line in file:
            # Strip any whitespace or newlines and split by comma
            cost, weight = line.strip().split(',')
            
            # Append the values to the lists (convert them to integers)
            costs.append(int(cost))
            weights.append(int(weight))
    return costs, weights

def build_knapsack_cqm(costs, weights, max_weight):
    #Building the Constrained Quadratic Model (CQM)
    num_items = len(costs)
    print("\nBuilding a CQM for {} items.".format(str(num_items)))

    cqm = ConstrainedQuadraticModel()
    obj = BinaryQuadraticModel(vartype='BINARY')
    constraint = QuadraticModel()

    for i in range(num_items):
        # Objective is to maximize the total costs
        obj.add_variable(i)
        obj.set_linear(i, -costs[i])
        # Constraint is to keep the sum of items' weights under or equal capacity
        constraint.add_variable('BINARY', i)
        constraint.set_linear(i, weights[i])

    cqm.set_objective(obj)
    cqm.add_constraint(constraint, sense="<=", rhs=max_weight, label='capacity')

    return cqm

def main():
    client = dwave.cloud.Client(endpoint='https://my.dwave.system.com/sapi',  token='', permissive_ssl=True)
    knapsackSize=10
    PATH='data/data.csv'

    #initialize solver
    sampler = LeapHybridCQMSampler()

    #Get Values from file
    costs, weights=getValuesFromDataFile(PATH)
    print("cost : \n",costs,"\n","weight : \n",weights)

    #build problem from data and parameters
    cqm=build_knapsack_cqm(costs,weights,knapsackSize)

    #submit the problem to the solver
    print("Submitting CQM to solver {}.".format(sampler.solver.name))
    sampleset = sampler.sample_cqm(cqm, label='Example - Knapsack- modified')
    print(sampleset)


if __name__ == '__main__':
    main()