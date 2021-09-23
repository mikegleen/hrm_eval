"""
    split.py - Split one question into multiple questions.

    This is for the case where a question contains sub-questions in an
    identical format. For example:

    How would you rate the following?
    Ticket / booking experience - Not applicable / Don't know
    Ticket / booking experience - Poor
    Ticket / booking experience - Neither Good nor Poor
    Ticket / booking experience - Good
    Getting to the Museum (inc. parking) - Not applicable / Don't know
    etc.

    We take everything up the the string " - " to be the sub-question. Each
    sub-question is converted to a full question with numbers consisting of
    the original question number * 100 plus the sub-question index based on 1
    and append it to the right of the existing columns. So question q9 might
    be converted to q901, q902, etc.

    The new questions will occupy the same columns as the previous compound
    question.

"""

import argparse
import codecs
from collections import namedtuple, OrderedDict
import csv
import re
import sys

from config import SKIPCOLS

SPLIT_QUESTIONS = ('q9', )
splitpat = re.compile(r'(.*) - (.*)')
Qinfo = namedtuple('Qinfo', ('ix', 'len'))


def trace(level, template, *arglist):
    if args.verbose >= level:
        print(template.format(*arglist))


def get_question_dict(qrow):
    """
    :param qrow: The list of the first row returned from the CSV file which has
                 "q1", "q2", ... in question columns and "" otherwise.
    :return: OrderedDict mapping question number to a Qinfo namedtuple of
            (offset, length) where length is the number of answers to each
            question
    """
    # qnlist is [('q1', index1), ('q2', index2), ...]
    qnlist = [(qrow[i], i) for i in range(SKIPCOLS, len(qrow))
              if qrow[i]]
    qnlist.append(('qx', len(qrow)))  # append dummy entry
    trace(2, 'qnlist: {}', qnlist)
    qdict = OrderedDict()
    for i, tup in enumerate(qnlist[:-1]):  # tup is (q1, index1)
        limit = qnlist[i + 1][1]  # next question's column
        qdict[tup[0]] = Qinfo(tup[1], limit - tup[1])
    return qdict


def split_question(q, r1, r2, r3, qdict):
    """

    :param q: the question, like 'q9'
    :param r1: question number row (list of strings)
    :param r2: question text row
    :param r3: answer row
    :param qdict: dict mapping question -> Qinfo(ix, len)
    :return:
    """
    startcol = qdict[q].ix
    limit = startcol + qdict[q].len  # 1st column of next question

    oldq = ''
    subqnum = 0
    for col in range(startcol, limit):
        m = splitpat.match(r3[col])
        if m is None:
            trace(1, 'No match on question {}, col {}: "{}"', q, col, r3[col])
            return
        newq = m.group(1)
        r3[col] = m.group(2)  # the new answer
        if newq != oldq:
            oldq = newq
            subqnum += 1
            r1[col] = f'q{q[1:]}.{subqnum:02}'
            r2[col] = newq
    return None


def main():
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # row 1: has values like q1,,,,q2,,,q3,,etc.
    q_row = next(reader)
    trace(2, 'q_row(len {}): {}', len(q_row), q_row)
    # row 2: contains question text in cols under question #'s
    question_text_row = next(reader)
    # row 3: contains question answers
    answer_text_row = next(reader)

    # question_dict: question # -> (column index, length)
    question_dict = get_question_dict(q_row)

    nq_row = q_row[:]
    nq_row2 = question_text_row[:]
    na_row = answer_text_row[:]
    for question in question_dict:
        if question in SPLIT_QUESTIONS:
            split_question(question, nq_row, nq_row2, na_row, question_dict)
    trace(2, 'nq_row(len {}): {}', len(nq_row), nq_row)
    writer.writerow(nq_row)

    trace(2, 'nq_row2(len {}): {}', len(nq_row2), nq_row2)
    writer.writerow(nq_row2)

    writer.writerow(na_row)  # write row 3 with the aggregated answers

    # rows 4-n: the survey records
    for row in reader:
        writer.writerow(row)


def getargs():
    parser = argparse.ArgumentParser(
        description='''Copy a 'cleaned' CSV file, splitting questions into
                      multiple sub-questions as specified by an internal
                      configuration. This should precede the aggregation step.
        ''')
    parser.add_argument('infile', help='''
         The CSV file that has been cleaned by extract_csv.sh''')
    parser.add_argument('outfile',
                        help='''output CSV file.
        ''')
    parser.add_argument('-v', '--verbose', default=1, type=int, help='''
                        Control verbosity.''')
    _args = parser.parse_args()
    return _args


if __name__ == '__main__':
    assert sys.version_info >= (3, 6)
    args = getargs()
    infile = codecs.open(args.infile, 'r', 'utf-8-sig')
    outfile = codecs.open(args.outfile, 'w', 'utf-8-sig')
    main()
    print('End split.')
