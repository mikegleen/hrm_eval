"""

"""
import argparse
import codecs
import csv
import sys
from openpyxl import Workbook, load_workbook


def getargs():
    parser = argparse.ArgumentParser(
        description='''
        Clean the data from the Excel spreadsheet
        ''')
    parser.add_argument('infile', help='''
         The input XLSX file containing multiple tabs.''')
    parser.add_argument('outfile',
                        help='''output CSV file.
        ''')
    parser.add_argument('-v', '--verbose', default=1, type=int, help='''
    Modify verbosity.
    ''')
    args = parser.parse_args()
    return args


def main():
    oldwb = load_workbook(_args.infile)
    for name in oldwb.sheetnames:
        print(name)


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    _args = getargs()
    if _args.verbose > 1:
        print(f'verbosity: {_args.verbose}')
    # codecs.open(_args.outfile, 'w', 'utf-8-sig')
    main()
