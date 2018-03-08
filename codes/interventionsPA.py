
import numpy as np
import random
import networkx as nx
import pandas as pd

from codes.simulatePA import diffuse_behavior_PA

def get_subgraphs_centrality(graph, level_f='./'):
    # Create a dictionary. Keys are the classes, and the values are list of students
    class_list = [67, 71, 72, 74, 77, 78, 79, 81, 83, 86, 100, 101, 103, 121, 122, 125, 126, 127, 129, 130, 131, 133, 135, 136, 138, 139]
    class_dictionary = {}

    for c in class_list:
        class_dictionary[c] = []
    
    for node, key in graph.nodes.data('class'):
        class_dictionary[int(key)].append(node)

    list_subgraphs = [] 
    cent_dict = {}
    
    for c in class_list:
        #print(class_dictionary[c])
        subgraph = graph.subgraph(class_dictionary[c])
        list_subgraphs.append(subgraph)
        for key, cent in nx.degree_centrality(subgraph).items():
            cent_dict[key]=cent
        #centrality_dict = nx.degree_centrality(subgraph)
    # cent_dict is the dictionary with all centralities for all nodes
    return cent_dict, list_subgraphs


def get_class_dictionary(graph, level_f='../'):
    '''
    Generates the dictionary with BMI and env for each kid per class
    Create a dictionary. Keys are the classes, and the values are list 
        of students
    '''
    
    class_list = [67, 71, 72, 74, 77, 78, 79, 81, 83, 86, 100, 101, 103, 121, 122, 125, 126, 127, 129, 130, 131, 133, 135, 136, 138, 139]
    class_dictionary = {}

    for c in class_list:
        class_dictionary[c] = []

    centrality_dict, _ = get_subgraphs_centrality(graph,level_f)

    for node, key in graph.nodes.data('class'):
        class_dictionary[int(key)].append((node,
                                           graph.nodes[node]['gender'],
                                           graph.nodes[node]['bmi_cat'],
                                           graph.nodes[node]['env'],
                                           centrality_dict[node],
                                           graph.nodes[node]['bmi']))
    return class_dictionary


def apply_intervention(graph, selected_nodes=[], debug=True):
    '''
    Apply the intervention for the PA
    '''
    for node in selected_nodes:
        # 17%
        if debug:
            print('Node #{} - old PA: {}'.format(node,graph.nodes[node]['PA']))
        graph.nodes[node]['PA'] = graph.nodes[node]['PA']*1.17
        graph.nodes()[node]['PA_hist'] = [graph.nodes()[node]['PA']]
        if debug:
            print('Node #{} - new PA: {}'.format(node,graph.nodes[node]['PA']))
    return graph


def apply_intervention_random_nodes(graph, perc=0.1, level_f='../'):
    '''
    Random selection of nodes based purely in the percentage
    '''
    
    list_selected = []
    class_dictionary = get_class_dictionary(graph, level_f)

    print('------------------------------------------------------------------')
    print('Getting {0}% of the nodes'.format(perc))
    print('------------------------------------------------------------------')

    for c, data in class_dictionary.items():
        #print(c, round(len(data)*perc))
        num_selected = round(len(data)*perc)

        total = len(data)
        children = [item[0] for item in data]
        
        list_selected = list_selected + random.sample(children, num_selected)
        
        print('Class {}: #{} nodes'.format(c,num_selected))
        print('{0}'.format(list_selected))

    # Return graph with updated values
    #return list_selected
    return apply_intervention(graph, selected_nodes=list_selected)
    


def apply_interventions_centrality(graph, perc=0.1, level_f='../'):
    '''
    Select nodes with higher centrality
    '''
    list_selected = []

    class_dictionary = get_class_dictionary(graph, level_f)
    #print(class_dictionary)
    print('------------------------------------------------------------------')
    print('Getting {0}% of the nodes for centrality intervention'.format(perc))
    print('------------------------------------------------------------------')

    for c, data in class_dictionary.items():
        
        num_selected = round(len(data)*perc)
        total = len(data)
        # Select the info about centrality and order the list
        centrality_list = [(item[0],item[4]) for item in data]
        centrality_list.sort(key=lambda tup: tup[1],reverse=True)
        
        selected_nodes = centrality_list[0:num_selected]
        selected_nodes = [item[0] for item in selected_nodes]
        list_selected = list_selected + selected_nodes    
        print('Class {}: #{} nodes'.format(c,num_selected))
        print('{0}'.format(selected_nodes))

    return apply_intervention(graph, selected_nodes=list_selected)



def apply_interventions_high_risk(graph, perc=0.1, level_f='../'):
    '''
    Select nodes with higher BMI
    '''
    list_selected = []

    class_dictionary = get_class_dictionary(graph, level_f)
    #print(class_dictionary)
    print('------------------------------------------------------------------')
    print('Getting {0}% of the nodes for high risk intervention (BMI)'.format(perc))
    print('------------------------------------------------------------------')

    for c, data in class_dictionary.items():
        
        num_selected = round(len(data)*perc)
        total = len(data)
        # Select the info about centrality and order the list
        bmi_list = [(item[0],item[5]) for item in data]
        #print(bmi_list)
        bmi_list.sort(key=lambda tup: tup[1],reverse=True)
        
        selected_nodes = bmi_list[0:num_selected]
        selected_nodes = [item[0] for item in selected_nodes]
        list_selected = list_selected + selected_nodes    
        print('Class {}: #{} nodes'.format(c,num_selected))
        print('{0}'.format(selected_nodes))

    return apply_intervention(graph, selected_nodes=list_selected)


def apply_interventions_vulnerability(graph, perc=0.1, level_f='../'):
    '''
    Select nodes with higher BMI
    '''
    list_selected = []

    class_dictionary = get_class_dictionary(graph, level_f)
    #print(class_dictionary)
    print('------------------------------------------------------------------')
    print('Getting {0}% of the nodes for high risk intervention (BMI)'.format(perc))
    print('------------------------------------------------------------------')

    for c, data in class_dictionary.items():
        
        num_selected = round(len(data)*perc)
        total = len(data)
        # Select the info about centrality and order the list
        env_list = [(item[0],item[5]) for item in data]
        #print(env_list)
        env_list.sort(key=lambda tup: tup[1],reverse=True)
        
        selected_nodes = env_list[0:num_selected]
        selected_nodes = [item[0] for item in selected_nodes]
        list_selected = list_selected + selected_nodes    
        print('Class {}: #{} nodes'.format(c,num_selected))
        print('{0}'.format(selected_nodes))

    return apply_intervention(graph, selected_nodes=list_selected)



# Max influence
def apply_intervention_max_influence(graph, perc=0.1, years=1, thres_PA = 0.2, I_PA = 0.00075, level_f='../'):
    '''
    Objective is to maximize the PA of the whole network.
    '''
    
    all_selected = []
    class_dictionary = get_class_dictionary(graph, level_f)
    
    print('------------------------------------------------------------------')
    print('Getting {0}% of the nodes for maximum influence'.format(perc))
    print('------------------------------------------------------------------')

    for c, data in class_dictionary.items():
        print('\nClass {}: Starting'.format(c))
        print('--------------------------------')
        num_selected = round(len(data)*perc)
        total = len(data)
        
        selected_nodes = []
        
        while len(selected_nodes) < num_selected:
            node_n=len(selected_nodes)+1
            
            print('Class {}: Selecting #{} node'.format(c, node_n))
            
            # All nodes in this subgraph
            list_nodes = [item[0] for item in data]
            
            # check the available nodes in the 
            available_nodes = list(set(list_nodes) - set(selected_nodes))
            
            impact_nodes = {}

            for node in available_nodes:
                # copy graph to reset the nodes
                g = graph.subgraph(list_nodes).copy()

                # append without altering selected nodes list...
                temp_list = selected_nodes + [node]
                apply_intervention(g, selected_nodes=temp_list, debug=False)
                diffuse_behavior_PA(g, years=years, thres_PA=thres_PA, I_PA=I_PA)

                # Calculate impact
                sum_diff_PA = 0

                for n in g.nodes():
                    #final_PA = nx.get_node_attributes(g,'PA_hist')[968]
                    final_PA = g.nodes()[n]['PA_hist'][-1]
                    initial_PA = g.nodes()[n]['PA_hist'][0]
                    
                    sum_diff_PA = sum_diff_PA + (final_PA - initial_PA)
                
                impact_nodes[node] = sum_diff_PA
            
            #print('Impact of all nodes:')
            #print(pd.Series(impact_nodes).sort_values(ascending=False))

            # Get the nodes sorted by the BW
            keys_sorted = sorted(impact_nodes, key=impact_nodes.get, reverse=True)
            
            selected_nodes.append(keys_sorted[0])
            all_selected.append(keys_sorted[0])
            print('Selected node: {}'.format(keys_sorted[0]))
            
    return apply_intervention(graph, selected_nodes=all_selected)


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
