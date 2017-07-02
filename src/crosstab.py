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
from collections import OrderedDict
from copy import deepcopy
import csv
import sys
from openpyxl.styles import colors
from openpyxl.styles import Font, Color, NamedStyle
from openpyxl import Workbook

from assign_nums import num_dict

CLEANED = "/Users/mlg/Downloads/hrm/evaluation/data_exports/2017-06-13/cleaned/all_exp_act.csv"

TO_COMPARE = {'q15':  # gender
              'q13'  # likely to recommend
              }
# qtext - the text name of the question, from row 2
# ans_dict - dictionary mapping the answer text to the count


class Qdata:

    def __init__(self, qnum, qtext, startcol, limitcol, ans_dict):
        self.qnum = qnum
        self.qtext = qtext
        self.startcol = startcol
        self.limitcol = limitcol
        '''
        For the major question, the values of the ans_dict are minor question
        Qdata instances. For the minor questions, the values are integers
        containing the counts of occurences.
        '''
        self.ans_dict = ans_dict
        self.total = 0


def make_qdata(qnum):
    """
    For the given question, return a Qdata instance.
    The first entry is the text of the question.
    The second entry is a dict where the keys are the answer texts and
    the value is zero. This will be used to accumulate the counts.

    Obtain the answers by extracting all of the answers starting with the same
    column as the question and ending with the column before the next question.

    :param qnum: string like 'q1' or 'q22'
    """
    startcol = question_dict[qnum]
    qtext = question_text_row[startcol]
    # For example, if our question is q13, limitcol is q14's column number.
    limitcol = question_dict['q' + str(int(qnum[1:]) + 1)]
    ans_dict = OrderedDict([(answer_text_row[n], 0)
                            for n in range(startcol, limitcol)])
    qdata = Qdata(qnum, qtext, startcol, limitcol, ans_dict)
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


def make_major_qdata(major, infile):
    """

    :param major:  the question for the left column, a string like "q4"
    :param infile:
    :return: this question's populated major QData and the template minor
    Qdata which contains the minor question and answers and is more convenient
    to use than digging the minor info out of the major structure.
    """
    global question_dict, question_text_row, answer_text_row
    reader = csv.reader(infile)
    question_row = next(reader)  # has values like q1,,,,q2,,,q3,,etc.
    question_dict = num_dict(question_row)  # dict mapping q<n> -> column index
    question_text_row = next(reader)
    answer_text_row = next(reader)
    minor = TO_COMPARE[major]
    qdmajor = make_qdata(major)
    qdminor = make_qdata(minor)  # minor qdata template
    '''
        For each major answer, create a minor qdata and store it as the value
        of the major's answer dictionary, overwriting the zero that was created
        by make_qdata.
    '''
    for ans in qdmajor.ans_dict:
        qdmajor.ans_dict[ans] = deepcopy(qdminor)  # each answer gets its own
    for row in reader:
        onerow(row, qdmajor)
    return qdmajor, qdminor


def count_answers(major_qdata):
    for major_answer in major_qdata.ans_dict:
        print(major_answer)
        minor_qdata = major_qdata.ans_dict[major_answer]
        print(minor_qdata.qtext)
        for ans in minor_qdata.ans_dict:
            print(ans, minor_qdata.ans_dict[ans])
            minor_qdata.total += minor_qdata.ans_dict[ans]
        print(minor_qdata.total)
        major_qdata.total += minor_qdata.total


def create_xlsx(major_qdata, minor_qdata):
    wb = Workbook()
    ws = wb.active
    title = f'{major_qdata.qnum.upper()}: {major_qdata.qtext}'
    ws.cell(row=1, column=1, value=title)
    a3 = ws.cell(row=3, column=1, value='BASE')
    a3.font = Font(bold=True)
    wb.save(sys.argv[2])


def main():
    for question in TO_COMPARE:
        with codecs.open(sys.argv[1], 'r', 'utf-8-sig') as infile:
            major_qdata, minor_qdata = make_major_qdata(question, infile)
            # print('major_qdata:')
            # print(major_qdata)
            print("Major question:", major_qdata.qtext)
            print("Minor question:", minor_qdata.qtext)
            count_answers(major_qdata)
            create_xlsx(major_qdata, minor_qdata)
            print('Major Qdata total', major_qdata.total)


if __name__ == '__main__':
    question_dict, question_text_row, answer_text_row = None, None, None
    if sys.version_info.major < 3 or sys.version_info.minor < 6:
        raise ImportError('requires Python 3.6')
    main()


