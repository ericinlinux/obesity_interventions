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


def get_bmi_cat(gender,age,bmi):
    '''
    Calculating the BMI category based on gender, age and BMI value
    '''

    if (bmi == -1) or (gender == -1) or (age == -1) :
        return np.nan

    category=0
    #males
    if gender==0:
        if age==2:
            if bmi<=13.36:
                category=1
            elif 13.37<=bmi<=15.13:
                category=2
            elif 15.14<=bmi<=18.40:
                category=3
            elif 18.41<=bmi<=20.09:
                category=4
            elif bmi>20.09:
                category=5
        elif age==3:
            if bmi<=13.09:
                category=1
            elif 13.10<=bmi<=14.73:
                category=2
            elif 14.74<=bmi<=17.88:
                category=3
            elif 17.89<=bmi<=19.57:
                category=4
            elif bmi>19.57:
                category=5
        elif age==4:
            if bmi<=12.86:
                category=1
            elif 12.87<=bmi<=14.42:
                category=2
            elif 14.43<=bmi<=17.54:
                category=3
            elif 17.55<=bmi<=19.29:
                category=4
            elif bmi>19.29:
                category=5
        elif age==5:
            if bmi<=12.66:
                category=1
            elif 12.67<=bmi<=14.20:
                category=2
            elif 14.21<=bmi<=17.41:
                category=3
            elif 17.42<=bmi<=19.30:
                category=4
            elif bmi>19.30:
                category=5
        elif age==6:
            if bmi<=12.50:
                category=1
            elif 12.51<=bmi<=14.06:
                category=2
            elif 14.07<=bmi<=17.54:
                category=3
            elif 17.55<=bmi<=19.78:
                category=4
            elif bmi>19.78:
                category=5
        elif age==7:
            if bmi<=12.42:
                category=1
            elif 12.43<=bmi<=14.03:
                category=2
            elif 14.04<=bmi<=17.91:
                category=3
            elif 17.92<=bmi<=20.63:
                category=4
            elif bmi>20.63:
                category=5
        elif age==8:
            if bmi<=12.42:
                category=1
            elif 12.43<=bmi<=14.14:
                category=2
            elif 14.15<=bmi<=18.43:
                category=3
            elif 18.44<=bmi<=21.60:
                category=4
            elif bmi>21.60:
                category=5
        elif age==9:
            if bmi<=12.50:
                category=1
            elif 12.51<=bmi<=14.34:
                category=2
            elif 14.35<=bmi<=19.09:
                category=3
            elif 19.10<=bmi<=22.77:
                category=4
            elif bmi>22.77:
                category=5
        elif age==10:
            if bmi<=12.66:
                category=1
            elif 12.67<=bmi<=14.63:
                category=2
            elif 14.64<=bmi<=19.83:
                category=3
            elif 19.84<=bmi<=24.00:
                category=4
            elif bmi>24.00:
                category=5
        elif age==11:
            if bmi<=12.89:
                category=1
            elif 12.90<=bmi<=14.96:
                category=2
            elif 14.97<=bmi<=20.54:
                category=3
            elif 20.55<=bmi<=25.10:
                category=4
            elif bmi>25.10:
                category=5
        elif age==12:
            if bmi<=13.18:
                category=1
            elif 13.19<=bmi<=15.34:
                category=2
            elif 15.35<=bmi<=21.21:
                category=3
            elif 21.22<=bmi<=26.02:
                category=4
            elif bmi>26.02:
                category=5
        elif age==13:
            if bmi<=13.59:
                category=1
            elif 13.60<=bmi<=15.83:
                category=2
            elif 15.84<=bmi<=21.90:
                category=3
            elif 21.91<=bmi<=26.84:
                category=4
            elif bmi>26.84:
                category=5
        elif age==14:
            if bmi<=14.09:
                category=1
            elif 14.10<=bmi<=16.40:
                category=2
            elif 16.41<=bmi<=22.61:
                category=3
            elif 22.62<=bmi<=27.63:
                category=4
            elif bmi>27.63:
                category=5
        elif age==15:
            if bmi<=14.60:
                category=1
            elif 14.61<bmi<16.97:
                category=2
            elif 16.98<=bmi<=23.28:
                category=3
            elif 23.29<=bmi<=28.30:
                category=4
            elif bmi>28.30:
                category=5
        elif age==16:
            if bmi<=15.12:
                category=1
            elif 15.13<=bmi<=17.53:
                category=2
            elif 17.54<=bmi<=23.89:
                category=3
            elif 23.90<=bmi<=28.88:
                category=4
            elif bmi>28.88:
                category=5
        elif age==17:
            if bmi<=15.60:
                category=1
            elif 15.61<=bmi<=18.04:
                category=2
            elif 18.05<=bmi<=24.45:
                category=3
            elif 24.46<=bmi<=29.41:
                category=4
            elif bmi>29.41:
                category=5
        elif age==18:
            if bmi<=16.00:
                category=1
            elif 16.01<=bmi<=18.49:
                category=2
            elif 18.50<=bmi<=24.99:
                category=3
            elif 25.00<=bmi<=30.00:
                category=4
            elif bmi>30.00:
                category=5
                    #males
    if gender==1:
        if age==2:
            if bmi<=13.24:
                category=1
            elif 13.25<bmi<14.82:
                category=2
            elif 14.83<=bmi<=18.01:
                category=3
            elif 18.02<=bmi<=19.81:
                category=4
            elif bmi>19.81:
                category=5
        elif age==3:
            if bmi<=12.98:
                category=1
            elif 12.99<=bmi<=14.46:
                category=2
            elif 14.47<=bmi<=17.55:
                category=3
            elif 17.56<=bmi<=19.36:
                category=4
            elif bmi>19.36:
                category=5
        elif age==4:
            if bmi<=12.73:
                category=1
            elif 12.74<=bmi<=14.18:
                category=2
            elif 14.19<=bmi<=17.27:
                category=3
            elif 17.28<=bmi<=19.15:
                category=4
            elif bmi>19.15:
                category=5
        elif age==5:
            if bmi<=12.50:
                category=1
            elif 12.51<=bmi<=13.93:
                category=2
            elif 13.94<=bmi<=17.14:
                category=3
            elif 17.15<=bmi<=19.17:
                category=4
            elif bmi>19.17:
                category=5
        elif age==6:
            if bmi<=12.32:
                category=1
            elif 12.33<=bmi<=13.81:
                category=2
            elif 13.82<=bmi<=17.33:
                category=3
            elif 17.34<=bmi<=19.65:
                category=4
            elif bmi>19.65:
                category=5
        elif age==7:
            if bmi<=12.26:
                category=1
            elif 12.27<=bmi<=13.85:
                category=2
            elif 13.86<=bmi<=17.74:
                category=3
            elif 17.75<=bmi<=20.51:
                category=4
            elif bmi>20.51:
                category=5
        elif age==8:
            if bmi<=12.31:
                category=1
            elif 12.32<=bmi<=14.01:
                category=2
            elif 14.02<=bmi<=18.34:
                category=3
            elif 18.35<=bmi<=21.57:
                category=4
            elif bmi>21.57:
                category=5
        elif age==9:
            if bmi<=12.44:
                category=1
            elif 12.45<=bmi<=14.27:
                category=2
            elif 14.28<=bmi<=19.06:
                category=3
            elif 19.07<=bmi<=22.81:
                category=4
            elif bmi>22.81:
                category=5
        elif age==10:
            if bmi<=12.64:
                category=1
            elif 12.65<=bmi<=14.60:
                category=2
            elif 14.61<=bmi<=19.85:
                category=3
            elif 19.86<=bmi<=24.11:
                category=4
            elif bmi>24.11:
                category=5
        elif age==11:
            if bmi<=12.95:
                category=1
            elif 12.96<=bmi<=15.04:
                category=2
            elif 15.05<=bmi<=20.73:
                category=3
            elif 20.74<=bmi<=25.42:
                category=4
            elif bmi>25.42:
                category=5
        elif age==12:
            if bmi<=13.39:
                category=1
            elif 13.40<=bmi<=15.61:
                category=2
            elif 15.62<=bmi<=21.67:
                category=3
            elif 21.68<=bmi<=26.67:
                category=4
            elif bmi>26.67:
                category=5
        elif age==13:
            if bmi<=13.92:
                category=1
            elif 13.93<bmi<16.25:
                category=2
            elif 16.26<=bmi<=22.57:
                category=3
            elif 22.58<=bmi<=27.76:
                category=4
            elif bmi>27.76:
                category=5
        elif age==14:
            if bmi<=14.48:
                category=1
            elif 14.49<=bmi<=16.87:
                category=2
            elif 16.88<=bmi<=23.33:
                category=3
            elif 23.34<=bmi<=28.57:
                category=4
            elif bmi>28.57:
                category=5
        elif age==15:
            if bmi<=15.01:
                category=1
            elif 15.02<=bmi<=17.44:
                category=2
            elif 17.45<=bmi<=23.93:
                category=3
            elif 23.94<=bmi<=29.11:
                category=4
            elif bmi>29.11:
                category=5
        elif age==16:
            if bmi<=15.46:
                category=1
            elif 15.47<=bmi<=17.90:
                category=2
            elif 17.91<=bmi<=24.36:
                category=3
            elif 24.37<=bmi<=29.43:
                category=4
            elif bmi>29.43:
                category=5
        elif age==17:
            if bmi<=15.78:
                category=1
            elif 15.79<=bmi<=18.24:
                category=2
            elif 18.25<=bmi<=24.69:
                category=3
            elif 24.70<=bmi<=29.69:
                category=4
            elif bmi>29.69:
                category=5
        elif age==18:
            if bmi<=15.99:
                category=1
            elif 16.00<=bmi<=18.49:
                category=2
            elif 18.50<=bmi<=24.99:
                category=3
            elif 25.00<=bmi<=30.00:
                category=4
            elif bmi>30.00:
                category=5
    return category