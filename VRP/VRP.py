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

def build_vrp_cqm(distances, num_vehicles, depot=0):
    num_cities = len(distances)
    print("\nBuilding a CQM for VRP with {} cities and {} vehicles.".format(num_cities, num_vehicles))

    # Initialize the CQM
    cqm = ConstrainedQuadraticModel()

    # Binary variables x[i,j,k] where i is the city, j is the position in the tour, and k is the vehicle
    x = {}
    for i in range(num_cities):
        for j in range(num_cities):
            for k in range(num_vehicles):
                x[(i, j, k)] = BinaryQuadraticModel(vartype='BINARY')
                x[(i, j, k)].add_variable(i * num_cities * num_vehicles + j * num_vehicles + k)

    # Objective: Minimize the total distance
    obj = BinaryQuadraticModel(vartype='BINARY')
    for i in range(num_cities):
        for j in range(num_cities):
            for k in range(num_vehicles):
                for l in range(num_cities):
                    if i != l:
                        obj.set_quadratic(i * num_cities * num_vehicles + j * num_vehicles + k,
                                          l * num_cities * num_vehicles + (j + 1) % num_cities * num_vehicles + k,
                                          distances[i][l])
    cqm.set_objective(obj)

    # Constraints:
    # 1. Each city must be visited exactly once (excluding the depot).
    for i in range(1, num_cities):
        constraint = QuadraticModel()
        for j in range(num_cities):
            for k in range(num_vehicles):
                constraint.add_variable('BINARY', i * num_cities * num_vehicles + j * num_vehicles + k)
                constraint.set_linear(i * num_cities * num_vehicles + j * num_vehicles + k, 1)
        cqm.add_constraint(constraint, sense="==", rhs=1, label=f'visit_once_{i}')

    # 2. Each position in the tour must be filled by exactly one city per vehicle.
    for j in range(num_cities):
        for k in range(num_vehicles):
            constraint = QuadraticModel()
            for i in range(num_cities):
                constraint.add_variable('BINARY', i * num_cities * num_vehicles + j * num_vehicles + k)
                constraint.set_linear(i * num_cities * num_vehicles + j * num_vehicles + k, 1)
            cqm.add_constraint(constraint, sense="==", rhs=1, label=f'one_city_per_pos_{j}_vehicle_{k}')

    # 3. Each vehicle must start and end at the depot.
    for k in range(num_vehicles):
        start_constraint = QuadraticModel()
        end_constraint = QuadraticModel()
        for j in range(num_cities):
            start_constraint.add_variable('BINARY', depot * num_cities * num_vehicles + j * num_vehicles + k)
            start_constraint.set_linear(depot * num_cities * num_vehicles + j * num_vehicles + k, 1)
            end_constraint.add_variable('BINARY', depot * num_cities * num_vehicles + (j + num_cities - 1) % num_cities * num_vehicles + k)
            end_constraint.set_linear(depot * num_cities * num_vehicles + (j + num_cities - 1) % num_cities * num_vehicles + k, 1)
        cqm.add_constraint(start_constraint, sense="==", rhs=1, label=f'start_at_depot_vehicle_{k}')
        cqm.add_constraint(end_constraint, sense="==", rhs=1, label=f'end_at_depot_vehicle_{k}')

    return cqm

def main():
    client = dwave.cloud.Client(endpoint='https://my.dwave.system.com/sapi', token='', permissive_ssl=True)
    PATH = 'data/distances.csv'
    num_vehicles = 3  # Number of vehicles available
    depot = 0  # Assume the depot is at city 0

    # Initialize solver
    sampler = LeapHybridCQMSampler()

    # Get distance matrix from file
    distances = getDistancesFromDataFile(PATH)
    print("Distance matrix:\n", distances)

    # Build the VRP problem from data and parameters
    cqm = build_vrp_cqm(distances, num_vehicles, depot)

    # Submit the problem to the solver
    print("Submitting CQM to solver {}.".format(sampler.solver.name))
    sampleset = sampler.sample_cqm(cqm, label='Example - VRP')
    print(sampleset)


if __name__ == '__main__':
    main()
