"""

"""
import argparse
from collections import defaultdict
import codecs
import csv
import sys
from openpyxl import Workbook, load_workbook


class SmartFormatter(argparse.HelpFormatter):

    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)


def getargs():
    parser = argparse.ArgumentParser(formatter_class=SmartFormatter,
                                     description='''
        Clean the data from the Excel spreadsheet
        ''')
    parser.add_argument('infile', help='''
         The input XLSX file containing multiple tabs.''')
    parser.add_argument('outfile',
                        help='''output CSV file.
        ''')
    parser.add_argument('-f', '--function', type=int, required=True, help='''R|
1. List heading rows.
2. Find bad dates.
3. Merge sheets to CSV file. Drop columns 1 and 2.
    ''')
    parser.add_argument('-v', '--verbose', default=1, type=int, help='''
    Modify verbosity.
    ''')
    args = parser.parse_args()
    return args


def list_hdg_rows(wb):  # function 1
    sheets = wb.worksheets
    for sheet in sheets[1:]:
        row = sheet[1]
        # print([r.value for r in row], sheet.title)
        writer.writerow([sheet.title] + [r.value for r in row])


def list_bad_dates(wb):  # function 2
    sheets = wb.worksheets
    for sheet in sheets:
        irows = sheet.iter_rows(max_row=4760, max_col=12)
        next(irows)
        nrow = 1
        for row in irows:
            nrow += 1
            row = [r.value for r in row[:5]]
            try:
                # Convert the datetime into a date string because the default
                # is to emit the date and time.
                row[2] = row[2].strftime('%Y-%m-%d')
            except AttributeError:
                if any(row):
                    print(sheet.title, nrow, [r for r in row])
            # writer.writerow([sheet.title] + [r.value for r in row])


def merge_sheets(wb):  # function 3
    sheets = list(wb.worksheets)
    row = 'date visitors first_visit how_heard local wherefrom'.split()
    writer.writerow(row)  # write header
    for sheet in sheets:
        irows = sheet.iter_rows(max_row=1000, max_col=12)
        next(irows)
        nrow = 1
        for row in irows:
            nrow += 1
            row = [r.value for r in row[2:8]]
            try:
                # Convert the datetime into a date string because the default
                # is to emit the date and time.
                row[0] = row[0].strftime('%Y-%m-%d')
                writer.writerow(row)
            except AttributeError:
                if any(row):
                    print('Bad date: ', sheet.title, nrow, [r for r in row])


def main():
    wb = load_workbook(_args.infile)
    if _args.function == 1:
        list_hdg_rows(wb)
    elif _args.function == 2:
        list_bad_dates(wb)
    elif _args.function == 3:
        merge_sheets(wb)

    # for row in sheet.values:
    #     n += 1
    #     print(n, row)
    #     writer.writerow(row)
    #     if len(row) > 5 and row[5]:
    #         how_heard[row[5].lower().strip()] += 1
    # print(how_heard)
    # for how in sorted(how_heard, key=how_heard.get, reverse=True):
    #     print(how, how_heard[how])


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    _args = getargs()
    if _args.verbose > 1:
        print(f'verbosity: {_args.verbose}')
    print(f'Input: {_args.infile}')
    outfile = codecs.open(_args.outfile, 'w', 'utf-8-sig')
    writer = csv.writer(outfile)
    main()
