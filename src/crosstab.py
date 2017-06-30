# -*- coding: utf-8 -*-
"""
Input is a CSV file produced by SurveyMonkey. The creation method is:
1. Click on "Analyze Results".
2. Select the tab "Individual Responses".
3. Click on "Export All"
4. Select the dropdown "All response data".
5. Select the option ".XLS" (the leftmost option).
6. In "Data View", select "Original View".
7. In "Columns", select "Expanded".
8. In "Cells", select "Actual Answer Text".
9. Rename the file in the format yyyy-mm-dd_n.zip where n is the last survey in
   the export.

"""
import codecs
from collections import namedtuple, OrderedDict
from copy import deepcopy
import csv
import sys

from assign_nums import num_dict

CLEANED = "/Users/mlg/Downloads/hrm/evaluation/data_exports/2017-06-13/cleaned/all_exp_act.csv"

TO_COMPARE = {'q15':  # gender
              'q13'  # likely to recommend
              }
# qtext - the text name of the question, from row 2
# ans_dict - dictionary mapping the answer text to the count
Qdata = namedtuple('Qdata', 'qtext startcol limitcol ans_dict total'.split())


def make_qdata(qnum):
    """
    For the given question, return a Qdata namedtuple.
    The first entry is the text of the question.
    The second entry is a dict where the keys are the answer texts and
    the value is zero. This will be used to accumulate the counts.

    Obtain the answers by extracting all of the answers starting with the same
    column as the question and ending with the column before the next question.

    :param qnum: string like 'q1' or 'q22'
    """
    startcol = question_dict[qnum]
    qtext = question_text_row[startcol]
    limitcol = question_dict['q' + str(int(qnum[1:]) + 1)]
    ans_dict = OrderedDict([(answer_text_row[n], 0)
                            for n in range(startcol, limitcol)])
    qdata = Qdata(qtext, startcol, limitcol, ans_dict, 0)
    return qdata


def oneans(row, qdminor):
    """
    Iterate over the possible minor answers and increment the counter when
    they exist.
    :param row:
    :param qdminor: the Qdata for the minor question
    :return:
    """
    for anscol in range(qdminor.startcol, qdminor.limitcol):
        if row[anscol]:
            anstext = row[anscol]  # Male / Female
            qdminor.ans_dict[anstext] += 1


def onerow(row, qdmajor):
    """
    Iterate over the possible major answers. If an answer is present then
    iterate over its minor answers and increment each minor answer that is
    present.

    :param row:
    :param qdmajor: The current major question's Qdata
    :return:
    """
    for anscol in range(qdmajor.startcol, qdmajor.limitcol):
        if row[anscol]:
            anstext = row[anscol]  # Male / Female
            oneans(row, qdmajor.ans_dict[anstext])


def make_table(major, infile):
    """

    :param major:  the question for the left column, a string like "q4"
    :param infile:
    :return: this question's populated QData
    """
    global question_dict, question_text_row, answer_text_row
    reader = csv.reader(infile)
    question_row = next(reader)
    question_dict = num_dict(question_row)  # dict mapping q<n> -> column index
    question_text_row = next(reader)
    answer_text_row = next(reader)
    minor = TO_COMPARE[major]
    qdmajor = make_qdata(major)
    qdminor = make_qdata(minor)
    '''
        For each major answer, create a minor qdata and store it as the value
        of the major's answer dictionary, overwriting the zero that was created
        by make_qdata.
    '''
    for ans in qdmajor.ans_dict:
        qdmajor.ans_dict[ans] = deepcopy(qdminor)  # each answer gets its own
    for row in reader:
        onerow(row, qdmajor)
    return qdmajor


def main():
    for question in TO_COMPARE:
        with codecs.open(sys.argv[1], 'r', 'utf-8-sig') as infile:
            qtable = make_table(question, infile)
            print(qtable)

if __name__ == '__main__':
    question_dict, question_text_row, answer_text_row = None, None, None
    if sys.version_info.major < 3 or sys.version_info.minor < 6:
        raise ImportError('requires Python 3.6')
    # outfile = open(sys.argv[2], 'w', newline='')
    # writer = csv.writer(outfile)
    main()


