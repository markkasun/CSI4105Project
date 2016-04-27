import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.join(os.path.dirname('../../')))
from GreedySetCover.main import library

problems = ['scp47', 'scp510', 'scp62', 'scpa3', 'scpb2', 'scpc4', 'scpd4',
            'scpe5']
problems = ['scp47', 'scpb2', 'scpe5', 'scpcyc09']
problems2 = sorted([_ for _ in library if "scpclr" in _])
problems3 = sorted([_ for _ in library if "scpcyc" in _])
# problems = [probset+'4' for probset in
#             ['scp4', 'scp5', 'scp6', 'scpa', 'scpb', 'scpc', 'scpd',
#              'scpe']]
# problems = ['scpd4']
for current_problem in problems:
    # current_problem = 'scpclr11'

    diagram = plt.figure(current_problem)
    if current_problem == 'scpe5':
        axfreq = diagram.add_subplot(2, 1, 1)
        axtime = diagram.add_subplot(2, 1, 2)
    else:
        axfreq = diagram.add_subplot(1, 1, 1)
    cmap = 'Paired'  # 'gist_rainbow'

    df = pd.read_csv('out/'+current_problem+'.csv')
    freq = df['cost'].value_counts()
    fill_index = np.arange(np.min(freq.index.values),
                           np.max(freq.index.values) + 1)
    freq_filled = freq.reindex(fill_index, fill_value=0)

    binpts = np.repeat(fill_index - 0.5, 2)
    binpts[1::2] += 1
    freqpts = np.repeat(freq_filled.values, 2)
    # axfreq.fill_between(binpts, freqpts, 0)
    cm = plt.get_cmap(cmap)
    cgen = (cm(1.*i/len(freq)) for i in xrange(len(freq)))
    # print xrange(len(freq))
    # print freq
    for i in xrange(0, len(binpts), 2):
        c = 'k' if freqpts[i+1] == 0 else cgen.next()
        # print binpts[i], c
        axfreq.fill_between(binpts[i:i+2], freqpts[i:i+2], color=c)

    if current_problem == 'scpe5':
        # time = df[['time', 'cost']].pivot(columns='cost')
        time = df[['time', 'cost']].groupby('cost')
        time = time.apply(pd.rolling_median, 1, min_periods=0)\
                   .pivot(columns='cost')
        # print time
        time.plot(style='.', ax=axtime, colormap=cmap,
                  sort_columns=True, legend=None)
plt.show()
