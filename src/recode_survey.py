"""
   Convert "Heath Robinson Museum Survey", aka V1, to "Heath Robinson Museum Short Survey", aka V2.
"""
import argparse
import csv
import sys

hdr_filename = 'data/short_survey_hdr.csv'

'''
Some of the questions in V1 do not exist in V2, so we must skip them.
The tuple 'skips' consists of pairs where the first number is the row in the
new table where we have to skip reading the old table to the second number.
'''
skips = ((9, 85), (69, 152), (111, 209), (142, 291),
         (sys.maxsize, sys.maxsize))


def pivot():
    infile = open(sys.argv[1], newline='')
    reader = csv.reader(infile)
    outfile = open(sys.argv[2], 'w', newline='')
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
    pivott = zip(*table)
    for row in pivott:
        writer.writerow(row)


def one_row(oldrow):
    if len(oldrow) < maxrowlen:
        oldrow += ['' for x in range(maxrowlen - len(oldrow))]
    newrow = []
    col_new = col_old = 0
    for c_new, c_old in skips:
        while col_new < c_new:
            try:
                newrow.append(oldrow[col_old])
            except IndexError:  # done with oldrow
                return newrow
            col_new += 1
            col_old += 1
        col_old = c_old


def main():
    global maxrowlen
    infile = open(sys.argv[1], newline='')
    reader = csv.reader(infile)
    outfile = open(sys.argv[2], 'w', newline='')
    writer = csv.writer(outfile)
    hdr_file = open(hdr_filename, newline='')
    hdr_reader = csv.reader(hdr_file)
    maxrowlen = 0
    for row in hdr_reader:
        maxrowlen = max(maxrowlen, len(row))
        writer.writerow(row)
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
    maxrowlen = 0
    main()
