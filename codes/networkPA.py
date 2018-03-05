'''
Simplified creation of the network for the simulation of PA
'''


import json
import networkx as nx
import numpy as np
import os
import pandas as pd
import re
import random
from codes.network import fix_float64, create_connections, generate_basic
from codes.interventions import get_bmi_cat

def remove_nodes_PA(graph, level_f='../'):
    file = open(level_f+'settings/class.txt', 'r')

    nodes_removed_class = []
    
    list_classes = [int(line) for line in file]
    
    for node in graph.nodes():
        if graph.nodes()[node]['class'] not in list_classes:
            nodes_removed_class.append(node)

    graph.remove_nodes_from(nodes_removed_class)
    

    print('Nodes removed for not being in the selected classes: #', len(nodes_removed_class))
    return graph



def generate_PA(metric='steps', level_f='../'):
    '''
    NetworkClass:       Does the class reach the treshold of >60% of participation
    Steps:              observed mean daily steps count per week    
    Minutes_MVPA: :     observed mean daily minutes of moderate to vigorous physical activity per week      
    Steps_imp1:         simple imputation for missing Steps data    
    MVPA_imp1:          simple imputation for missing Minutes_MVPA data 
    Steps_ML_imp1:      single multilevel imputation for Steps data 
    Minutes_MVPA_ML_imp1:   single multilevel imputation for Minutes_MVPA data

    |- inputs:
        |-- metric: steps or mvpa
    |- outputs:
        |-- dictionary with steps or minutes

    '''
    fitbit = pd.read_csv(level_f+'data/fitbit.csv', sep=';', header=0)
    
    steps_mean_wave = fitbit.groupby(['Child_Bosse', 'Wave']).mean()['Steps_ML_imp1'].reset_index()
    steps_mean_wave.Steps_ML_imp1 = steps_mean_wave.Steps_ML_imp1 * 0.000153
    steps_mean_wave = steps_mean_wave.pivot(index='Child_Bosse', columns='Wave')['Steps_ML_imp1']

    return dict(steps_mean_wave[1])

    '''
    # Mean of minutes from moderate to vigorous activity and steps (all imputed)
    minutes_MVPA_df = fitbit.groupby(['Child_Bosse']).mean()['Minutes_MVPA_ML_imp1']

    # Steps are converted to fit the system. 1.53 (PA) corresponds to 10.000 steps.
    steps_df = fitbit.groupby(['Child_Bosse']).mean()['Steps_ML_imp1'] * 0.000153

    if metric == 'mvpa':
        minutes_MVPA_df.to_csv(level_f+'results/mvpa.csv')
        return dict(minutes_MVPA_df)
    elif metric == 'steps':
        steps_df.to_csv(level_f+'results/steps.csv')
        return dict(steps_df)
    else:
        print('Metric not valid! >>>', metric)
        return False

    '''


def generate_environment(level_f='../'):
    '''
    The environment variable is going to be generated randomly by now, but should be replaced later
    
    * Computer: [0, 1, 2, 3]
    * Car:      [0, 1, 2]
    * Vacation: [0, 1, 2, 3]
    * Own room: [0, 1]
    '''
    env = pd.read_csv(level_f+'data/environment.csv', sep=';', header=0)
    env = env[['Child_Bosse', 'School', 'Class', 'Wave', 'GEN_FAS_computer_R',
               'GEN_FAS_car_R', 'GEN_FAS_vacation_R', 'GEN_FAS_ownroom_R']]
    
    classes=[67, 71, 72, 74, 77, 78, 79, 81, 83, 86, 100, 101, 103, 121, 
             122, 125, 126, 127, 129, 130, 131, 133, 135, 136, 138, 139]
    
    env = env[env['Class'].isin(classes)]

    env_filter = env[env.Wave==1][['Child_Bosse', 'GEN_FAS_computer_R', 'GEN_FAS_car_R', 
                                   'GEN_FAS_vacation_R', 'GEN_FAS_ownroom_R']].copy()
    
    env_filter['FAS_Score_R'] = env_filter['GEN_FAS_computer_R'] + env_filter['GEN_FAS_vacation_R'] + \
                            env_filter['GEN_FAS_car_R']*1.5 + env_filter['GEN_FAS_ownroom_R']*3

    # To keep the values between 0 and 2.
    env_filter.FAS_Score_R = env_filter.FAS_Score_R/6
    env_filter.index = env_filter['Child_Bosse']

    env_dict = dict(env_filter['FAS_Score_R'])
    for key, value in env_dict.items():
        if np.isnan(value):
            env_dict[key] = env_filter.FAS_Score_R.mean()

    return env_dict


def generate_bmi(level_f='../'):
    '''
    Created in Mar 5
    Generate the BMI that is going to be used to classify the children 
    in an obesity scale.
    '''
    bmi = pd.read_csv(level_f+'data/bmi.csv', sep=';', header=0)
    bmi = bmi[bmi.Wave==2][['Child_Bosse', 'BMI']]
    bmi.index = bmi.Child_Bosse
    bmi = bmi['BMI']

    return dict(bmi)

def create_agents_PA(graph, level_f='../'):
    '''
    Each agent need the following information:
        |-- gender
        |-- age
        |-- class
        |-- height
        |-- weight
        |-- EI
        |-- EE
        |-- Env
        |-- PA
    '''
    
    PA_dict = generate_PA(metric='steps', level_f=level_f)
    gender_dict, age_dict, class_dict = generate_basic(level_f=level_f)
    environment_dict = generate_environment(level_f=level_f)
    bmi_dict = generate_bmi(level_f=level_f)
    
    PA_dict = fix_float64(PA_dict)
    print('PA')
    gender_dict = fix_float64(gender_dict)
    print('gender')
    age_dict = fix_float64(age_dict)
    print('age')
    class_dict = fix_float64(class_dict)
    print('class')
    environment_dict = fix_float64(environment_dict)
    print('env')
    bmi_dict = fix_float64(bmi_dict)
    print('obesity classifier')
    
    nx.set_node_attributes(graph, values=PA_dict, name='PA')
    nx.set_node_attributes(graph, values=gender_dict, name='gender')
    nx.set_node_attributes(graph, values=age_dict, name='age')
    nx.set_node_attributes(graph, values=class_dict, name='class')
    nx.set_node_attributes(graph, values=environment_dict, name='env')
    nx.set_node_attributes(graph, values=bmi_dict, name='bmi')
    
    # Adding category for the nodes
    obesity_class = {}
    for node in graph.nodes():
        obesity_class[node] = get_bmi_cat(gender_dict[node], age_dict[node], bmi_dict[node])

    nx.set_node_attributes(graph, values=obesity_class, name='bmi_cat')

    return graph



def generate_network_PA(level_f='../', label=None, formula_s=None):
    '''
    label and formula_s are variables for the create_connections(). 
    They are basically the file to read (label) or the string formula to customize the calculation of the edges.

    background = pd.read_csv(data_f+'background.csv', sep=';', header=0)
    bmi = pd.read_csv(data_f+'bmi.csv', sep=';', header=0)
    fitbit = pd.read_csv(data_f+'fitbit.csv', sep=';', header=0)
    nominations = pd.read_csv(data_f+'nominations.csv', sep=';', header=0)
    nominations.columns = ['class', 'child', 'wave', 'variable', 'class_nominated', 'nominated', 'same_class']
    pp = pd.read_csv(data_f+'pp.csv', sep=';', header=0)
    pp['sum_waves'] = pp.parti_W1+pp.parti_W2+pp.parti_W3+pp.parti_W4
    '''
    print('###############################################################')
    print('Graph generation starting!')
    print('Label: {}\nFormula: {}'.format(label, formula_s))
    print('###############################################################\n')
    graph = nx.DiGraph()

    print('Create connections...')
    create_connections(graph=graph, level_f=level_f, label=label, formula_s=formula_s, waves='all')

    print('Nodes after connections: #', len(graph.nodes()))
    print('Edges created #: ', len(graph.edges()))

    print('\nCreate agents...')
    create_agents_PA(graph=graph, level_f=level_f)

    # Comment this if you want to keep all the nodes
    print('Removing nodes not in the specified classes...')
    remove_nodes_PA(graph=graph, level_f=level_f)

    print('Nodes remaining after removal: #', len(graph.nodes()))
    print('Edges remaining after removal #: ', len(graph.edges()))
    if label is None:
        g_file = 'results/graph.gexf'
    else:
        g_file = 'results/graph_' + label + '.gexf'
    try:
        nx.write_gexf(graph, level_f+ g_file)
    except IOError as e:
        errno, strerror = e.args
        print("I/O error({0}): {1}".format(errno,strerror))
        # e can be printed directly without using .args:
        # print(e)
    
    print('###############################################################')
    print('Graph generated successfuly!')
    print('###############################################################\n')
    return graph
