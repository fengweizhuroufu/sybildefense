from evaluations import parameters
from evaluations.run_experiment import run_experiment

"""
	Experiment:
	Determine the success rate influences the performance

	Variations:
	Success Rate:
		0.2 - 0.8
		0.1 - 0.5

	Systems:
	All Systems, all scenarios

"""

for i in ((0.2, 0.7), (0.1, 0.5)):
	paras = parameters.ParameterSettingsP(graph='facebook', strategy='breadthFirst', boosted=True, evalAt=(50,), maxRequests=51, numRepeats=3)
	paras.acceptanceRatioLimits = i
	paras.numSeeds = 100
	run_experiment(paras, saveAs='ratio{}PTar.p'.format(i))

	paras = parameters.ParameterSettingsP(graph='facebook', strategy='random', boosted=False, evalAt=(50,), maxRequests=51, numRepeats=3)
	paras.acceptanceRatioLimits = i
	paras.numSeeds = 100

	run_experiment(paras, saveAs='ratio{}PRand.p'.format(i))

	paras = parameters.ParameterSettingsSR(graph='facebook', evalAt=(50,), maxRequests=51, numRepeats=3)
	paras.acceptanceRatioLimits = i
	paras.numSeeds = 100

	run_experiment(paras, saveAs='ratio{}SRRand.p'.format(i))
