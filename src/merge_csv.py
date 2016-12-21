import csv
import sys

# The number of columns in the 2nd file to skip
SKIPCOLS = 9


def main():
    infile1 = open(sys.argv[1], newline='')
    infile2 = open(sys.argv[2], newline='')
    outfile = open(sys.argv[3], 'w', newline='')
    reader1 = csv.reader(infile1)
    reader2 = csv.reader(infile2)
    writer = csv.writer(outfile)

    n = 0
    for line1 in reader1:
        n += 1
        try:
            line2 = next(reader2)
        except StopIteration:
            print('CSV file 2 is too short.')
        writer.writerow(line1 + line2[SKIPCOLS:])
    try:
        next(reader2)
        print('CSV file 1 is too short.')
    except StopIteration:
        pass

if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    main()


