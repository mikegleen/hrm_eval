import datetime
import pandas as pd
import pandas.io.excel as ex
import sys

EXCEL_FILE = ('/Users/mlg/Downloads/hrm/surveymonkey/data_exports/cleaned/'
              + 'Data_All_Actual_2016-12-18/survey.xlsx')
E3 = ('/Users/mlg/Downloads/hrm/surveymonkey/data_exports/response/'
      + 'Data_All_Actual_2016-12-18/Excel/Sheet_1.xls')
SKIPROWS = 2
MANUAL_COLLECTOR = 94865372
FIELD_NAMES = 'respondent collector start_date end_date visit_date'


def round_to_minute(t):
    seconds = t.seconds % 60
    minutes = t.seconds // 60
    if seconds > 29:
        minutes += 1
    return datetime.timedelta(minutes=minutes)


def read_excel(excel_file):
    survey = ex.read_excel(excel_file, 'survey', header=None,
                           skiprows=SKIPROWS, parse_cols='A,B,C,D,J',
                           names=FIELD_NAMES.split())
    return survey


def main():
    pass
    s = read_excel(E3)

    s = s.dropna()
    s['diff'] = s.end_date-s.start_date
    s['r_diff'] = s['diff'].map(round_to_minute)
    ss = s[(s['diff'] < pd.Timedelta('02:24:00')) & (s['diff'] > pd.Timedelta('00:04:00'))]
    ss = ss[ss.collector != MANUAL_COLLECTOR]
    c = ss.groupby('r_diff').count()


if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    main()

