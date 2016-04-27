import random as rn
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from itertools import chain
import timeit
import sys
import os
sys.path.append(os.path.join(os.path.dirname('../../')))
from GreedySetCover.main import library

ntrials = 1


def main():
    start = timeit.default_timer()
    tot_gen_time = 0
    problems = sorted(library)  # sorted([_ for _ in library if "scpe" in _])
    for current_problem in problems:
        # current_problem = 'scpcyc07'
        file_location = "../../library/" + current_problem + ".txt"

        # IMPORT
        start_import = timeit.default_timer()

        costs, rsets, lsets = import_problem(file_location, w=False, v=True)
        costs = np.asarray(costs, dtype='uint16')

        stop_import = timeit.default_timer()
        import_time = stop_import - start_import
        # print(import_time)

        # GENERATE
        solnsets = []
        solncosts = []
        times = []
        # timelimit = tot_gen_time + 5
        # while tot_gen_time < timelimit:
        for _ in xrange(ntrials):
            start_gen = timeit.default_timer()
            trialsoln, incidence = generate(rsets, lsets, costs)
            stop_gen = timeit.default_timer()
            gen_time = stop_gen - start_gen

            solnsets.append(trialsoln)
            solncosts.append(np.sum(costs[trialsoln]))
            times.append(gen_time)
            tot_gen_time += gen_time
        print(tot_gen_time)

        # df = pd.DataFrame.from_dict({'sets': solnsets,
        #                              'cost': solncosts,
        #                              'time': times})
        # df.to_csv('out/'+current_problem+'.csv')
        # library[current_problem] = {current_problem: library[current_problem],
        #                             'dataframe': df}

        # freq = df['cost'].value_counts()
        # fill_index = np.arange(np.min(freq.index.values),
        #                        np.max(freq.index.values) + 1)
        # freq_filled = freq.reindex(fill_index, fill_value=0)
        # freq_filled.plot.bar()
        # plt.show()

        print(np.sum(costs[trialsoln]), gen_time)
        check(rsets, lsets, costs, trialsoln, incidence)
        print('---')
    stop = timeit.default_timer()
    print(stop - start, tot_gen_time)


def generate(rsets, lsets, costs):
    """
    Pick an initial state for SA.
     Fast randomized greedy search for reduced feasible solution
    """
    trialsoln = []
    incidence = np.zeros(len(lsets), dtype='uint16')
    uncovered = set(xrange(len(lsets)))  # should correspond to incidence=0

    while uncovered:  # nonempty set evaluates True
        hitme = rn.choice(tuple(uncovered))  # random element
        # find a set in U-S which hits chosen element
        # for s in lsets[hitme]:
        #     if s not in trialsoln:
        #         trialsoln.append(s)
        #         incidence[list(rsets[s])] += 1
        #         uncovered -= set(rsets[s])
        #         break
        s = lsets[hitme][0]
        trialsoln.append(s)
        incidence[list(rsets[s])] += 1
        uncovered -= set(rsets[s])

    # check for redundancy. Since we add low cost rsets first, the last rsets
    #  added are more likely to be more costly; check last first.
    # Removal is O(n), so identify sets to remove then remove them all at once
    dropme = set()
    for s in reversed(trialsoln):  # iterator is reversed, not trialsoln!
        if np.all(incidence[list(rsets[s])] - 1):
            incidence[list(rsets[s])] -= 1
            dropme.add(s)
    trialsoln[:] = [s for s in trialsoln if s not in dropme]

    return (trialsoln, incidence)


def check(rsets, lsets, costs,
          trialsoln, incidence, v=0):
    if v == 1:
        print(trialsoln)
        print(incidence)
    """DEPRECATED
    # Do we have a complete cover?
    covered = set(chain.from_iterable([rsets[s] for s in trialsoln]))
    print(covered - set(xrange(nelems)))
    print(set(xrange(nelems)) - covered)
    assert covered == set(xrange(nelems))
    """
    # We construct the cover as a list.
    #  Do we list a set more than once?
    assert len(trialsoln) - len(set(trialsoln)) == 0


def import_problem(file_location, w=True, v=True):
    input_file = open(file_location)
    current_line = input_file.readline().split(' ')
    number_of_elements = int(current_line[1])
    number_of_rsets = int(current_line[2])
    if v:
        print(input_file.name)
        print('Sets: {0}, Elements: {1}'
              .format(number_of_rsets, number_of_elements))

    rsets = [[] for _ in xrange(number_of_rsets)]
    lsets = []
    costs = []

    while len(costs) < number_of_rsets:
        costs.extend([int(x) for x in
                      input_file.readline().strip().split(' ')])

    current_element = 0

    while True:
        current_line = input_file.readline()
        if not current_line:
            break
        nhits = int(current_line)
        lset = []
        while len(lset) < nhits:
            lset.extend([int(x) - 1 for x in
                         input_file.readline().strip().split(' ')])
        lsets.append(tuple(lset))
        for rset_number in lset:
            rsets[int(rset_number)].append(current_element)
        current_element += 1
    input_file.close()

    if w:
        assert len(lsets) == number_of_elements
        assert len(rsets) == number_of_rsets

    lsets = tuple(lsets)
    rsets = tuple(tuple(elem for elem in s) for s in rsets)
    return costs, rsets, lsets

if __name__ == "__main__":
    main()


# Search
#     Perturb
#     """
#     Remove columns to produce partial solution.
#     Randomly or by least uniqueness
#     """
#     Construct
#     """
#     Create feasible solution from partial solution.
#     Greedy heuristic
#     """
#     Redund
#     """
#     Remove unnecessary columns.
#     Consider columns in decreasing order of cost for feasible removal
#     """
