



def select_nodes_random():
	return


def select_nodes_centrality():
	return


def select_nodes_high_risk():
	return


def select_nodes_max_influence():
	return


def select_nodes_vulnerable():
	return

def diffuse_behavior(graph, intervention='none', years=3, level_f='../'):
	'''
	|- diffuse-behavior (influente_PA or influence_EI?)
		|-- neighbors -> node
	|- update
		|-- node weight is updated
	'''

	for t in range(365*years):
		if t == 0:
			# Initiate hist vectors
			for node in graph.nodes():
				graph.nodes()[node]['PA_hist'] = [graph.nodes()[node]['PA']]
				graph.nodes()[node]['EI_hist'] = [graph.nodes()[node]['EI_Kcal']]
				graph.nodes()[node]['BW_hist'] = [graph.nodes()[node]['weight']]
				graph.nodes()[node]['BMI_hist'] = [graph.nodes()[node]['weight']/(graph.nodes()[node]['height']*graph.nodes()[node]['height'])]
			continue
		print(t)
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
			for pred in graph.predecessors(node):
				inf_PA = inf_PA + (graph.nodes()[pred]['PA_hist'][t-1] - PA)
				inf_EI = inf_EI + (graph.nodes()[pred]['EI_hist'][t-1] - EI)
			# Combined influence
			inf_PA = inf_PA/len(list(graph.predecessors(node)))
			inf_EI = inf_EI/len(list(graph.predecessors(node)))

			# 2
			inf_PA_env = inf_PA * env if inf_PA >= 0 else inf_PA / env
			inf_EI_env = inf_EI * env if inf_EI < 0 else inf_EI / env
			
			# 3
			thres_EI_l = 0.02
			thres_EI_h = 0.2

			thres_PA_l = 0.02
			thres_PA_h = 0.2

			I_PA = 0.125
			I_EI = 0.125
			# For PA
			if inf_PA_env > 0 and abs(inf_PA_env) > thres_PA_h * PA:
				PA_new = PA * (1 + I_PA)
			if inf_PA_env < 0 and abs(inf_PA_env) < thres_PA_l * PA:
				PA_new = PA * (1-I_PA)
			# For EI
			if inf_EI_env > 0 and abs(inf_EI_env) > thres_EI_h * EI:
				EI_new = EI * (1 + I_EI)
			if inf_EI_env < 0 and abs(inf_EI_env) < thres_EI_l * EI:
				EI_new = EI * (1-I_EI)

			# update
			delta = 0.9*EI_new - PA_new * (0.083 * BW + 0.85)
			BW_new = BW + (delta/32.2)
			BMI_new = BW/(height*height)

			graph.nodes()[node]['PA_hist'].append(PA_new)
			graph.nodes()[node]['EI_hist'].append(EI_new)
			graph.nodes()[node]['BW_hist'].append(BW_new)
			graph.nodes()[node]['BMI_hist'].append(BMI_new)


	return graph