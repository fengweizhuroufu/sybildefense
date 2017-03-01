from util.calc import getMergedAuc
import pickle
from matplotlib import pyplot as plt
from util import setMatplotlib
from baseparameters import paras as pathParas
graph = 'facebook'

PRandAll = pickle.load(open('../pickles/attackEdges/attackEdgesPRand{}.p'.format(graph),'rb'))
PRandRes = PRandAll[0]
PRandAUC = getMergedAuc(PRandRes)
PRandParas = PRandAll[1]


PTarAll = pickle.load(open('../pickles/attackEdges/attackEdgesPTar{}.p'.format(graph),'rb'))
PTarRes = PTarAll[0]
PTarAUC = getMergedAuc(PTarRes)
PTarParas = PTarAll[1]

SRRandAll = pickle.load(open('../pickles/attackEdges/attackEdgesSRRand{}.p'.format(graph),'rb'))
SRRandRes = SRRandAll[0]
SRRandAUC = getMergedAuc(SRRandRes)
SRRandParas = SRRandAll[1]

PTarTwoPhaseAll = pickle.load(open('../pickles/attackEdges/attackEdgesPTwoPhase{}.p'.format(graph),'rb'))
PTarTwoPhaseRes = PTarTwoPhaseAll[0]
PTarTwoPhaseAUC = getMergedAuc(PTarTwoPhaseRes)
PTarTwoPhaseParas = PTarTwoPhaseAll[1]

PTarNoboostAll = pickle.load(open('../pickles/attackEdges/attackEdgesPTarNoboost{}.p'.format(graph),'rb'))
PTarNoboostRes = PTarNoboostAll[0]
PTarNoboostAUC = getMergedAuc(PTarNoboostRes)
PTarNoboostParas = PTarNoboostAll[1]

f, axarr = plt.subplots(1, 3, figsize=(5.8, 2.5), sharey=True)

x = [x for x in PRandParas.evalAt]

"SR Random"
axarr[0].plot(x, list(SRRandAUC['integro'].values()), 'r-', label='Integro')
axarr[0].plot(x, list(SRRandAUC['votetrust'].values()),'b--', label='Votetrust')
axarr[0].plot(x, list(SRRandAUC['sybilframe'].values()),'k-.', label='SybilFrame')
axarr[0].set_ylabel('Area Under ROC')

axarr[0].set_ylim((0,1.1))
axarr[0].set_title('Sybil Region Random', loc='center')

"P Random"
axarr[1].plot(x, list(PRandAUC['integro'].values()), 'r-')
axarr[1].plot(x, list(PRandAUC['votetrust'].values()),'b--')
axarr[1].plot(x, list(PRandAUC['sybilframe'].values()),'k-.')

axarr[1].set_ylim((0, 1.1))
axarr[1].set_title('Peri. Random', loc='center')
axarr[1].set_xlabel('Number of Requests')


"P Targeted Noboost"
axarr[2].plot(x, list(PTarNoboostAUC['integro'].values()), 'r-')
axarr[2].plot(x, list(PTarNoboostAUC['votetrust'].values()),'b--')
axarr[2].plot(x, list(PTarNoboostAUC['sybilframe'].values()),'k-.')

axarr[2].set_ylim((0, 1.1))
axarr[2].set_title('Peri. Targeted', loc='center')

plt.tight_layout()
plt.subplots_adjust(top=0.9)
f.subplots_adjust(wspace=0.1)
plt.savefig(pathParas['figuresPath']+'/AttackEdges1{}.pdf'.format(graph), format='pdf')

f, axarr = plt.subplots(1, 2, figsize=(4.2, 2.2), sharey=True)

f.suptitle('Systems Performance by Number of Requests', weight='bold')

"P Targeted Boost"
axarr[0].plot(x, list(PTarAUC['integro'].values()), 'r-')
axarr[0].plot(x, list(PTarAUC['votetrust'].values()),'b--')
axarr[0].plot(x, list(PTarAUC['sybilframe'].values()),'k-.')

axarr[0].set_title('Peri. Targeted Boosted', loc='center')
axarr[0].set_ylim((0, 1.1))
axarr[0].set_ylabel('Area Under ROC')


"P Two Phase Boost"
axarr[1].plot(x, list(PTarTwoPhaseAUC['integro'].values()), 'r-')
axarr[1].plot(x, list(PTarTwoPhaseAUC['votetrust'].values()),'b--')
axarr[1].plot(x, list(PTarTwoPhaseAUC['sybilframe'].values()),'k-.')

axarr[1].set_ylim((0, 1.1))
axarr[1].set_title('Peri. Two Phase Boosted', loc='center')
axarr[0].legend(bbox_to_anchor=(0,0.52), loc='upper left')


plt.tight_layout()
plt.subplots_adjust(top=0.78, bottom=0.1)
f.subplots_adjust(wspace=0.1)
plt.savefig(pathParas['figuresPath']+'/AttackEdges2{}.pdf'.format(graph), format='pdf')

