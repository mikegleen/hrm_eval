"""
    Remove HTML tags from the first two rows in a CSV file.

    Assign question numbers. In the input file, questions start at column 10
    (column 9 if zero based). Only non-empty cells are counted.
"""

import csv
import sys
from bs4 import BeautifulSoup as Bs

FIXED_HEADER = 'RespondentID,CollectorID,StartDate,EndDate,IP Address,'
FIXED_HEADER += 'Email Address,First Name,LastName,Custom Data'
FIXED_HEADER = FIXED_HEADER.replace(' ', '').lower().split(',')
SKIPCOLS = len(FIXED_HEADER)


def build_header(row):
    header = FIXED_HEADER
    q_num = 0
    for cell in row[SKIPCOLS:]:
        if cell:
            q_num += 1
            header.append('q{}'.format(q_num))
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
        # print('{}: {}-->{}'.format(n, cell, text))
        row.append(text)
    return row


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
        writer.writerow(row)


if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    main(sys.argv[1], sys.argv[2])
