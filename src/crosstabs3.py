"""

crosstabs3 - based on crosstabs2 plus multiple minor questions (across the top)
             and multiple major questions, one per page

Input is a CSV file produced by extract_csv.sh. The creation method is:
1. Click on "Analyze Results".
2. Step deleted.
3. Click on "Export All"
4. Select the dropdown "All response data".
5. Select the option ".XLS" (the leftmost option).
6. In "Data View", select "Original View".
7. In "Columns", select "Expanded".
8. In "Cells", select "Actual Answer Text".
9. Rename the file in the format yyyy-mm-dd_n.zip where n is the last survey in
   the export.
An input file might be:
    ~/Downloads/hrm/evaluation/data_exports/2017-11-05/cleaned/126.csv
or (via the symbolic link)
    ~/pyprj/hrm/evaluation/exports/2017-11-05/cleaned/126.csv
"""
import argparse
import codecs
from collections import OrderedDict
import csv
import sys
from openpyxl.styles import Font  # , Color, NamedStyle
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

from assign_nums import num_dict
from config import SKIPCOLS

TO_COMPARE = {'Q13':  # likely to recommend
              ('Q3',  # alone/with others
               'Q16')  # age
              }
TO_COMPARE = {'Q1':  # likely to recommend
              ('Q2',  # alone/with others
               'Q3')  # age
              }
QUESTIONS = ['Q' + n for n in '3,10,13,16,17,18,19'.split(',')]


class Qdata:

    def __init__(self, qnum):
        self.qnum = qnum
        self.startcol = q_dict[qnum]
        # For example, if our question is q13, limitcol is q14's column number.
        self.limitcol = q_dict['Q' + str(int(qnum[1:]) + 1)]
        # qtext - the text name of the question, from row 2
        self.qtext = question_text_row[self.startcol]

        # ans_dict - dictionary mapping the answer text to the count
        # For the major question, the values of the ans_dict are minor question
        # Qdata instances. Not used for the minor questions.

        # ans_count - dictionary mapping the answer text to the count
        # For the major question, the sum of the answers to the first minor
        # question. Since all of the minor questions have one and only one
        # answer, the totals will all be identical.

        self.ans_dict = OrderedDict([(answer_text_row[n], 0)
                                     for n in range(self.startcol,
                                                    self.limitcol)])
        self.ans_count = OrderedDict([(answer_text_row[n], 0)
                                     for n in range(self.startcol,
                                                    self.limitcol)])

        # minor_totals -
        self.minor_totals = 0  # will be populated for major question only
        self.total = 0  # valid responses
        self.base = 0  # all responses


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def validate_row(row, qdminor):
    """
    Iterate over the possible minor answers and return zero if they exist.
    :param row:
    :param qdminor: the Qdata for the minor question that corresponds to the
                    current major question's current answer
    :return: None if an answer is found, otherwise the question number (Qnn).
    """
    error = qdminor.qnum

    for anscol in range(qdminor.startcol, qdminor.limitcol):
        if row[anscol]:
            error = 0
            break
    return error


def oneanswer(row, qdminor):
    """
    Iterate over the possible minor answers and increment the counter when
    they exist.
    :param row:
    :param qdminor: the Qdata for the minor question that corresponds to the
                    current major question's current answer
    :return: None
    """
    for anscol in range(qdminor.startcol, qdminor.limitcol):
        if row[anscol]:
            trace(2, 'oneanswer: minor: {}, col: {}', qdminor.qnum, anscol)
            anstext = answer_text_row[anscol]  # minor answer
            qdminor.ans_count[anstext] += 1


def onerow(row, qdmajor):
    """
    Iterate over the possible major answers. If an answer is present then
    iterate over its minor answers and increment each minor answer that is
    present.

    :param row:
    :param qdmajor: The current major question's Qdata
    :return:
    """
    qdmajor.base += 1
    error = qdmajor.qnum  # error is in major question
    # First check that there is at least one answer to each minor question
    for anscol in range(qdmajor.startcol, qdmajor.limitcol):
        if row[anscol]:
            error = None  # found a major answer
            anstext = answer_text_row[anscol]  # Male / Female
            minordict = qdmajor.ans_dict[anstext]
            # For each of the minor questions, if any have no answers,
            # the row is invalid.
            for minorqdata in minordict.values():
                minorerror = validate_row(row, minorqdata)
                if minorerror:
                    error = minorerror
                    break
    if error:
        trace(2, '*****skipping row {} respondent {}, no response to {}',
              qdmajor.base, row[0], error)
        return

    for anscol in range(qdmajor.startcol, qdmajor.limitcol):
        trace(2, 'onerow: major: {}, col: {}', qdmajor.qnum, anscol)
        if row[anscol]:
            anstext = answer_text_row[anscol]  # Male / Female
            minordict = qdmajor.ans_dict[anstext]
            for minorqdata in minordict.values():
                oneanswer(row, minorqdata)


def make_major_qdata(major, infile):
    """
    :param major:  the question for the left column, a string like "q4"
    :param infile:
    :return: this question's populated major QData and the template minor
    Qdata which contains the minor question and answers and will be used to
    accumulate totals.
    """
    global q_dict, question_text_row, answer_text_row
    reader = csv.reader(infile)
    question_row = next(reader)  # has values like q1,,,,q2,,,q3,,etc.
    # Create a dict mapping Q<n> -> column index
    q_dict = num_dict(question_row, _args.skipcols)
    question_text_row = next(reader)
    answer_text_row = next(reader)
    minortuple = TO_COMPARE[major]
    qdmajor = Qdata(major)
    '''
        For each major answer, create a dict of minor qdata and store it as the
        value of the major's answer dictionary.
    '''
    for ans in qdmajor.ans_dict:
        qdmajor.ans_dict[ans] = {minor: Qdata(minor) for minor in minortuple}
    # Create a dictionary of dictionaries where the outer dictionary is keyed
    # by the minor questions and the inner dictionaries are each keyed by the
    # respective minor questions answers.
    qdmajor.minor_totals = {}
    for minor in minortuple:
        minorqd = Qdata(minor)
        qdmajor.minor_totals[minor] = {ans: 0 for ans in minorqd.ans_dict}
    for row in reader:
        onerow(row, qdmajor)
    return qdmajor


def count_answers(major_qdata):
    for majans in major_qdata.ans_dict:
        totflag = True  # only take totals for first minor question
        trace(2, 'in count_answers, majans = {}', majans)
        minor_qdata_dict = major_qdata.ans_dict[majans]
        for minq in minor_qdata_dict.values():
            trace(2, 'minor question: {}', minq.qtext)
            for ans in minq.ans_count:
                trace(2, r'ans: "{}" ({})', ans, minq.ans_count[ans])
                minq.total += minq.ans_count[ans]
            trace(2, 'in count_answers, minq.total = {}', minq.total)
            if totflag:
                major_qdata.ans_count[majans] += minq.total
                major_qdata.total += minq.total
                totflag = False
    minq_tuple = TO_COMPARE[major_qdata.qnum]
    for minq in minq_tuple:
        globalmin = major_qdata.minor_totals[minq]
        # accumulate minor answers across all major answers
        for majans in major_qdata.ans_dict:  # iterate over major answers
            minor_qdata_dict = major_qdata.ans_dict[majans]  # minor Qdata
            minqdata = minor_qdata_dict[minq]
            for minans in minqdata.ans_count:  # iterate over minor answers
                globalmin[minans] += minqdata.ans_count[minans]


def create_sheet(major_qdata, minor_qdata):
    j = major_qdata
    ws = workbook.create_sheet(major_qdata.qnum)
    title = f'{j.qnum.upper()}: {j.qtext.upper()}'
    a1 = ws.cell(row=1, column=1, value=title)
    a2 = ws.cell(row=2, column=1, value='BASE: ALL RESPONDENTS')
    a3 = ws.cell(row=5, column=1, value='BASE')
    b3 = ws.cell(row=5, column=2, value=j.base)
    b6 = ws.cell(row=6, column=2, value=1.0)  # 100%
    ws.cell(row=7, column=1, value='VALID RESPONSES')
    b7 = ws.cell(row=7, column=2, value=j.total)
    b8 = ws.cell(row=8, column=2, value=j.total / j.base)
    txt = f'{minor_qdata.qnum.upper()}: {minor_qdata.qtext.upper()}'
    c3 = ws.cell(row=3, column=3, value=txt)
    # Populate the minor answer names
    coln = 2  # start with column 3
    for ans in minor_qdata.ans_dict:
        coln += 1
        ws.cell(row=4, column=coln, value=ans)
        # ws.cell(row=6, column=coln, value=1.0).style = 'Percent'
        ws.column_dimensions[get_column_letter(coln)].width = len(ans) * 1.20
    a1.font = Font(bold=True)
    a2.font = Font(bold=True)
    a3.font = Font(bold=True)
    b3.font = Font(bold=True)
    b7.font = Font(bold=True)
    c3.font = Font(bold=True)
    b6.style = 'Percent'
    b8.style = 'Percent'
    # Set the column width of the first column
    colw = 0
    for q in j.ans_dict:
        w = len(q)
        if w > colw:
            colw = w
    ws.column_dimensions['A'].width = colw * 1.10
    # Populate the minor answer totals
    globalans = minor_qdata.ans_dict
    col = 2  # 1st col = 3
    for minans in globalans:
        col += 1
        c = ws.cell(row=7, column=col, value=globalans[minans])
        c.font = Font(bold=True)
        c = ws.cell(row=8, column=col,
                    value=globalans[minans] / j.total)
        c.style = 'Percent'
    # For each major answer, populate the corresponding minor answers
    rownum = 7
    for majans in j.ans_dict:  # iterate over the major answers
        rownum += 3
        ws.cell(row=rownum, column=1, value=majans)
        minqd = j.ans_dict[majans]
        c = ws.cell(row=rownum, column=2, value=minqd.total)
        c.font = Font(bold=True)
        c = ws.cell(row=rownum + 1, column=2, value=minqd.total / j.total)
        c.style = 'Percent'
        col = 2
        for minans in minqd.ans_dict:
            col += 1
            c = ws.cell(row=rownum, column=col, value=minqd.ans_dict[minans])
            c.font = Font(bold=True)
            if minqd.total:
                c = ws.cell(row=rownum + 1, column=col,
                            value=minqd.ans_dict[minans] / globalans[minans])
                c.style = 'Percent'
            else:
                ws.cell(row=rownum + 1, column=col, value='NaN')
    ws.column_dimensions['A'].width = 20


def main():
    global workbook
    workbook = Workbook()
    del workbook[workbook.sheetnames[0]]  # remove the default sheet
    for question in TO_COMPARE:
        with codecs.open(sys.argv[1], 'r', 'utf-8-sig') as infile:
            major_qdata = make_major_qdata(question, infile)
            # print('major_qdata:')
            # print(major_qdata)
            print("Major question:", major_qdata.qtext)
            # print("Minor question:", minor_qdata_list)
            count_answers(major_qdata)
            create_sheet(major_qdata)
            print('Major Qdata total', major_qdata.total)
    workbook.save(sys.argv[2])


def getargs():
    parser = argparse.ArgumentParser(
        description='''
        Create a crosstabs xlsx file.
        ''')
    parser.add_argument('infile', help='''
         The CSV file that has been cleaned by extract_csv.sh''')
    parser.add_argument('outfile',
                        help='''output XLSX file.
        ''')
    parser.add_argument('-j', '--major', help='''Not implemented yet.''')
    parser.add_argument('-m', '--multiple', action='store_true', help='''
    Specifies whether the minor question may have multiple (or no) answers. If
    not specified, exactly one minor answer must be selected.''')
    parser.add_argument('-n', '--minor', help='''Not implemented yet.''')
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
    if sys.version_info.major < 3 or sys.version_info.minor < 6:
        raise ImportError('requires Python 3.6')
    # q_dict, question_text_row, answer_text_row = None, None, None
    _args = getargs()
    main()
    print('End crosstabs3.')
