'''
Functions related to the diffusion spread in a social network.
Code by: Eric Araujo
'''

import networkx as nx
import random


def apply_intervention(graph, factor=None, selected_nodes=[]):
    # Apply the right intervention
    for node in selected_nodes:
        if factor == 'PA':
            graph.nodes[node]['PA'] = graph.nodes[node]['PA'] + graph.nodes[node]['PA']*0.17
            graph.nodes()[node]['PA_hist'] = [graph.nodes()[node]['PA']]
        elif factor == 'EI':
            graph.nodes[node]['EI'] = graph.nodes[node]['EI'] - graph.nodes[node]['EI']*0.15
            graph.nodes()[node]['EI_hist'] = [graph.nodes()[node]['EI']]
        else:
            print('Wrong factor! Should be PA or EI.')
            return False
    return graph


# Random selection of nodes
def select_nodes_random(graph, factor=None, perc=0.1, level_f='../'):
    # Select nodes by random
    list_nodes = list(graph.nodes())
    num_selected = round(len(list_nodes)*perc)

    selected_nodes = random.sample(list_nodes, num_selected)

    # Return graph with updated values
    return apply_intervention(graph, factor=factor, selected_nodes=selected_nodes)


# Select nodes with higher centrality
def select_nodes_centrality(graph, factor=None, perc=0.1, level_f='../'):

    centrality_dict=nx.degree_centrality(graph)
    keys_sorted = sorted(centrality_dict, key=centrality_dict.get, reverse=True)

    num_selected = round(len(keys_sorted)*0.1)

    selected_nodes = keys_sorted[0:num_selected]

    return apply_intervention(graph, factor=factor, selected_nodes=selected_nodes)


# Select nodes with BMI > 20
def select_nodes_high_risk(graph, factor=None, perc=0.1, level_f='../'):
    list_nodes = list(graph.nodes())
    num_selected = round(len(list_nodes)*perc)

    BMI_dict = {node: graph.nodes()[node]['BMI_hist'][0] for node in list_nodes}

    keys_sorted = sorted(BMI_dict, key=BMI_dict.get, reverse=True)

    selected_nodes = []
    for n in keys_sorted[0:num_selected]:
        if BMI_dict[n] > 20:
            selected_nodes.append(n)

    return apply_intervention(graph, factor=factor, selected_nodes=selected_nodes)


# Vulnerable nodes with env < 1
def select_nodes_vulnerable(graph, factor=None, perc=0.1, level_f='../'):
    list_nodes = list(graph.nodes())
    num_selected = round(len(list_nodes)*perc)

    env_dict = {node: graph.nodes()[node]['env'] for node in list_nodes}

    keys_sorted = sorted(env_dict, key=env_dict.get, reverse=False)

    selected_nodes = []
    for n in keys_sorted[0:num_selected]:
        if env_dict[n] < 1.0:
            selected_nodes.append(n)

    return apply_intervention(graph, factor=factor, selected_nodes=selected_nodes)


# Max influence
def select_nodes_max_influence(graph, factor=None, perc=0.1, objective='min_obese', level_f='../', debug=True):
    '''
    Objective is the variable we want to minize. In the original work it can be min-obese, min-overweight, min-sum-both and min-bw.
        |- min-obese:       sum of BW of people with BMI > 29.9 - sum of ORIGINAL BW of people with BMI > 29.9
        |- min-overweight:  sum BW of people with 25 < BMI <= 29.9 - sum of ORIGINAL BW of people with 25< BMI <= 29.9
        |- min-sum-both:    sum BW of people with BMI > 25 - sum of ORIGINAL BW of people with BMI > 25  
        |- min-bw:          sum BW of all people - sum ORIGINAL BW of all people
    '''
    if debug:
        print('\n#######################################')
        print('Max-influence started!')
        print('Objective function: ', objective)
        print('#######################################\n')

    list_nodes = list(graph.nodes())
    num_selected = round(len(list_nodes)*perc)
    
    if debug:
        print('This max-influence simulation is for a network with {0} nodes and {1} edges'.format(len(graph.nodes()), len(graph.edges())))
        print('Number of nodes to select: ', num_selected)
    
    selected_nodes = []
    
    while len(selected_nodes) < num_selected:
        
        # check the available nodes in the 
        available_nodes = list(set(list_nodes) - set(selected_nodes))
        
        impact_nodes = {}

        for node in available_nodes:
            # copy graph to reset the nodes
            g = graph.copy()

            # append without altering selected nodes list...
            temp_list = selected_nodes + [node]
            apply_intervention(g, factor=factor, selected_nodes=temp_list)
            diffuse_behavior(g, intervention=None, level_f=level_f, debug=False)

            # Get nodes to calculate the average BW
            list_obese=[]
            list_overweight = []
            list_sum_both = []
            list_all = []
            BW_obese = 0
            BW_overweight = 0
            BW_sum_both = 0
            BW_all = 0

            
            for n in g.nodes():
                BMI_node = g.nodes()[n]['BMI_hist'][-1]
                BW_init = g.nodes()[n]['BW_hist'][0]
                BW_final = g.nodes()[n]['BW_hist'][-1]
                BW_diff = BW_final - BW_init
                
                #if debug:
                #    print('\tNode {0}: \t BW initial {1}\t BW diff {2}'.format(n, BW_init, BW_diff))
                
                #if BMI_node > 29.9:
                if BMI_node > 20.9:
                    #print('Found node obese!')
                    list_obese.append(n)
                    list_all.append(n)
                    list_sum_both.append(n)
                    
                    BW_obese += BW_diff
                    BW_all += BW_diff
                    BW_sum_both += BW_diff

                #elif BMI_node > 25 and BMI_node <= 29.9:
                elif BMI_node > 18.0 and BMI_node <= 20.9:
                    list_overweight.append(n)
                    list_all.append(n)
                    list_sum_both.append(n)

                    BW_overweight += BW_diff
                    BW_all += BW_diff
                    BW_sum_both += BW_diff
                else:
                    list_all.append(n)
                    BW_all += BW_diff

            # Sum up the impacts caused in the network
            if debug:
                print('Impact node #{0}: \tobese: {1:.4f} \toverweight: {2:.4f} \tboth: {3:.4f} \tall: {4:.4f} '.format(node, BW_obese, BW_overweight, BW_sum_both, BW_all))

            if objective == 'min-obese':
                impact_nodes[node] = BW_obese
            elif objective == 'min-overweight':
                impact_nodes[node] = BW_overweight
            elif objective == 'min-sum-both':
                impact_nodes[node] = BW_sum_both
            else:
                impact_nodes[node] = BW_all

        # Get the nodes sorted by the BW
        keys_sorted = sorted(impact_nodes, key=impact_nodes.get, reverse=False)
        
        if debug:
            print('Keys in order of impact: ', keys_sorted)
        
        selected_nodes.append(keys_sorted[0])

        if debug:
            print('Node #{0} selected: {1} with an BW impact of {2}!\n'.format(len(selected_nodes), keys_sorted[0], impact_nodes[keys_sorted[0]]))
    if debug:
        print('Applying interventions for the nodes in the list: {}\n'.format(selected_nodes))
    return apply_intervention(graph, factor=factor, selected_nodes=selected_nodes)


def diffuse_behavior(graph, intervention=None, factor=None, objective='min-overweight', years=2, perc=0.1, level_f='../', debug=True):
    '''
    Method 1: ignore EI provided by the snacks.

    |- diffuse-behavior (influente_PA or influence_EI?)
        |-- neighbors -> node
    |- update
        |-- node weight is updated
    '''

    for t in range(round(365*years)):
        if t == 0:
            # Initiate hist vectors
            for node in graph.nodes():
                graph.nodes()[node]['PA_hist'] = [graph.nodes()[node]['PA']]
                #graph.nodes()[node]['EI_hist'] = [graph.nodes()[node]['EI_Kcal']]
                graph.nodes()[node]['EI'] = graph.nodes()[node]['PA'] * (0.083*graph.nodes()[node]['weight']+0.85)/0.9
                graph.nodes()[node]['EI_hist'] = [graph.nodes()[node]['EI']]
                graph.nodes()[node]['BW_hist'] = [graph.nodes()[node]['weight']]
                graph.nodes()[node]['BMI_hist'] = [graph.nodes()[node]['weight']/(graph.nodes()[node]['height']*graph.nodes()[node]['height'])]

            # Interventions in case it is not None
            if intervention is not None:
                print('Intervention started: ', intervention)
                
                if intervention == 'random':
                    select_nodes_random(graph=graph, factor=factor, perc=perc, level_f=level_f)
                elif intervention == 'centrality':
                    select_nodes_centrality(graph=graph, factor=factor, perc=perc, level_f=level_f)
                elif intervention == 'high_risk':
                    select_nodes_high_risk(graph=graph, factor=factor, perc=perc, level_f=level_f)
                elif intervention == 'vulnerable':
                    select_nodes_vulnerable(graph=graph, factor=factor, perc=perc, level_f=level_f)
                elif intervention == 'max-influence':
                    select_nodes_max_influence(graph=graph, factor=factor, objective=objective, perc=perc, level_f=level_f)
                else:
                    print('Wrong intervention ({}) called!'.format(intervention))
            else:
                if debug:
                    print('Simulation without interventions.')
            
            if debug:
                print('Cluster contains {0} nodes and {1} edges!'.format(len(graph.nodes()), len(graph.edges())))

            continue

        #if t % 365 == 0:
        #   print(t)

        for node in graph.nodes():
            # Cummulative influence from neighbors for PA and EI
            inf_PA = 0
            inf_EI = 0
            
            # Current values
            PA = graph.nodes()[node]['PA_hist'][t-1]
            EI = graph.nodes()[node]['EI_hist'][t-1]
            BW = graph.nodes()[node]['BW_hist'][t-1]
            height = graph.nodes()[node]['height']
            env = graph.nodes()[node]['env']
            
            # Neighbors are the out-edges
            sum_weights = 0
            for pred in graph.predecessors(node):
                w_pred2node = graph.edges[pred, node]['weight']
                sum_weights = sum_weights+w_pred2node
                #print(w_pred2node)
                #inf_PA = inf_PA + (graph.nodes()[pred]['PA_hist'][t-1] - PA)
                inf_PA = inf_PA + (graph.nodes()[pred]['PA_hist'][t-1] - PA)*w_pred2node
                inf_EI = inf_EI + (graph.nodes()[pred]['EI_hist'][t-1] - EI)*w_pred2node

            # Combined influence
            try:
                #inf_PA = inf_PA/len(list(graph.predecessors(node)))
                inf_PA = inf_PA/sum_weights
                #inf_EI = inf_EI/len(list(graph.predecessors(node)))
                inf_EI = inf_EI/sum_weights
            except:
                inf_PA = 0
                inf_EI = 0

            # 2
            inf_PA_env = inf_PA * env if inf_PA >= 0 else inf_PA / env
            inf_EI_env = inf_EI * env if inf_EI < 0 else inf_EI / env
            
            # 3
            thres_EI_l = 0.02
            thres_EI_h = 0.2

            thres_PA_l = 0.02
            thres_PA_h = 0.2

            #I_PA = 0.125
            #I_EI = 0.125
            I_PA = 0.00075
            I_EI = 0.00075
            
            # For PA
            if inf_PA_env > 0 and abs(inf_PA_env) > thres_PA_h * PA:
                PA_new = PA * (1 + I_PA)
            elif inf_PA_env < 0 and abs(inf_PA_env) < thres_PA_l * PA:
                PA_new = PA * (1 - I_PA)
            else:
                PA_new = PA

            # For EI
            if inf_EI_env > 0 and abs(inf_EI_env) > thres_EI_h * EI:
                EI_new = EI * (1 + I_EI)
            elif inf_EI_env < 0 and abs(inf_EI_env) < thres_EI_l * EI:
                EI_new = EI * (1-I_EI)
            else:
                EI_new = EI

            # update
            delta = 0.9*EI_new - PA_new * (0.083 * BW + 0.85)
            BW_new = BW + (delta/32.2)
            BMI_new = BW/(height*height)

            graph.nodes()[node]['PA_hist'].append(PA_new)
            graph.nodes()[node]['EI_hist'].append(EI_new)
            graph.nodes()[node]['BW_hist'].append(BW_new)
            graph.nodes()[node]['BMI_hist'].append(BMI_new)


    return 


