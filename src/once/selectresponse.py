# -*- coding: utf-8 -*-
"""
Parameter 1 CSV file to select
Parameter 2 Output CSV file with just those records
-s          text file with one key per row

"""
from argparse import ArgumentParser
import codecs
import csv
import sys


def getargs():
    parser: ArgumentParser = ArgumentParser(
        description='''
        Select rows which match one of a list of keys.  The key is in the first
        (zero-th) column by default or may be specified.
        ''')
    parser.add_argument('infile', help='''
         The input CSV file, assumed to be UTF-8 with an optional BOM.''')
    parser.add_argument('outfile', help='''
         The output CSV file in UTF-8 with BOM.''')
    parser.add_argument('-a', '--all', action='store_true', help='''
    If specified, output all rows with the given key.  The
    default is only output a single instance of a selected row.
    ''')
    parser.add_argument('-c', '--column', default=0,
                        help='''the column containing the key, default=0
        ''')
    parser.add_argument('-s', '--select',
                        help='''text file with one key per line.
        ''')
    parser.add_argument('-v', '--verbose', default=1, type=int, help='''
    Modify verbosity.
    ''')
    args = parser.parse_args()
    return args


def main(infilename, outfilename, selectfilename):
    infile = codecs.open(infilename, 'r', 'utf-8-sig')
    selectfile = codecs.open(selectfilename, 'r', 'utf-8-sig')
    reader = csv.reader(infile)
    outfile = open(outfilename, 'w', newline='')
    writer = csv.writer(outfile)
    select = set()
    rowcount = 0
    for line in selectfile:
        select.add(line.strip())
    print(f'{len(select)} targets.')
    for x in range(3):
        row = next(reader)
        writer.writerow(row)
    for row in reader:
        # print(row[_args.column])
        if row[_args.column].strip() in select:
            writer.writerow(row)
            rowcount += 1
            if not _args.all:
                select.remove(row[_args.column])
    print(f'{rowcount} rows found.')
    if select and not _args.all:
        print('Not found:')
        for key in select:
            print('', key)


if __name__ == '__main__':
    if sys.version_info.major < 3 or sys.version_info.minor < 6:
        raise ImportError('requires Python 3.6')
    _args = getargs()
    main(_args.infile, _args.outfile, _args.select)
    print('End selectresponse.')
