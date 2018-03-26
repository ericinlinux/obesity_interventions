import pandas as pd


def get_graphs_PA_df(graph):
    results_dict = dict(graph.nodes(data=True))
    PA_dict = {}
    for k, v in results_dict.items():
        PA_dict[k] = results_dict[k]['PA_hist']
    return pd.DataFrame(PA_dict).mean(axis=1)