from __future__ import division
import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname('../')))
from GreedySetCover.main import library

problems = sorted(library)
avgtimes = []
avgiters = []
avgcosts = []
maxcosts = []
mincosts = []
for current_problem in problems:
    df = pd.read_csv('out/'+current_problem+'.csv')
    avgtimes.append(df['time'].mean())
    avgiters.append(df['iters'].mean())
    avgcosts.append(df['cost'].mean())
    maxcosts.append(df['cost'].max())
    mincosts.append(df['cost'].min())
statsdf = pd.DataFrame.from_dict({'problem': problems,
                                  'runtime': avgtimes,
                                  'iters': avgiters,
                                  'cost': avgcosts,
                                  'maxcost': maxcosts,
                                  'mincost': mincosts}).set_index('problem')
statsdf.to_csv('out/stats.csv')
