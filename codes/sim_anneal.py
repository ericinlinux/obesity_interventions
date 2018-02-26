import pandas as pd


def get_emp_PA(metric='steps', level_f='../'):
    '''
    Return a DataFrame with the PA for the beggining and end
    '''
    
    fitbit = pd.read_csv(level_f+'data/fitbit.csv', sep=';', header=0)
    
    original_PA = fitbit[fitbit.Wave != 4]
    final_PA = fitbit[fitbit.Wave == 4]
    if metric == 'steps':
        initial_steps_df = original_PA.groupby(['Child_Bosse']).mean()['Steps_ML_imp1'] * 0.000153
        final_steps_df = final_PA.groupby(['Child_Bosse']).mean()['Steps_ML_imp1'] * 0.000153
    else:
        print('Metric as MVPA still to implement...')
        return

    empirical_data = pd.DataFrame([initial_steps_df, final_steps_df], ['Initial', 'Final']).T

    return empirical_data


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
    inf_I_PA = -0.01
    sup_I_PA = 0.01
    
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


def get_error(graph, empirical):

    PA_results = {}
    for node in G_all.nodes():
        PA_results[node] = G_all.nodes[node]['PA_hist']

    PA_df = pd.DataFrame(PA_results).T

    PA_sim = PA_df[[0, 30, 60, 364]]
    PA_sim.columns = ['W1', 'W2', 'W3', 'W4']
    empirical.columns = ['W1', 'W2', 'W3', 'W4']
    
    return ((PA_sim - empirical)**2).sum().sum()