# -*- coding: utf-8 -*-
"""

Built from crosstab.py, adding aggregation. For example, "Your Age" can be
Under 16, 16-34, 35-54, 55-64, and 65 or over. We want to aggregate these
to 'under 55' and '55 and over'.

See crosstabs.py for how to create the input CSV file.

"""
import argparse
import codecs
from collections import namedtuple, OrderedDict
import csv
import sys

from assign_nums import SKIPCOLS

aggmap = namedtuple('aggmap', ('newcol', 'oldcols'))
qinfo = namedtuple('qinfo', ('ix', 'len'))
AGGLIST = [
    (15, [aggmap('Female', ('Female',)),
          aggmap('Male', ('Male',))]),
    (16, [aggmap('Under 55', ['Under 16', '16 - 34', '35 - 54']),
          aggmap('55 or over', ['55 - 64', '65 or over'])])
]
AGGDICT = OrderedDict(AGGLIST)
print(AGGDICT)


def trace(level, template, *arglist):
    if args.verbose >= level:
        print(template.format(*arglist))


def append_cols(newlist, oldlist, ix, length):
    for i in range(ix, ix + length):
        newlist.append(oldlist[i])


def get_question_dict(qrow):
    """
    :param qrow: The list of the first row returned from the CSV file which has
                 "q1", "q2", ... in question columns and "" otherwise.
    :return: OrderedDict mapping question number to a qinfo namedtuple of
            (offset, length) where length is the number of answers to each
            question
    """
    # qrow[i][1:] maps q21 -> 21
    # qnlist is [(1, index1), (2, index2), ...]
    qnlist = [(int(qrow[i][1:]), i) for i in range(SKIPCOLS, len(qrow))
              if qrow[i]]
    trace(2, 'qnlist: {}', qnlist)
    qndict = OrderedDict(qnlist)
    # qndict maps question number to zero-based column index
    lastq = list(qndict.keys())[-1]  # the last question number
    qndict[lastq + 1] = len(qrow)  # insert dummy question at end
    trace(2, 'qndict: {}', qndict)
    lir = list(enumerate(qndict.items()))
    # lir = [(0, (1, IX1)), (1, (2, IX2)), ... , (n, (n+1, IXn)]
    # where IXn is the n-th question's index in the row
    # print(lir)
    qdict = OrderedDict()
    for i, qix in lir[:-1]:  # iterate over all but the dummy last entry
        # qix is a tuple of (question number starting with 1,
        #     index in row starting with zero)
        # print(i, qix)
        # lir[i] == (i, (qn, ix))  qn: question #, ix: row index
        # lir[i][1] == (qn, ix)
        # lir[i][1][1] = ix
        # print(f'len = {lir[i + 1][1][1] - qix[1]}')
        anslen = lir[i + 1][1][1] - qix[1]
        qdict[qix[0]] = qinfo(ix=qix[1], len=anslen)
    return qdict


def inv_aggdict():
    """
    Convert AGGDICT to a dictionary where for each question the keys are the
    original column names and the values are the aggregate columns.
    :return:
    """
    invdict = OrderedDict()
    for q in AGGDICT:
        anslist = AGGDICT[q]  # the list of aggmap namedtuples for this question
        invmap = OrderedDict()
        for amap in anslist:
            for origcol in amap.oldcols:
                invmap[origcol] = amap.newcol
        invdict[q] = invmap
    trace(1, 'inverted agg dict: {}', invdict)
    return invdict


def new_q_row(qrow, qdict):
    """
    For each question, insert the question text followed by a number of empty
    columns. The number to insert is one less than either the number of answers
    in the input row or the number of aggregated answers.
    This is used for rows 1 and 2.
    :param qrow: The list as read from the CSV file
    :param qdict: The dictionary built by get_question_dict.
    :return: The list with the new aggregated columns
    """

    nqr = [qrow[i] for i in range(SKIPCOLS)]  # initialize to constant cols
    # If the question is to be aggregated, append the new columns to nqr and
    # skip to the next question. Otherwise, append the old columns.

    for question, qinf in qdict.items():
        ix = qinf.ix
        length = qinf.len
        trace(2, 'question {} len {}', question, length)
        if question in AGGDICT:
            length = len(AGGDICT[question])
            trace(2, ' in AGGDICT len {}', length)
        nqr.append(qrow[ix])
        nqr += [''] * (length - 1)
    return nqr


def new_ans_map(arow, qdict):
    """
    Process row #3 in the CSV file containing answer titles. Create a dict
    mapping original answer columns to aggregated answer columns. Later, when
    processing the data rows, we will copy non-empty original columns to the
    corresponding aggregated columns.
    :param arow: Third row of the CSV file
    :param qdict: The OrderedDict created by get_question_dict
    :return: dict for ea column, the corresponding aggregated answer if one
             exists.
    """
    amap = {}
    newarow = [arow[i] for i in range(SKIPCOLS)]  # initialize to constant cols
    for question, qinf in qdict.items():
        ix = qinf.ix
        length = qinf.len
        if question not in INV_AGGDICT:
            append_cols(newarow, arow, ix, length)
            continue
        oamap = INV_AGGDICT[question]  # orig ans -> agg ans
        agdict = AGGDICT[question]  # agg ans -> orig answers
        for qi in agdict:  # qi is a qinfo namedtuple
            newarow.append(qi.newcol)
        # Build a list of column offset -> agg column name
        for coln in range(ix, ix + length):
            old_ans = arow[coln]
            try:
                amap[coln] = oamap[old_ans]
            except KeyError:
                continue  # we will be ignoring this column
        trace(2, 'after question {} answers(len={}) {}', question, len(amap),
              amap)
    trace(1, 'answer map: {}', amap)
    return amap, newarow


def new_data_row(row, qdict, namap):
    """

    :param row: the next data row
    :param qdict: created by new_q_row
    :param namap: created by new_ans_map
    :return:
    """
    newrow = [row[i] for i in range(SKIPCOLS)]  # initialize to constant cols
    for question, qinf in qdict.items():
        ix = qinf.ix
        length = qinf.len
        if question not in INV_AGGDICT:
            append_cols(newrow, row, ix, length)
            continue
        for coln in range(ix, ix + length):
            try:
                newans = namap[coln]
            except KeyError:
                continue  # skip this column
    return newrow


def main():
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    q_row = next(reader)  # has values like q1,,,,q2,,,q3,,etc.
    trace(1, 'q_row(len {}): {}', len(q_row), q_row)
    q_dict = get_question_dict(q_row)
    # q_dict: question # -> (column index, length)
    nq_row = new_q_row(q_row, q_dict)
    trace(1, 'nq_row(len {}): {}', len(nq_row), nq_row)
    writer.writerow(nq_row)
    question_text_row = next(reader)
    nq_row2 = new_q_row(question_text_row, q_dict)
    trace(1, 'nq_row2(len {}): {}', len(nq_row2), nq_row2)
    writer.writerow(nq_row2)
    answer_text_row = next(reader)
    na_map, na_row = new_ans_map(answer_text_row, q_dict)
    writer.writerow(na_row)
    for row in reader:
        newrow = new_data_row(row, q_dict, na_map)
        writer.writerow(newrow)


def getargs():
    parser = argparse.ArgumentParser(
        description='''Copy a 'cleaned' CSV file, aggregating answers to
                    questions as specified by an internal configuration.
        ''')
    parser.add_argument('infile', help='''
         The CSV file that has been cleaned by extract_csv.sh''')
    parser.add_argument('outfile',
                        help='''output CSV file.
        ''')
    parser.add_argument('-v', '--verbose', default=1, type=int, help='''
    ''')
    _args = parser.parse_args()
    return _args


if __name__ == '__main__':
    if sys.version_info.major < 3 or sys.version_info.minor < 6:
        raise ImportError('requires Python 3.6')
    # invd = inv_aggdict()
    # print(invd)
    args = getargs()
    infile = codecs.open(sys.argv[1], 'r', 'utf-8-sig')
    outfile = codecs.open(sys.argv[2], 'w', 'utf-8-sig')
    INV_AGGDICT = inv_aggdict()
    main()
