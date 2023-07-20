# -*- coding: utf-8 -*-
"""

"""
from argparse import ArgumentParser
import codecs
import csv
import sys
import textwrap

from assign_nums import num_dict
from config import SKIPCOLS

COLS = ['Q11',  # positive comments
        'Q12',  # anything that could be improved
       ]
DATE_COL = 9
ENDDATE_COL = 3  # value to be used if DATE_COL is empty


def put(txt):
    print(txt, file=outfile)


def put_html_header():
    header = '''\
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Museum Comments</title>
      <style>
          table, th, td {
            border: 1px solid black;
            border-collapse: collapse;
            }
          th {
              text-align: center;
              padding: 15px;
             }
          td {
              padding: 15px;
              text-align: left;
            }
      </style>
    </head>
    <body>
    <table>
    <tr>
    <th style="width:20%">Date</th>
    <th style="width:40%">Positive Comments</th>
    <th style="width:40%">Can Be Improved</th>
    </tr>
    '''
    put(textwrap.dedent(header))


def put_html_footer():
    footer = '''\
    </body>
    </html>
    '''
    put(textwrap.dedent(footer))


def put_html_row(outlist):
    put('<tr>')
    for td in outlist:
        put(f'<td>{td}</td>')
    put('</tr>')


def main():
    reader = csv.reader(infile)
    writer = None  # avoid compiler warning
    if _args.html:
        put_html_header()
    else:
        writer = csv.writer(outfile)
    question_row = next(reader)  # has values like q1,,,,q2,,,q3,,etc.
    # Create a dict mapping Q<minor> -> column index
    q_dict: dict = num_dict(question_row, _args.skipcols)
    # print (q_dict)
    next(reader)  # question_text_row
    next(reader)  # answer_text_row

    for row in reader:
        outrow = []
        rowdate = row[DATE_COL] if row[DATE_COL] else row[ENDDATE_COL]
        outrow.append(rowdate[:10])  # yyyy-mm-dd
        for col in COLS:
            outrow.append(row[q_dict[col]])
        if _args.html:
            put_html_row(outrow)
        else:
            writer.writerow(outrow)


def getargs():
    parser: ArgumentParser = ArgumentParser(
        description='''
        For each row, output only the columns specified.
        ''')
    parser.add_argument('infile', help='''
         The input CSV file.''')
    parser.add_argument('outfile', help='''
         The output CSV or HTML file''')
    parser.add_argument('-c', '--cols',
                        help='''json file of columns to select.
        ''')
    parser.add_argument('--html', action='store_true',
                        help='''If selected, output will be in html format.
        ''')
    parser.add_argument('-s', '--skipcols', type=int, default=SKIPCOLS,
                        help=f'''Number of columns to ignore before extracting
                        the column numbers for defined questions. Default is
                        {SKIPCOLS}.''')
    parser.add_argument('-v', '--verbose', default=1, type=int, help='''
    Modify verbosity.
    ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 7)
    _args = getargs()
    infile = codecs.open(_args.infile, 'r', 'utf-8-sig')
    outfile = open(_args.outfile, 'w', encoding='utf-8-sig', newline=None if
                   _args.html else '')
    main()
    print('End select_cols.')
