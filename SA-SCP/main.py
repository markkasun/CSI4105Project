from __future__ import division
import random as rn
import numpy as np
import pandas as pd
import timeit
import sys
import os
sys.path.append(os.path.join(os.path.dirname('../')))
from GreedySetCover.main import library
import heuristic.main as heuristic


def main():
    nruns = 1
    problems = sorted(library)
    # problems = ['scpcyc10']
    paramdict = {'problem': list(),
                 'size': list(),
                 'T_init': list(),
                 'T_end': list(),
                 'ndrop': list(),
                 'activity_init': list(),
                 'coolrate': list()}

    for problem_name in problems:
        procproblem = process_problem(problem_name, w=False, v=True)
        nelems = len(procproblem['lsets'])
        nsets = len(procproblem['rsets'])
        size = 0
        for s in procproblem['rsets']:
            size += len(s)
        print('Size: {}'.format(size))

        T_init = np.average(procproblem['costs']) * np.log2(size)
        ndrop = int(np.ceil(0.2 * nsets * nelems / size))
        # consider approxcost/meansetweight
        activity_init = nelems
        stages = [(0.05*T_init, 0.8)]
        # stages = [(0.2, 0.8), (0.05, 0.9)]
        # each stage specifies cooling rate and stage end temperature, and
        #   stages supports extension to change cooling function and to swap
        #   workpieces in parallel tempering or adjust localsearch parameters
        paramdict['problem'].append(problem_name),
        paramdict['size'].append(size),
        paramdict['T_init'].append(T_init),
        paramdict['T_end'].append(stages[0][0]),
        paramdict['ndrop'].append(ndrop),
        paramdict['activity_init'].append(activity_init),
        paramdict['coolrate'].append(stages[0][1])

        times = []
        costs = []
        iters = []
        for _ in xrange(nruns):
            local_searcher = heuristic_sampler(ndrop, **procproblem)
            local_searcher.send(None)

            activity_func = lambda x: activity_init * x / T_init
            feasible = init_feasible(**procproblem)
            workpiece = MH_sampler(feasible, activity_func, local_searcher)
            workpiece.send(None)

            oven = oven_gen(T_init)
            oven.send(None)

            iteration = 1
            start_time = timeit.default_timer()

            for T_end, coolrate in stages:
                T = oven.send((lambda x: coolrate*x, workpiece))[0]
                while T > T_end:
                    T, feasible = oven.next()
                    iteration += 1

            stop_time = timeit.default_timer()
            runtime = stop_time - start_time
            times.append(runtime)
            cost = np.sum(procproblem['costs'][feasible['sets']])
            costs.append(cost)
            iters.append(iteration)
            print(cost, runtime)
        print('---')

        # resultsdf = pd.DataFrame.from_dict({'cost': costs,
        #                                     'time': times,
        #                                     'iters': iters})
        # resultsdf.to_csv('out/'+problem_name+'.csv')

    paramdf = pd.DataFrame.from_dict(paramdict)
    paramdf.to_csv('out/parameters.csv')


def process_problem(problem_name, **kwargs):
    """ Load the requested problem and preprocess as desired.
    All problem preprocessing (reduction or analysis) should be done here.
    Must provide:
    - The costs array
    - List-of-lists (LoL) of
    -- the sets: element coverage, and
    -- the elements: set hitting,
      with the sets indexed in natural order, ie., such that
      (i <= j) --> (c[i] <= c[j]). The element ordering follows;
      the element LoL ('lsets') are transpose to the set LoL ('rsets'),
      in the sense that the rsets are a column-wise LoL representation of the
      (sparse) unweighted hypergraph adjacency matrix, the lsets row-wise.
    """
    file_location = "../library/" + problem_name + ".txt"
    costs, rsets, lsets = heuristic.import_problem(file_location, **kwargs)
    costs = np.asarray(costs, dtype='uint16')
    return {'costs': costs, 'rsets': rsets, 'lsets': lsets}


def init_feasible(costs, rsets, lsets):
    """
    Pick an initial state for SA. Must be a feasible solution which
    respects any assumptions made by the MH local search; and should
    be such that MH can return to the initial state.

    As such, it is a good idea to use the same heuristic as we do to
    construct a feasible solution from a partial cover. This guarantees
    consistency and reversibility.
    """
    sets, incidence = heuristic.generate(rsets, lsets, costs)
    return {'sets': sets, 'incidence': incidence}


def heuristic_sampler(ndrop, costs, rsets, lsets):
    proposition = None
    cost_diff = 0
    inertia = 0
    activity = 1

    def dropsets(feasible, ndrop):
        sets = feasible['sets']
        incidence = feasible['incidence']

        # Removal is O(n), so choose sets to remove then remove all at once
        dropme = set()
        for _ in xrange(ndrop):
            dropme.add(rn.choice(sets))

        sets[:] = [s for s in sets if s not in dropme]
        for s in dropme:
            incidence[list(rsets[s])] -= 1
        uncovered = set(np.where(incidence == 0)[0])
        partial = {'sets': sets, 'incidence': incidence,
                   'uncovered': uncovered}  # not a feasible cover!

        return partial, dropme

    def complete(sets, incidence, uncovered):
        # Add
        added = set()
        while uncovered:  # nonempty set evaluates True
            hitme = rn.choice(tuple(uncovered))  # random element
            s = lsets[hitme][0]
            sets.append(s)
            added.add(s)
            incidence[list(rsets[s])] += 1
            uncovered -= set(rsets[s])

        # Reduce
        dropme = set()
        for s in reversed(sets):  # iterator is reversed, not trialsoln!
            if np.all(incidence[list(rsets[s])] - 1):
                incidence[list(rsets[s])] -= 1
                dropme.add(s)
        sets[:] = [s for s in sets if s not in dropme]

        proposition = {'sets': sets, 'incidence': incidence}  # feasible!
        return proposition, added, dropme

    while True:
        feasible, activity = yield proposition, cost_diff
        cost_diff = 0
        added = None
        subtracted = None
        inertia = 0

        while inertia < activity:
            inertia += 1
            if added == subtracted:
                partial, dropped = dropsets(feasible, ndrop)
                proposition, added, reduced = complete(**partial)
                subtracted = dropped.union(reduced)
            else:
                negated = subtracted.intersection(added)
                # these sets are generators and upset numpy causing error in
                #   cast to uint on sum over costs. Can't use np.sum or index
                #   costs by list...
                for i in added.difference(negated):
                    cost_diff += costs[i]
                for i in subtracted.difference(negated):
                    cost_diff -= costs[i]
                # cost_diff = np.sum(costs[list(added.difference(negated))]) -\
                #     np.sum(costs[list(subtracted.difference(negated))])
                break


def MH_sampler(feasible, activity_func, local_searcher):
    while True:
        T = yield feasible
        proposed, cost_diff = local_searcher.send((feasible, activity_func(T)))
        if cost_diff < 0 or rn.random() < np.exp(-cost_diff/T):
            feasible = proposed


def oven_gen(T):
    while True:
        f, workpiece = yield T
        while True:
            yield T, workpiece.send(T)
            T = f(T)

if __name__ == "__main__":
    main()
