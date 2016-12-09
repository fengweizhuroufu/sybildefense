__author__ = 'Martin'
import random
import pickle
import networkx as nx
from util import calc
from util.keys import SF_Keys
from evaluations import eval_systems, parameters
from sybil import integro, sybilframe
from collections import defaultdict

from util import graph_creation


def run_experiment(paras):
	for i in range(paras.numRepeats):

		" set parameters "
		getAcceptance = calc.getAcceptanceClosure(paras.acceptanceRatioLimits[0], paras.acceptanceRatioLimits[1])

		getVictimNodeProb = calc.getNodeProbClosure(paras.nodeProbVictim)
		getNonVictimNodeProb = calc.getNodeProbClosure(paras.nodeProbNonVictim)

		getSybilNodeProb = calc.getNodeProbClosure(paras.nodeProbSybil)
		getNonSybilNodeProb = calc.getNodeProbClosure(paras.nodeProbNonSybil)
		getSybilEdgeProb = calc.getNodeProbClosure(paras.edgeProbSybil)
		getNonSybilEdgeProb = calc.getNodeProbClosure(paras.edgeProbNonSybil)

		results_list = []
		return_package = (results_list, paras)

		"create benign region from graph"
		for j in range(paras.numRepeats):
			if paras.graph == 'smallWorld':
				g = graph_creation.create_directed_smallWorld(paras.sizeSmallWorld, paras.edgesSmallWorld)
			elif paras.graph == 'facebook':
				g = nx.read_adjlist(paras.datasetLocations[paras.graph])
				g = nx.convert_node_labels_to_integers(g)
				g = graph_creation.undirected_to_directed(g)
			elif paras.graph == 'newOrleans':
				g = nx.read_adjlist(paras.datasetLocations[paras.graph])
				g = nx.convert_node_labels_to_integers(g)
				g = graph_creation.undirected_to_directed(g)
			elif paras.graph == 'david':
				g = nx.read_edgelist(paras.datasetLocations[paras.graph], 'r', nodetype=int)
				g = nx.convert_node_labels_to_integers(g)
				g = graph_creation.undirected_to_directed(g)

		nx.set_node_attributes(g, 'label', 0)
		NUM_HONEST = len(g.nodes())
		NUM_ATTACKERS = paras.numSybils

		seeds = []
		if paras.seedsStrategy == 'list':
			for s in paras.seedsList:
				seeds.append(s)

		"add boosting region"
		if paras.boosted:
			r = []
			for i in range(paras.numDummies):
				while True:
					h = random.randint(0, NUM_HONEST - 1)
					if h not in r and h not in seeds:
						g.add_edge(h, NUM_HONEST, {'trust': 1})
						r.append(h)
						break

			g.add_edge(NUM_HONEST, NUM_HONEST + 1, {'trust': 1})
			g.add_edge(NUM_HONEST + 1, NUM_HONEST + 2, {'trust': 1})
			g.add_edge(NUM_HONEST + 2, NUM_HONEST, {'trust': 1})

			for i in range(3):
				g.node[NUM_HONEST + i]['label'] = 1

		"add sybil nodes"
		attackers = []

		"create sybil region for sybil region scenario"
		if paras.scenario == 'SR':
			graph_creation.add_community(g, paras.sizeSybilRegion, 0, type='sybil')
			for i in range(NUM_HONEST, NUM_HONEST+NUM_ATTACKERS):
				g.node[i]['label'] = 1
				attackers.append(i)


		elif paras.scenario == 'P':
			"create peripheral sybils (including boosting if boosting) for peripheral scenario"

			for i in range(NUM_ATTACKERS):
				offset = 0
				if paras.boosted:
					offset = 3
				g.add_node(NUM_HONEST + i + offset, {'label': 1})
				g.add_edge(NUM_HONEST + i + offset, NUM_HONEST, {'trust': 1})
				g.add_edge(NUM_HONEST + i + offset, NUM_HONEST + 1, {'trust': 1})
				g.add_edge(NUM_HONEST + i + offset, NUM_HONEST + 2, {'trust': 1})

			attackers.append(NUM_HONEST+offset+i)

		""" set node prob"""
		for i in g.nodes_iter():
			if g.node[i]['label'] == 0:
				prob_victim = getNonVictimNodeProb()
				prob_sybil = getNonSybilNodeProb()
			else:
				prob_victim = getVictimNodeProb()
				prob_sybil = getSybilNodeProb()

			g.node[i]['prob_victim'] = prob_victim
			g.node[i][SF_Keys.Potential] = sybilframe.create_node_func(prob_sybil)

		"set seed attributes"
		nx.set_node_attributes(g, 'seed', 0)
		for s in seeds:
			g.node[s]['seed'] = 1

		"create customized graph for each system"
		g_votetrust = g.copy()
		g_integro = nx.Graph(g)
		g_sybilframe = nx.DiGraph(g_integro)


		" set edge prob for sybilframe"
		for start, end in g_sybilframe.edges_iter():
			if g.node[start]['label'] == g.node[end]['label']:
				prob = getNonSybilEdgeProb()
			else:
				# print('ATTACK EDGE!!')
				prob = getSybilEdgeProb()
			g_sybilframe[start][end][SF_Keys.Potential] = sybilframe.create_edge_func(prob)

		"set pool for breadth first"
		if paras.strategy == 'twoPhase' or paras.strategy == "breadthFirst":
			pools = defaultdict(lambda : [])

		"set vuln pools for two phase strategy"
		if paras.strategy == 'twoPhase':
			pools_vuln = defaultdict(lambda : [])
			list_vuln = []
			for i in range(paras.numVuln):
				for j in attackers:
					while True:
						r = random.randint(0, NUM_HONEST-1)
						if r not in list_vuln:
							list_vuln.append(r)
							break
					pools_vuln[j].append(r)

		"successively add attack edges"
		requested = defaultdict(lambda : [])

		"container for results"
		results = {'integro': [], 'votetrust': [], 'sybilframe': []}

		for i in range(paras.maxRequests):
			"determine if systems should be run"
			if paras.evalAt == i or (not paras.evalAt and paras.evalInterval % i == 0):
				print('eval')
				results['integro'].append(eval_systems.eval_system(g_integro, system='integro'))
				results['votetrust'].append(eval_systems.eval_system(g_votetrust, system='votetrust'))
				results['sybilframe'].append(eval_systems.eval_system(g_sybilframe, system='sybilframe'))

			"Select new victims"
			for s in attackers:
				vuln_flag = False
				h = None
				if paras.strategy in ('breadthFirst', 'twoPhase'):
					if len(pools[s]) > 0:
						h = pools[s][0]
						pools[s].remove(h)

					elif paras.strategy == 'twoPhase':
						if len(pools_vuln[s]) > 0:
							h = pools[s][0]
							pools_vuln[s].remove(h)
							vuln_flag = True

				"select random honest node if strategy is random or specific strategies are out of targeted nodes"
				if h == None:
					while True:
						h = random.randint(0, NUM_HONEST - 1)
						if (h not in requested[s]) and (h not in seeds):
							break

				if vuln_flag:
					trust = calc.getSuccessByProb(paras.vulnAcceptanceProb)

				else:
					num_common_friends = len(set(g.neighbors(h)).intersection(set(g.neighbors(s))))
					trust = getAcceptance(num_common_friends)

				g_votetrust.add_edge(s, h, {'trust': trust})
				if trust == 1:
					if paras.strategy in ('breadthFirst', 'twoPhase'):
						friends_of_friend = g.neighbors(h)
						if s in friends_of_friend:
							friends_of_friend.remove(s)
						pools[s].extend(friends_of_friend)

						""" magic list conversion to remove duplicates and seeds"""
						seen = set()
						seen_add = seen.add
						pools[s] = [x for x in pools[s] if not (x in seen or seen_add(x)) and x not in requested[s]+seeds]

					g.node[h]['prob_victim'] = getVictimNodeProb()

					g_sybilframe.add_edge(s, h, {SF_Keys.Potential: sybilframe.create_edge_func(getSybilEdgeProb())})
					g_sybilframe.add_edge(h, s, {SF_Keys.Potential: sybilframe.create_edge_func(getSybilEdgeProb())})
					g.add_edge(s, h)

				requested[s].append(h)
			results_list.append(results)

	"create filename from parameters"
	filename = 'res_'
	filename += paras.strategy+'_'

	if paras.boosted:
		filename += 'boosted_'
	else:
		filename += 'noboost_'

	filename += paras.graph+'_'
	filename += paras.scenario+'.p'

	"save results as file"
	pickle.dump(return_package, open("../pickles/"+filename, "wb+"))

paras = parameters.ParameterSettingsP(graph='newOrleans', strategy='breadthFirst', boosted='True', evalAt=50, maxRequests=51)
#paras = parameters.ParameterSettingsP(graph='newOrleans', strategy='random', boosted=False, evalAt=50, maxRequests=51)
#paras = parameters.ParameterSettingsSR(graph='newOrleans', evalAt=10, maxRequests=11)
run_experiment(paras)