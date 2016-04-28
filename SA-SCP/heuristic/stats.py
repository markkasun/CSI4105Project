from __future__ import division
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.join(os.path.dirname('../../')))
from GreedySetCover.main import library

# problems = sorted(library)  # sorted([_ for _ in library if "scpe" in _])
# data = {}
# for current_problem in problems:
#     df = pd.read_csv('out/'+current_problem+'.csv')[['time', 'cost']]
#     data.update({current_problem: df})
# fulldf = pd.concat(data.values(), keys=data.keys())
# print fulldf
# fulldf.to_csv('heuristic.csv')

problems = sorted(library)  # sorted([_ for _ in library if "scpe" in _])
avgtimes = []
avgcosts = []
maxcosts = []
mincosts = []
for current_problem in problems:
    df = pd.read_csv('out/'+current_problem+'.csv')[['time', 'cost']]
    avgtimes.append(df['time'].mean())
    avgcosts.append(df['cost'].mean())
    maxcosts.append(df['cost'].max())
    mincosts.append(df['cost'].min())
heurdf = pd.DataFrame.from_dict({'problem': problems,
                                 'runtime': avgtimes,
                                 'cost': avgcosts,
                                 'maxcost': maxcosts,
                                 'mincost': mincosts}).set_index('problem')
# heurdf.to_csv('heuristic.csv')
appxdf = pd.read_csv('../../GreedySetCover/approxdata.csv')\
         .rename(columns=lambda x: ''.join(x.split()).lower())\
         .set_index('problem')

problemdf = appxdf[['elements', 'sets', 'optimal']].copy()
problemdf['size'] = problemdf['sets'] * problemdf['elements']

appxdf = appxdf[['greedy', 'runtime', 'harmonic']]\
         .rename(columns={'greedy': 'cost', 'harmonic': 'guarantee'})

targetprobdf = problemdf[problemdf['size'] < 1E7]
sortby = {}
sortby['sets'] = targetprobdf\
                 .sort_values(['sets', 'elements'],
                              ascending=[True, True]).index
sortby['elems'] = targetprobdf\
                 .sort_values(['elements', 'sets'],
                              ascending=[True, True]).index
sortby['size'] = targetprobdf\
                 .sort_values(['size', 'sets', 'elements'],
                              ascending=[True, True, True]).index

stats = plt.figure('stats')

nrows = 3
ncols = len(sortby)
col = 0
for sortkey, sortidx in sortby.iteritems():
    col += 1
    axt = stats.add_subplot(nrows, ncols, col)
    heurdf[['cost', 'maxcost', 'mincost']]\
        .loc[sortidx].plot(ax=axt, legend=None)

    appxdf[['cost']].loc[sortidx].plot(ax=axt, color='k',
                                       legend=None)

    axm = stats.add_subplot(nrows, ncols, col + ncols, sharex=axt)
    heurdf['runtime'].loc[sortidx].plot(ax=axm)

    axb = stats.add_subplot(nrows, ncols, col + ncols*2, sharex=axt)
    appxdf['runtime'].loc[sortidx].plot(ax=axb)

    axt.set_title(sortkey, y=1.1)
    if col == 1:
        for ax, ylabel in [[axt, 'cost'],
                           [axm, 'time, heur'],
                           [axb, 'time, appx']]:
            ax.set_ylabel(ylabel, rotation=0, size='large', labelpad=35)

guarpred = plt.figure('guarantee vs cost')

ax = guarpred.add_subplot(1, 1, 1)
appxdf_costsort = appxdf[appxdf['guarantee'] > 0]\
                  .sort_values(['cost'], ascending=[True])
optimal = problemdf['optimal'].loc[appxdf_costsort.index].values
guarantee = appxdf_costsort['guarantee'].values # optimal * H_k
result = appxdf_costsort['cost'].values
ax.scatter(result, guarantee/result, color='g')
ax.scatter(result, optimal/result, color='b')

plt.show()
