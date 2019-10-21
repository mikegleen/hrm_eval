"""
    Assign question numbers. In the input file, questions start at column 10
    (column 9 if zero based). Only non-empty cells are counted.
"""
import csv
import sys
from config import SKIPCOLS


def assign_numbers(row, skipcols=SKIPCOLS):
    """
        Input is the first row returned from the original CSV file.
        From the list containing Qnn entries in the corresponding columns,
        build a list containing 'Qnn' where there was question text and
        a zero-length string otherwise.
    """
    nums = ['' for n in range(skipcols)]
    q_num = 0
    for cell in row[skipcols:]:
        if cell:
            q_num += 1
            nums.append(f'Q{q_num}')
        else:
            nums.append('')
    return nums


def num_dict(row, skipcols=SKIPCOLS) -> dict:
    """
        Input is the first row returned from the modified CSV file where the
        first row now contains cells with qnn where the questions begin.
        From the list containing Qnn entries in the corresponding columns,
        build a dictionary mapping <question #> -> <zero based column #>.
    """
    en = enumerate(row[skipcols:])
    # print(list(en))
    nd = {t[1].upper(): t[0] + skipcols for t in en if t[1]}
    return nd


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
