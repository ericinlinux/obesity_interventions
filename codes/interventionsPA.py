
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


def apply_intervention(graph, selected_nodes=[], debug=False):
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


def apply_intervention_random_nodes(graph, perc=0.1, level_f='../', debug=False):
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
        if debug:
            print('Class {}: #{} nodes'.format(c,num_selected))
            print('{0}'.format(list_selected))

    return apply_intervention(graph, selected_nodes=list_selected)
    


def apply_interventions_centrality(graph, perc=0.1, level_f='../', debug=False):
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
        
        if debug:
            print('Class {}: #{} nodes'.format(c,num_selected))
            print('{0}'.format(selected_nodes))

    return apply_intervention(graph, selected_nodes=list_selected)



def apply_interventions_high_risk(graph, perc=0.1, level_f='../', debug=False):
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
        
        if debug:
            print('Class {}: #{} nodes'.format(c,num_selected))
            print('{0}'.format(selected_nodes))

    return apply_intervention(graph, selected_nodes=list_selected)


def apply_interventions_vulnerability(graph, perc=0.1, level_f='../', debug=False):
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
        
        if debug:
            print('Class {}: #{} nodes'.format(c,num_selected))
            print('{0}'.format(selected_nodes))

    return apply_intervention(graph, selected_nodes=list_selected)



# Max influence
def apply_intervention_max_influence(graph, perc=0.1, years=1, thres_PA = 0.2, I_PA = 0.00075, level_f='../', debug=False):
    '''
    Objective is to maximize the PA of the whole network.
    '''
    
    all_selected = []
    class_dictionary = get_class_dictionary(graph, level_f)
    
    print('------------------------------------------------------------------')
    print('Getting {0}% of the nodes for maximum influence'.format(perc))
    print('------------------------------------------------------------------')

    for c, data in class_dictionary.items():
        if debug:
            print('\nClass {}: Starting'.format(c))
            print('--------------------------------')
        num_selected = round(len(data)*perc)
        total = len(data)
        
        selected_nodes = []
        
        while len(selected_nodes) < num_selected:
            node_n=len(selected_nodes)+1
            if debug:
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
            if debug:
                print('Selected node: {}'.format(keys_sorted[0]))
            
    return apply_intervention(graph, selected_nodes=all_selected)



