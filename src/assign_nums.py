"""
    Assign question numbers. In the input file, questions start at column 10
    (column 9 if zero based). Only non-empty cells are counted.
"""

import csv
import sys

SKIPCOLS = 9


def assign_numbers(row):
    nums = ['' for n in range(SKIPCOLS)]
    q_num = 0
    for cell in row[SKIPCOLS:]:
        if cell:
            q_num += 1
            nums.append('Q{}'.format(q_num))
        else:
            nums.append('')
    return nums


def main():
    infile = open(sys.argv[1], newline='')
    reader = csv.reader(infile)
    outfile = open(sys.argv[2], 'w', newline='')
    writer = csv.writer(outfile)
    row = next(reader)
    nums = assign_numbers(row)
    writer.writerow(nums)
    writer.writerow(row)
    for row in reader:
        writer.writerow(row)


if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    main()
