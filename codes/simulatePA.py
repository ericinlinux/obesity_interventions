'''
The code below aims to simulate PA for the group of students collected in our data base.
'''
from codes.networkPA import generate_network_PA

def diffuse_behavior_PA(graph, years=1, thres_PA = 0.2, I_PA = 0.00075):
    '''
    Should run the social contagion for the PAs in the model.
    |- Inputs
        |-- years: amount of time for the simulation
        |-- thres_PA: threshold for the PA to take effect
        |-- I_PA: speed factor for PA for the changes
    '''
    for t in range(round(365*years)):
        # Initialize the data on day 0
        if t == 0:
            # Initiate hist vectors
            for node in graph.nodes():
                graph.nodes()[node]['PA_hist'] = [graph.nodes()[node]['PA']]
            continue

        for node in graph.nodes():
            # Cummulative influence from neighbors for PA and EI
            inf_PA = 0
            
            # Current values
            PA = graph.nodes()[node]['PA_hist'][t-1]
            env = graph.nodes()[node]['env']
            
            # Neighbors are the out-edges
            sum_weights = 0
            for pred in graph.predecessors(node):
                w_pred2node = graph.edges[pred, node]['weight']
                sum_weights = sum_weights+w_pred2node
                inf_PA = inf_PA + (graph.nodes()[pred]['PA_hist'][t-1] - PA)*w_pred2node

            # Combined influence
            try:
                inf_PA = inf_PA/sum_weights
            except:
                inf_PA = 0

            # 2
            #if env == 0:
            #    env = 0.0001
            if env <= 0.1:
                env = 0.1
            
            inf_PA_env = inf_PA / env if inf_PA >= 0 else inf_PA * env
            
            # 3
            # thres_PA_h, thres_PA_l, I_PA
            
            # For PA
            '''
            |inf_PA_env| <= thres_PA_l  or thres_PA_h <= |inf_PA_env|
            '''
            if (abs(inf_PA_env) <= thres_PA):
                # Do nothing
                PA_new = PA
            else:
                if inf_PA_env > 0:
                    PA_new = PA * (1 + I_PA)    
                elif inf_PA_env < 0:
                    PA_new = PA * (1 - I_PA)
                else:
                    PA_new = PA

            graph.nodes()[node]['PA_hist'].append(PA_new)

    return graph








if __name__ == "__main__":
    # execute only if run as a script
    graph_all = generate_network_PA(label='all')