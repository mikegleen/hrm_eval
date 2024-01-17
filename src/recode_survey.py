"""
   Convert "Heath Robinson Museum Survey", aka V1, to "Heath Robinson Museum Short Survey", aka V2.
"""
import argparse
import csv
import sys

'''
Some of the questions in V1 do not exist in V2, so we must skip them.
The following tuple contains tuples of inclusive ranges of rows to keep.
'''
puts = ((1, 9), (86, 145), (152, 193), (209, 217), (223, 244), (291, 301))
puts = [(x[0] - 1, x[1] - 1) for x in puts]  # make zero based
maxrowlen = puts[-1][1]


def one_row(oldrow):
    if len(oldrow) < maxrowlen:
        oldrow += [''] * (maxrowlen - len(oldrow))
    newrow = []
    col = 0
    for putuple in puts:
        col, fin = putuple
        while col <= fin:
            newrow.append(oldrow[col])
            col += 1
    return newrow


def main():
    infile = open(sys.argv[1], newline='')
    reader = csv.reader(infile)
    outfile = open(sys.argv[2], 'w', newline='')
    writer = csv.writer(outfile)
    for row in reader:
        newrow = one_row(row)
        writer.writerow(newrow)


def getparser():
    parser = argparse.ArgumentParser(description='''
        Create an output file with fields converted to the new layout.''')
    parser.add_argument('infile', help='''
        The input CSV file''')
    parser.add_argument('outfile', help='''
        The output CSV file.''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 11)
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs(sys.argv)
    main()
