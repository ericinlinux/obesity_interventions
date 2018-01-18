import json
import networkx as nx
import numpy as np
import pandas as pd
import os
import re

def generate_network(level_f='../data/'):
    '''
    background = pd.read_csv(data_f+'background.csv', sep=';', header=0)
    bmi = pd.read_csv(data_f+'bmi.csv', sep=';', header=0)
    fitbit = pd.read_csv(data_f+'fitbit.csv', sep=';', header=0)
    nominations = pd.read_csv(data_f+'nominations.csv', sep=';', header=0)
    nominations.columns = ['class', 'child', 'wave', 'variable', 'class_nominated', 'nominated', 'same_class']
    pp = pd.read_csv(data_f+'pp.csv', sep=';', header=0)
    pp['sum_waves'] = pp.parti_W1+pp.parti_W2+pp.parti_W3+pp.parti_W4
    '''
    

    create_connections(graph,formula)



def create_agents(graph, level_f='../'):
    '''
    Each agent need the following information:
        |-- gender
        |-- age
        |-- height
        |-- weight
        |-- EI
        |-- EE
        |-- Env
        |-- PA
    '''
    EI_dict = generate_EI(level_f=level_f)
    PA_dict = generate_PA(level_f=level_f)
    gender_dict, age_dict = generate_basic(level_f=level_f)
    environment_dict = generate_environment(level_f=level_f)
    bmi_dict, height_dict, weight_dict = generate_demographics(level_f=level_f)
    
    return

def generate_demographics(level_f='../'):
    
    return


def generate_environment(level_f=level_f):
    '''
    The environment variable is going to be generated randomly by now, but should be replaced later
    '''
    pp = pd.read_csv(level_f+'data/pp.csv', sep=';', header=0)
    list_participants = list(set(pp.Child_Bosse))
    # Random generator.
    environment_dict = {k: random.uniform(0.93, 1.02) for k in list_participants}
    pd.Series(environment_dict).to_csv(level_f+'results/environment.csv')

    return environment_dict


def generate_basic(level_f='../'):
    '''
    Static values. Age changes a little. Used the mean.
    '''
    background = pd.read_csv(level_f+'data/background.csv', sep=';', header=0)
    gender_df = background.groupby(['Child_Bosse']).mean()['Gender']
    age_df = background.groupby(['Child_Bosse']).mean()['Age']
    gender_df.to_csv(level_f+'results/gender.csv')
    age_df.to_csv(level_f+'results/age.csv')
    
    return dict(gender_df), dict(age_df)

def generate_PA(metric='mvpa', level_f='../'):
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
    
    # Mean of minutes from moderate to vigorous activity and steps (all imputed)
    minutes_MVPA_df = fitbit.groupby(['Child_Bosse']).mean()['Minutes_MVPA_ML_imp1']
    steps_df = fitbit.groupby(['Child_Bosse']).mean()['Steps_ML_imp1']

    if metric == 'mvpa':
        minutes_MVPA_df.to_csv(level_f+'results/mvpa.csv')
        return dict(minutes_MVPA_df)
    elif metric == 'steps':
        steps_df.to_csv(level_f+'results/steps.csv')
        return dict(steps_df)
    else:
        print('Metric not valid! >>>', metric)
        return False


def generate_EI(formula_s=None, level_f='../'):
    '''
    Returns a DataFrame with the mean quantity of every product consumed by the participant.
    --> The value should be divided by 4, so it is a weekly value. To make it daily divide by 28.
    '''

    diet_data = pd.read_csv(level_f+'data/dietary_intake.csv', sep=';', header=0)
    # Variables not used for EI
    remove_columns = ['BMI_W2', 'BMI_W4', 'zBMI_W2', 'zBMI_W4', 'BMIcor_W2', 'BMIcor_W4' ]
    # List of products in the intake behavior (foor and beveries)
    # Remove the time stamps and VAS
    list_products = [(re.split('_', x))[5] for x in list(diet_data.columns)[1:-6]]
    list_products = list(set(list_products) - {'TriggerDate', 'TriggerTime', 'VAS', 'Weekend'})

    # Generates the column for each product with the sum for the 4 weeks
    for product in list_products:
        list_columns = list(diet_data.filter(regex=(".*"+product)).columns)
        diet_data[product] = diet_data.filter(regex=(".*"+product)).sum(axis=1)
    # Add the id of the children as a column
    list_products.append('Child_Bos')
    # Select the columns with the total of the products and the ids, fix the index and remove the column with the ids
    consumption = diet_data[list_products]
    consumption.index = consumption.Child_Bos
    list_products.remove('Child_Bos')
    consumption = consumption[list_products]

    # Save
    consumption.to_csv(level_f+'results/EI.csv')

    # Read formula to calculate the weight for the connections
    if formula_s is None:
        formula = json.loads(open(level_f+'settings/agents.json').read())
    else:
        try:
            formula = json.loads(formula_s)
        except:
            print('Formula provided is corrupted.')
            return

    for item, w in formula.items():
        consumption[item] = consumption[item]*w

    EI_dict = dict(consumption.sum(axis=1))
    
    # Mean for 4 weeks of consumption (maybe divide by 28 days?)
    # To be done later, with the values for each product
    # consumption = consumption/4

    # Save results per child
    consumption.sum(axis=1).to_csv(level_f+'results/EI_per_child.csv')

    return EI_dict

def create_connections(graph, formula_s=None, level_f='../'):
    '''
    graph: DiGraph
    formula_s: string containing a json with the weights for each variable
    --------------------------------------------------------------
    Network connections are based on influence from the kids on each other. The variables used are:
    --------------------------------------------------------------
    Health
    --------------------------------------------------------------
    SOC_DI_Com_network: (1 item) with who participants talk about what they eat and drink
    SOC_DI_Impression_management: (1 item) who participants want to come across as somebody who eats and drinks healthy
    SOC_Di_Modelling_reversed: (1 item) who are examples in eating & drinking healthy
    SOC_DI_Modelling: (1 item) who are eating & drinking products participants also want to eat or drink
    --------------------------------------------------------------
    Leadership and influence
    --------------------------------------------------------------
    SOC_GEN_Advice: (1 item) to who participants go to for advice
    SOC_GEN_Friendship: (1 item) with who participants are friends
    SOC_GEN_INNOV: (1 item) who most often have the newest products & clothes
    SOC_GEN_Leader: (1 item) who participants consider as leaders 
    SOC_GEN_Respect: (1 item) who participants respect
    SOC_GEN_Social_Facilitation: (1 item) with who participants hang out / have contact with
    SOC_GEN_Want2B: (1 item) who participants want to be like
    SOC_ME_Com_network: (1 item) with who participants talk about what they see on television  or internet 
    SOC_PA_Com_network: (1 item) with who participants talk about physical activity and sports
    SOC_PA_Impression_management: (1 item) for who participants want to come across as somebody who is doing sports often
    SOC_PA_Modelling_reversed: (1 item) for who participants are examples in sports
    SOC_PA_Modelling: (1 item) who are exercising in a way participants also want to exercise
    --------------------------------------------------------------
    formula should be a dictionary with the variables used and the weights for each of them. For instance:
    {
        SOC_GEN_Advice: 1,
        SOC_GEN_Friendship: 1,
        SOC_GEN_Leader: 1,
        SOC_GEN_INNOV: 0.5,
        SOC_DI_Com_network: 0.5,
        SOC_Di_Modelling_reversed: 0.2
    }
    '''
    # List with all the participants in the experiment
    pp = pd.read_csv(level_f+'data/pp.csv', sep=';', header=0)
    list_participants = list(pp.Child_Bosse)

    # Read the file with the nominations from the participants and adapt the labels for the columns
    nominations = pd.read_csv(level_f+'data/nominations.csv', sep=';', header=0)
    nominations.columns = ['class', 'child', 'wave', 'variable', 'class_nominated', 'nominated', 'same_class']

    # Read formula to calculate the weight for the connections
    if formula_s is None:
        formula = json.loads(open(level_f+'settings/connections.json').read())
    else:
        try:
            formula = json.loads(formula_s)
        except:
            print('Formula provided is corrupted.')
            return

    # Sum of all weights from the formula
    max_score = sum(formula.values())

    # Create a dictionary with the connections and weights
    connections_dict = {}
    for child in list(pp.Child_Bosse):
        connections_dict[child] = {}

    # To avoid repetition of nominations in different waves
    nominations_list = []

    for line in nominations[['child', 'nominated', 'variable']].iterrows():
        (ch, nom, var) = line[1]  
        # Verify if nominated is in the list of participants (pp)
        if nom in list_participants and (ch, nom, var) not in nominations_list:
            # Add value in the key
            connections_dict[ch][nom] = connections_dict[ch].get(nom, 0) + 1*formula[var]
            nominations_list.append((ch, nom, var))
    
    # Make a dataframe and normalize the values for the edges
    connections_df = pd.DataFrame(connections_dict).fillna(0)/max_score
    connections_dict = connections_df.to_dict()
    # Create the edges in the graph
    for node in connections_dict.items():
        destine = node[0]
        origins = node[1]
        for peer, weight in origins.items():
            if weight > 0:
                graph.add_edge(peer, destine, weight=weight)

    # Save the connections file in the results folder
    connections_df.to_csv(level_f+'results/connections.csv')

    return graph
