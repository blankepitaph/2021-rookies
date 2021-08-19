'''
transform.py - transform Google Forms tsv output to long format

usage:
    python transform.py [input (.tsv)] [output (.tsv)]

requires python3.6

written by u/blankepitaph
'''

import sys
import re
import csv

raw_data = sys.argv[-2]
clean_data = sys.argv[-1]

def parse_line(line):
    line_list = []
    first_team = line['first-team'].split(', ')
    second_team = line['second-team'].split(', ')
    
    # check for doubles
    double_votes = set(first_team).intersection(set(second_team))
    if len(double_votes) > 0:
        return None # spoiled vote

    # parse selections
    for i, selection in enumerate([first_team, second_team]):
        for player in selection:
            if i == 0:
                vote = 'first_team'
            elif i == 1:
                vote = 'second_team'
            if selection[0]: # some people may have left second team empty
                try:
                    player_team = re.search('^[A-Z]{3,4}', player).group()
                    player_handle = re.search('- (\w+) ', player).group(1)
                    player_role = re.search('\(([A-Z\/]+)\)$', player).group(1)
                except AttributeError as e:
                    raise Exception(f'{i} {player} {selection} bonked the regex')
                out = {'timestamp': line['timestamp'],
                    'player': player_handle, 'team': player_team,
                    'role': player_role, 'selection': vote}
                line_list.append(out)

    return line_list

def main():
    with open(clean_data, 'w') as f:
        fieldnames = ['timestamp', 'player', 'team', 'role', 'selection']
        writer = csv.DictWriter(f, delimiter='\t', fieldnames=fieldnames)
        writer.writeheader()
        with open(raw_data, 'r') as f_in:
            fieldnames_in = ['timestamp', 'first-team', 'second-team', 'comments']
            reader = csv.DictReader(f_in, delimiter='\t', fieldnames=fieldnames_in)
            _ = next(reader) # discard first line
            counter, spoiled, total = 0, 0, 0
            for i, line in enumerate(reader):
                line_list = parse_line(line)
                if line_list:
                    counter += 1
                    for line_out in line_list:
                        total += 1
                        writer.writerow(line_out)
                else:
                    spoiled += 1

    print(f'{total} votes cast over {counter} submissions',
          f'{spoiled} ballots were spoiled (double votes)')

if __name__ == '__main__':
    main()

