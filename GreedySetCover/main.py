from __future__ import division
from fractions import Fraction
import timeit


def main():
    output = open("test.html", 'w')
    output.write("<html><body><table border=1>\n")
    output.write("<tr><th>Problem</th><th>Elements</th><th>Sets</th><th>Optimal</th>"
                 "<th>Greedy</th><th>Harmonic</th><th>Run Time</th></tr>\n")
    for current_problem in sorted(library):
        file_location = "../library/" + current_problem + ".txt"
        optimal = library[current_problem]

        sets = []
        costs = []
        number_of_elements = import_problem(file_location, sets, costs)

        picked_sets = []
        start = timeit.default_timer()
        total_cost = greedy_set_cover(number_of_elements, sets, costs, picked_sets)
        stop = timeit.default_timer()
        run_time = stop - start
        print "Picked Sets: ", picked_sets
        print "Greedy Cost: ", total_cost
        print "Optimal Cost: ", optimal
        print "Run time: ", run_time

        largest_set = find_largest_set(sets)
        largest_set_size = len(sets[largest_set])
        # print "Guaranteed Greedy Cost(log): ", (1 + math.log(largest_set_size)) * optimal
        guaranteed_cost = harmonic(largest_set_size) * optimal
        print "Guaranteed Greedy Cost(H): ", guaranteed_cost

        output.write("<tr><td>" + str(current_problem) + "</td><td>" + str(number_of_elements) + "</td><td>" +
                     str(len(sets)) + "</td><td>" + str(optimal) + "<td>" + str(total_cost) + "</td><td>" +
                     str(int(guaranteed_cost)) + "</td><td>" + str(run_time) + "</td></tr>\n")
    output.write("</table></body></html>")
    output.close()


def greedy_set_cover(number_of_elements, sets, costs, picked_sets):
    covered = set()
    total_cost = 0
    while len(covered) < number_of_elements:
        min_cost = float('inf')
        min_cost_set = 0
        for current_set in xrange(len(sets)):
            current_uncovered = len(sets[current_set].difference(covered))
            if current_uncovered == 0:
                cost = float('inf')
            else:
                cost = costs[current_set]/current_uncovered
            if cost < min_cost:
                min_cost = cost
                min_cost_set = current_set
        covered = covered.union(sets[min_cost_set])
        total_cost += costs[min_cost_set]
        picked_sets.append(min_cost_set)
    return total_cost


def import_problem(file_location, sets, costs):
    input_file = open(file_location)
    print input_file.name

    current_line = input_file.readline().split(' ')
    number_of_elements = int(current_line[1])
    number_of_sets = int(current_line[2])
    print "Sets: ", number_of_sets, " Elements: ", number_of_elements
    for _ in xrange(number_of_sets):
        sets.append(set())

    while len(costs) < number_of_sets:
        current_line = input_file.readline().split(' ')[1:-1]
        costs.extend(current_line)
    for i in xrange(len(costs)):
        costs[i] = int(costs[i])

    current_element = 1

    while True:
        current_line = input_file.readline()
        if not current_line:
            break
        upcoming_sets = int(current_line)
        upcoming_set = []
        while len(upcoming_set) < upcoming_sets:
            upcoming_set.extend(input_file.readline().split(' ')[1:-1])
        for set_number in upcoming_set:
            sets[int(set_number)-1].add(current_element)
        current_element += 1
    input_file.close()
    return number_of_elements


def find_largest_set(sets):
    largest_set = 0
    largest_set_size = 0
    for i in xrange(len(sets)):
        # print "i: ", i, " Size: ", len(i)
        if len(sets[i]) > largest_set_size:
            largest_set = i
            largest_set_size = len(sets[i])

    # print "Max Set: ", largest_set, " Size: ", largest_set_size, " Set: ", sets[largest_set]
    return largest_set


def harmonic(n):
    harmonic_number = sum(Fraction(1, d) for d in xrange(1, n+1))
    return harmonic_number * 1.0

library = {
    'scp41': 429,
    'scp42': 512,
    'scp43': 516,
    'scp44': 494,
    'scp45': 512,
    'scp46': 560,
    'scp47': 430,
    'scp48': 492,
    'scp49': 641,
    'scp410': 514,
    'scp51': 253,
    'scp52': 302,
    'scp53': 226,
    'scp54': 242,
    'scp55': 211,
    'scp56': 213,
    'scp57': 293,
    'scp58': 288,
    'scp59': 279,
    'scp510': 265,
    'scp61': 138,
    'scp62': 146,
    'scp63': 145,
    'scp64': 131,
    'scp65': 161,
    'scpa1': 253,
    'scpa2': 252,
    'scpa3': 232,
    'scpa4': 234,
    'scpa5': 236,
    'scpb1': 69,
    'scpb2': 76,
    'scpb3': 80,
    'scpb4': 79,
    'scpb5': 72,
    'scpc1': 227,
    'scpc2': 219,
    'scpc3': 243,
    'scpc4': 219,
    'scpc5': 215,
    'scpd1': 60,
    'scpd2': 66,
    'scpd3': 72,
    'scpd4': 62,
    'scpd5': 61,
    'scpe1': 5,
    'scpe2': 5,
    'scpe3': 5,
    'scpe4': 5,
    'scpe5': 5,
    'scpnre1': 0,
    'scpnre2': 0,
    'scpnre3': 0,
    'scpnre4': 0,
    'scpnre5': 0,
    'scpnrf1': 0,
    'scpnrf2': 0,
    'scpnrf3': 0,
    'scpnrf4': 0,
    'scpnrf5': 0,
    'scpnrg1': 0,
    'scpnrg2': 0,
    'scpnrg3': 0,
    'scpnrg4': 0,
    'scpnrg5': 0,
    'scpnrh1': 0,
    'scpnrh2': 0,
    'scpnrh3': 0,
    'scpnrh4': 0,
    'scpnrh5': 0,
    'scpcyc06': 0,
    'scpcyc07': 0,
    'scpcyc08': 0,
    'scpcyc09': 0,
    'scpcyc10': 0,
    'scpcyc11': 0,
    'scpclr10': 0,
    'scpclr11': 0,
    'scpclr12': 0,
    'scpclr13': 0,
}

if __name__ == "__main__":
    main()
