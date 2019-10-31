# -*- coding: utf-8 -*-
"""

Aggregate CSV columns. For example, "Your Age" can be
Under 16, 16-34, 35-54, 55-64, and 65 or over. We want to aggregate these
to 'under 55' and '55 and over'.

Input is the cleaned file produced by extract_csv.sh.

Processing depends upon the three header rows:
Row 1. Text q[n] where n is the question number in the first column
   corresponding to the Nth question
Row 2. In the column where a q[n] appears in row 1, row 2 contains the name of
   the question.
Row 3. Each column associated with a question contains a possible answer.

See crosstabs.py for how to create the input CSV file.

TODO:
In AGGLIST, if an 'oldcols' entry has a leading asterisk, there will be no
existing column of that name but it should be created, meaning that it will
count when no responses are selected. This must be the last column defined.
"""
import argparse
import codecs
from collections import namedtuple, OrderedDict
import csv
import sys

from config import SKIPCOLS

Aggmap = namedtuple('Aggmap', ('newcol', 'oldcols'))
Qinfo = namedtuple('Qinfo', ('ix', 'len'))
AGGLIST = [
    ('q10', [Aggmap('Not very', ('- very unsatisfied', '- 2', '- 3', '- 4',
                                 '- 5')),
             Aggmap('Quite', ('- satisfied', '- 7', '- 8')),
             Aggmap('Very', ('- 9', '- extremely satisfied'))
          ]),
    ('q13', [Aggmap('Not very', ('Very unlikely', 'Unlikely',
                                 'Neither likely nor unlikely')),
             Aggmap('Likely', ('Likely', 'Very likely'))
          ]),
    ('q15', [Aggmap('Female', ('Female',)),
             Aggmap('Male', ('Male',))
          ]),
    ('q16', [Aggmap('Under 55', ('Under 16', '16 - 34', '35 - 54')),
             Aggmap('55 or over', ('55 - 64', '65 or over'))
          ]),
    ('q17', [Aggmap('Not disabled', ('No',)),
             Aggmap('Disabled', ('Yes, limited a little', 'Yes, limited a lot')),
          ]),
    ('q18', [Aggmap('White British',
                 ('White - British (English/Scottish/Welsh/Northern Irish)',)),
             Aggmap('Other', ('White - Irish', 'other White', 'Indian',
                              'Pakistani', 'Bangladeshi', 'Chinese',
                              'other Asian background', 'Black African',
                              'Black Caribbean', 'other Black background',
                              'Middle Eastern / Iraqi / Iranian',
                              'Arab', 'Mixed / Multiple ethnic group(s)',
                              'other ethnicity'))
          ]),
    ('q19', [Aggmap('Harrow', ('Harrow borough',)),
             Aggmap('Other London', ('other London borough',)),
             Aggmap('Elsewhere', ('elsewhere in UK', 'Not in UK')),
          ]),
]
# All of the mappings for the sub-questions of question 9 are identical.
AGGMAP9 = [Aggmap('not good', ('Very Poor', 'Poor', 'Neither Good nor Poor')),
           Aggmap('good', ('Good', 'Very Good'))
           ]
# The format string will produce keys 'q9.01' .. 'q9.17'
AGGLIST9 = [(f'q{qn / 100:.02f}', AGGMAP9) for qn in range(901, 917)]
AGGDICT = OrderedDict(AGGLIST + AGGLIST9)


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


def inv_aggdict():
    """
    Convert AGGDICT to a dictionary of dictionaries where for each question the
    keys are the original column names and the values are the aggregate column
    names. For example, assuming we have only question 16 where AGGLIST has:

        ('q16', [Aggmap('Under 55', ('Under 16', '16 - 34', '35 - 54')),
              Aggmap('55 or over', ('55 - 64', '65 or over'))
              ]),

    INV_AGGDICT will be:

    {'q16': {
            'Under 16': 'Under 55',
            '16 - 34': 'Under 55',
            '35 - 54': 'Under 55',
            '55 - 64': '55 or over',
            '65 or over': '55 or over'
        }
    }
    :return: The inverted dictionary
    """
    invdict = OrderedDict()
    for q in AGGDICT:
        # anslist is the list of Aggmap namedtuples for this question
        anslist = AGGDICT[q]
        invmap = OrderedDict()
        for amap in anslist:
            for origcol in amap.oldcols:
                invmap[origcol.strip()] = amap.newcol.strip()
        invdict[q] = invmap
    trace(2, 'inverted agg dict: {}', invdict)
    return invdict


def get_question_row(qrow, qdict):
    """
    This is used for rows 1 and 2.
    For each question, insert the question text followed by a number of empty
    columns. The number to insert is one less than either the number of answers
    in the input row or the number of aggregated answers.
    :param qrow: Row 1 or 2 as read from the CSV file
    :param qdict: The dictionary built by get_question_dict.
    :return: The list with the new aggregated columns
    """

    nqr = [qrow[i] for i in range(SKIPCOLS)]  # initialize to constant cols

    # If the question is to be aggregated, append the new columns to nqr and
    # skip to the next question. Otherwise, append the old columns.

    for question, qinfo in qdict.items():
        ix = qinfo.ix
        length = qinfo.len
        trace(2, 'question {} len {}', question, length)
        if question in AGGDICT:
            length = len(AGGDICT[question])
            trace(2, ' in AGGDICT len {}', length)
        nqr.append(qrow[ix])
        nqr += [''] * (length - 1)
    return nqr


def new_ans_map(ansrow, qdict):
    """
    Process row #3 in the CSV file containing answer titles. Create a dict
    mapping original answer columns to aggregated answer columns. Later, when
    processing the data rows, we will copy non-empty original columns to the
    corresponding aggregated columns.
    :param ansrow: Third row of the CSV file
    :param qdict: The OrderedDict created by get_question_dict
    :return: dict for ea column, the corresponding aggregated answer if one
             exists.
    """
    amap = {}
    newarow = [ansrow[i] for i in range(SKIPCOLS)]  # initialize to constants
    for question, qinf in qdict.items():
        ix = qinf.ix
        length = qinf.len
        if question not in INV_AGGDICT:
            # just copy the original questions
            newarow += ansrow[ix:ix + length]
            continue
        oamap = INV_AGGDICT[question]  # orig ans -> agg ans
        agdict = AGGDICT[question]  # agg ans -> orig answers
        for am in agdict:  # qi is an Aggmap namedtuple
            newarow.append(am.newcol)
        # Build a dict of original column offset -> agg column name. amap will
        # only have entries for answers to questions being aggregated.
        for coln in range(ix, ix + length):
            old_ans = ansrow[coln].strip()
            try:
                amap[coln] = oamap[old_ans]
            except KeyError:
                continue  # we will be ignoring this column
        trace(3, 'after question {} answers(len={}) {}', question, len(amap),
              amap)
    trace(2, 'answer map: {}', amap)
    return amap, newarow


def new_data_row(row, qdict, namap):
    """

    :param row: the next data row
    :param qdict: created by get_question_row
    :param namap: created by new_ans_map
    :return: the newly constructed row with aggregated answers
    """
    newrow = [row[i] for i in range(SKIPCOLS)]  # initialize to constant cols
    for question, qinf in qdict.items():
        ix = qinf.ix
        length = qinf.len
        if question not in AGGDICT:
            newrow += row[ix:ix + length]
            continue
        aggd = AGGDICT[question]
        nansdict = OrderedDict([(ad.newcol, '') for ad in aggd])
        trace(3, 'nansdict: {}', nansdict)
        for coln in range(ix, ix + length):
            try:
                newans = namap[coln]
            except KeyError:
                # This column in the original file is being dropped - it does
                # not have an entry in this question's Aggmap.
                continue  # skip this column
            if row[coln]:
                # Insert the original answer, not the aggregated answer. So, if
                # the aggregated answer is '55 or over', the value might be
                # '55 - 64' or '65 or over'.
                nansdict[newans] = row[coln]
        newrow += nansdict.values()
    return newrow


def check_1_answer(qnum, agmlist, row3):
    """

    :param qnum: the question number
    :param agmlist: the list of Aggmaps for this question
    :param row3: the slice of row3 for this question
    :return: None
    """
    # build a set of answers in the config
    orig_answers = set()
    for aggmap in agmlist:
        for ans in aggmap.oldcols:
            if ans in orig_answers:
                trace(1, 'Q{}: duplicate answer: {}', qnum, ans)
            else:
                orig_answers.add(ans)
    trace(2, 'cfg orig: {}', orig_answers)
    # Now we have a set of the original answers from the config and a list of
    # the answer names from the CSV file for this question in row3.
    #
    for cell in [r.strip() for r in row3]:
        if cell in orig_answers:
            orig_answers.remove(cell)
        else:
            # An ignored answer is one that is in the CSV file but is not
            # aggregated. This may be intended.
            trace(1, '    Q{}: ignored answer: "{}"', qnum, cell)
    #
    # Check for leftover answers in the config file
    for answer in orig_answers:
        trace(1, '    Q{}: unused answer: "{}"', qnum, answer)


def check_answers(question_dict, answer_text_row):
    """
    Display diagnostics for inconsistencies between the configuration and the
    data in the spreadsheet.

    :param question_dict: question # -> (column index, length)
    :param answer_text_row: row 3 of the CSV file
    :return:
    """
    for qn, agmlist in AGGDICT.items():  # agmlist is a list of Aggmap items.
        qinfo = question_dict[qn]
        ix = qinfo.ix
        length = qinfo.len
        trace(1, 'Checking answer {}, ix = {}, length = {}.', qn, ix, length)
        check_1_answer(qn, agmlist, answer_text_row[ix:ix + length])


def main():
    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    # row 1: has values like q1,,,,q2,,,q3,,etc.
    q_row = next(reader)
    trace(2, 'q_row(len {}): {}', len(q_row), q_row)
    # question_dict: question # -> (column index, length)
    question_dict = get_question_dict(q_row)
    nq_row = get_question_row(q_row, question_dict)
    trace(2, 'nq_row(len {}): {}', len(nq_row), nq_row)
    writer.writerow(nq_row)

    # row 2: contains question text in cols under question #'s
    question_text_row = next(reader)
    nq_row2 = get_question_row(question_text_row, question_dict)
    trace(2, 'nq_row2(len {}): {}', len(nq_row2), nq_row2)
    writer.writerow(nq_row2)

    # row 3: contains question answers
    answer_text_row = next(reader)
    if args.check:
        check_answers(question_dict, answer_text_row)
    na_map, na_row = new_ans_map(answer_text_row, question_dict)
    writer.writerow(na_row)  # write row 3 with the aggregated answers

    # rows 4-n: the survey records
    for row in reader:
        newrow = new_data_row(row, question_dict, na_map)
        writer.writerow(newrow)


def getargs():
    parser = argparse.ArgumentParser(
        description='''Copy a 'cleaned' CSV file, aggregating answers to
                    questions as specified by an internal configuration.
        ''')
    parser.add_argument('-c', '--check', action='store_true',
                        help='''Check that the aggregation configuration
                        matches the CSV file.
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
    if sys.version_info.major < 3 or sys.version_info.minor < 6:
        raise ImportError('requires Python 3.6')
    args = getargs()
    infile = codecs.open(args.infile, 'r', 'utf-8-sig')
    outfile = codecs.open(args.outfile, 'w', 'utf-8-sig')
    INV_AGGDICT = inv_aggdict()
    main()
    print('End aggregate.')
