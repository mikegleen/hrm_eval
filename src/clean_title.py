"""
    Remove HTML tags from the first two rows in a CSV file.

    Assign question numbers. In the input file, questions start at column 10
    (column 9 if zero based). Only non-empty cells are counted.
"""

import csv
from datetime import datetime as dt
import sys
from bs4 import BeautifulSoup as Bs

import config
from excel_cols import col2num

FIXED_HEADER = 'RespondentID,CollectorID,StartDate,EndDate,IP Address,'
FIXED_HEADER += 'Email Address,First Name,LastName,Custom Data'
FIXED_HEADER = FIXED_HEADER.replace(' ', '').lower().split(',')
SKIPCOLS = len(FIXED_HEADER)
DATE_COLS = ('c', 'd') if config.SHORTSURVEY else ('c', 'd', 'j')


def build_header(row):
    header = FIXED_HEADER
    q_num = 0
    for cell in row[SKIPCOLS:]:
        if cell:
            q_num += 1
            header.append(f'q{q_num}')
        else:
            header.append('')
    return header


def clean_row(dirtyrow):
    n = 0
    row = []
    for cell in dirtyrow:
        n += 1
        soup = Bs(cell, 'html.parser')
        text = soup.get_text()
        if cell != text:
            print(n, cell, '-->', text)
        # print('{}: {}-->{}'.format(minor, cell, text))
        row.append(text)
    return row


def fix1date(row, col):
    # print(f'***{col}')
    # print(row)
    coln = col2num(col)
    s = row[coln]
    if not s:
        return
    if ':' in s:
        # d = dt.strptime(s, '%m/%d/%Y %H:%M:%S')
        d = dt.strptime(s, '%m/%d/%Y %I:%M:%S %p')
    else:
        # print(f'---------- "{s}"')
        # kludge for column 'j' which is in d/m/y order
        d = dt.strptime(s, '%d/%m/%Y')
    row[coln] = d.strftime('%Y-%m-%dT%H:%M:%SZ')


def fix_dates(row):
    # Warning: If changing columns, update fix1date() to get the month and day
    #          order right.
    for col in DATE_COLS:
        fix1date(row, col)


def main(infilename, outfilename):
    infile = open(infilename, newline='')
    reader = csv.reader(infile)
    outfile = open(outfilename, 'w', newline='')
    writer = csv.writer(outfile)
    line = next(reader)
    row1 = clean_row(line)  # first row
    line = next(reader)
    row2 = clean_row(line)  # second row
    header = build_header(row1)
    writer.writerow(header)  # new first row
    writer.writerow(row1)
    writer.writerow(row2)
    for line in reader:
        row = clean_row(line)
        fix_dates(row)
        writer.writerow(row)


if __name__ == '__main__':
    assert sys.version_info >= (3, 11)
    main(sys.argv[1], sys.argv[2])
