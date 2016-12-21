import csv
import sys


def main():
    infile = open(sys.argv[1], newline='')
    reader = csv.reader(infile)

    n = 0
    for line in reader:
        n += 1
        print('{}: {}'.format(n, len(line)))

if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    main()

