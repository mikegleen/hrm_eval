"""
    Convert row 1 to column 1, ... , row N to column N.
"""
import argparse
import csv
import sys


def main():
    infile = open(sys.argv[1], newline='')
    outfile = open(sys.argv[2], 'w', newline='')
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    table = list()
    n = 0
    maxlen = 0
    for line in reader:
        n += 1
        if n > _args.numrows:
            break
        # print('{}: {}'.format(n, len(line)))
        maxlen = max(len(line), maxlen)
        table.append(line)
    for line in table:
        if len(line) < maxlen:
            line += ["" for n in range(maxlen - len(line))]
    pivot = zip(*table)
    for row in pivot:
        writer.writerow(row)


def getparser():
    parser = argparse.ArgumentParser(description='''
        Create an output file with the top N rows of the input file pivoted.''')
    parser.add_argument('infile', help='''
        The input CSV file''')
    parser.add_argument('outfile', help='''
        The output CSV file with rows pivoted.''')
    parser.add_argument('-n', '--numrows', required=True, type=int, help='''
        The number of rows to pivot.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    return args


if __name__ == '__main__':
    _args = getargs(sys.argv)
    assert sys.version_info >= (3, 11)
    main()
