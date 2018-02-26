

from codes.networkPA import generate_network_PA
from codes.simulatePA import diffuse_behavior_PA

import networkx as nx
import numpy as np
import pandas as pd
from pprint import pprint
from random import random
from time import time

def acceptance_probability(old_cost, new_cost, T):
    '''
    Function to define acceptance probability values for SA
    '''
    delta = new_cost-old_cost
    probability = np.exp(-delta/T)
    return probability


def get_neighbor(parameters):
    '''
    Parameters are:
        thres_PA = 0.2
        I_PA = 0.00075

    A list with two positions:
        [thres, I_PA]
    '''
    old_thres = parameters[0]
    old_I_PA = parameters[1]

    minn = 0.00001
    
    max_I_PA = 0.5
    inf_I_PA = -0.05
    sup_I_PA = 0.05
    
    maxn_thres = 0.9999
    inf_thres = -0.1
    sup_thres = 0.1
    
    new_thres = old_thres + ((sup_thres - inf_thres) * random() + inf_thres)
    new_thres = minn if new_thres < minn else maxn_thres if new_thres > maxn_thres else new_thres
    

    new_I_PA = old_I_PA + ((sup_I_PA - inf_I_PA) * random() + inf_I_PA)
    new_I_PA = minn if new_I_PA < minn else max_I_PA if new_I_PA > max_I_PA else new_I_PA
    
    return [new_thres, new_I_PA]


def get_empirical(metric='steps', level_f='../'):
    '''
    Get the data for the 4 waves.
    This is based only on steps so far
    '''
    fitbit = pd.read_csv(level_f+'data/fitbit.csv', sep=';', header=0)
    
    steps_mean_wave = fitbit.groupby(['Child_Bosse', 'Wave']).mean()['Steps_ML_imp1'].reset_index()
    steps_mean_wave.Steps_ML_imp1 = steps_mean_wave.Steps_ML_imp1 * 0.000153
    steps_mean_wave = steps_mean_wave.pivot(index='Child_Bosse', columns='Wave')['Steps_ML_imp1']

    return steps_mean_wave


def get_error(graph, empirical, parameters=None, label='all', level_f='../'):
    '''
    Runs the simulation and calculates the difference
    '''

    if parameters is None:
        thres_PA = random()
        I_PA = random()
    else:
        thres_PA = parameters[0]
        I_PA = parameters[1]
    
    #graph = generate_network_PA(level_f=level_f, label=label)
    #print('PA hist <before>: ', nx.get_node_attributes(graph, 'PA_hist'))
    
    init_time = time()
    diffuse_behavior_PA(graph, years=1, thres_PA=thres_PA, I_PA=I_PA)
    end_time = time()
    print('Diffuse behavior time: ', (end_time-init_time))
    #print(parameters, '\n')

    #print('PA hist <after>: ', nx.get_node_attributes(graph, 'PA_hist'))
    PA_results = {}
    for node in graph.nodes():
        PA_results[node] = graph.nodes[node]['PA_hist']

    PA_df = pd.DataFrame(PA_results).T

    PA_sim = PA_df[[0, 30, 60, 364]]
    PA_sim.columns = ['W1', 'W2', 'W3', 'W4']
    empirical.columns = ['W1', 'W2', 'W3', 'W4']
    
    # Divided by 100 to increase the chance of acceptance of worst scenarios
    return ((PA_sim - empirical)**2).sum().sum()/100, parameters


def parameter_tuning(parameters=None, label='all', level_f='../'):
    '''
    Parameter tuning function
    '''

    # Keeping history (vectors)
    cost_hist = list([])
    parameters_hist = list([])

    empirical_data = get_empirical(level_f=level_f)
    original_graph = generate_network_PA(level_f=level_f, label=label)
    
    # Actual cost
    old_cost, initial_parameters = get_error(graph=original_graph.copy(), empirical=empirical_data, parameters=parameters, label=label, level_f=level_f)

    cost_hist.append(old_cost)
    parameters_hist.append(initial_parameters)

    T = 1.0
    T_min = 0.01
    # original = 0.9
    alpha = 0.9
    num_neighbors = 20
    
    parameters = initial_parameters

    while T > T_min:
        print('\nTemp: ', T)
        i = 1
        # original = 100
        while i <= num_neighbors:
            #init_time = time()
            new_parameters = get_neighbor(parameters)
            new_cost, new_parameters = get_error(graph=original_graph.copy(), empirical=empirical_data, parameters=new_parameters, label=label, level_f=level_f)
            #end_time = time()
            #print(T, i, (end_time-init_time))

            if new_cost < old_cost:
                parameters = new_parameters
                parameters_hist.append(parameters)
                old_cost = new_cost
                cost_hist.append(old_cost)
            else:
                ap = acceptance_probability(old_cost, new_cost, T)
                if ap > random():
                    #print 'accepted!'
                    parameters = new_parameters
                    parameters_hist.append(parameters)
                    old_cost = new_cost
                    cost_hist.append(old_cost)
            i += 1
        pprint(parameters_hist[-1])
        print(cost_hist[-1])
        T = T*alpha

    # plot_results(parameters, cost_hist, parameters_hist)

    return parameters, cost_hist, parameters_hist

if __name__ == "__main__":
    parameter_tuning()