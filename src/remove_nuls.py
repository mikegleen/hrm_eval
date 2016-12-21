import sys


def main():
    outfile = open(sys.argv[2], "wb")
    with open(sys.argv[1], "rb") as infile:
        byteline = infile.readline()
        n = 0
        while byteline != b'':
            n += 1
            cleanline = byteline.replace(b'\x00', b'')
            if cleanline != byteline:
                print('{}: {}->{}'.format(n, len(byteline), len(cleanline)))
            outfile.write(cleanline)
            byteline = infile.readline()

if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    main()

