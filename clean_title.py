import csv
import sys
from bs4 import BeautifulSoup as Bs


def clean_row(dirtyrow):
    n = 0
    row = []
    for cell in dirtyrow:
        n += 1
        soup = Bs(cell, 'html.parser')
        text = soup.get_text()
        print('{}: {}-->{}'.format(n, cell, text))
        row.append(text)
    return row


def main():
    infile = open(sys.argv[1], newline='')
    reader = csv.reader(infile)
    outfile = open(sys.argv[2], 'w', newline='')
    writer = csv.writer(outfile)
    line = next(reader)
    row = clean_row(line)  # first row
    writer.writerow(row)
    line = next(reader)
    row = clean_row(line)  # second row
    writer.writerow(row)
    for line in reader:
        row = clean_row(line)
        writer.writerow(row)


if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    main()
