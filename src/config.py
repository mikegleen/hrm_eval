"""
Configuration file for processing SurveyMonkey CSV files.

This configuration assumes that the CSV file has been cleaned up by
get_response.sh which adds a row at the top containing the question numbers and
merges multiple CSV files into a single spreadsheet.

To use the unmodified export from SurveyMonkey, change skiprows to 2 and adjust
the column numbers accordingly.

"""
from excel_cols import col2num

SHORTSURVEY = True
DEBUGMODE = False  # If True, create abbreviated lists
SKIPCOLS = 9
SKIPROWS = 3

if not SHORTSURVEY:
    # updated 2017-02-18:
    # noinspection PyRedeclaration
    DEFCOL = {
        'postcode': 'IJ',
        'want_newsletter': 'KE',
        'want_notify': 'KF',
        'volunteer': 'KG',
        'email_addr': 'KK',
    }
    defcol = {dc: col2num(DEFCOL[dc]) for dc in DEFCOL}

    # begin crosstab definitions
    CROSSTAB_TITLES = {'Q3': 'Visiting w. others',
                       # 'Q7': 'How found out',
                       'Q10': 'Satisfaction',
                       'Q13': 'Visit again',
                       # 'Q14': 'Likely recommend',
                       'Q15': 'Gender',
                       'Q16': 'Age',
                       'Q17': 'Disabled?',
                       'Q18': 'Ethnicity',
                       'Q19': 'Where live UK'}
    QUESTIONS9 = [f'Q{n / 100:.02f}' for n in range(901, 917)]  # Q9.01, Q9.02, ...
    MAJOR_QUESTIONS = list(CROSSTAB_TITLES.keys()) + QUESTIONS9 + [f'Q{i}' for i in
                                                                   (2, 4, 6, 7, 8,
                                                                    14)]
    # SANITY_QUESTION must be present in the CSV file. If not, we are probably
    # not processing the result of aggregate.py -> split.py
    SANITY_QUESTION = QUESTIONS9[0]
    MAJOR_QUESTIONS = sorted(MAJOR_QUESTIONS, key=lambda k: float(k[1:]))
    MINOR_QUESTIONS = list(CROSSTAB_TITLES)
    if DEBUGMODE:
        CROSSTAB_TITLES = {'Q3': 'Visiting w. others',
                           # 'Q7': 'How found out',
                           'Q10': 'Satisfaction',
                           }
        MAJOR_QUESTIONS = list(CROSSTAB_TITLES.keys())
        MAJOR_QUESTIONS = sorted(MAJOR_QUESTIONS, key=lambda k: float(k[1:]))
        MINOR_QUESTIONS = list(CROSSTAB_TITLES)
else:
    # updated 2017-02-18:
    # noinspection PyRedeclaration
    DEFCOL = {
        'postcode': 'IJ',
        'want_newsletter': 'KE',
        'want_notify': 'KF',
        'volunteer': 'KG',
        'email_addr': 'KK',
    }
    defcol = {dc: col2num(DEFCOL[dc]) for dc in DEFCOL}

    # begin crosstab definitions
    CROSSTAB_TITLES = {'Q2': 'Satisfaction',
                       'Q13': 'Visit again',
                       # 'Q14': 'Likely recommend',
                       'Q15': 'Gender',
                       'Q16': 'Age',
                       'Q17': 'Disabled?',
                       'Q18': 'Ethnicity',
                       'Q19': 'Where live UK'}
    QUESTIONS9 = [f'Q{n / 100:.02f}' for n in range(901, 917)]  # Q9.01, Q9.02, ...
    MAJOR_QUESTIONS = list(CROSSTAB_TITLES.keys()) + QUESTIONS9 + [f'Q{i}' for i in
                                                                   (2, 4, 6, 7, 8,
                                                                    14)]
    # SANITY_QUESTION must be present in the CSV file. If not, we are probably
    # not processing the result of aggregate.py -> split.py
    SANITY_QUESTION = QUESTIONS9[0]
    MAJOR_QUESTIONS = sorted(MAJOR_QUESTIONS, key=lambda k: float(k[1:]))
    MINOR_QUESTIONS = list(CROSSTAB_TITLES)
    if DEBUGMODE:
        CROSSTAB_TITLES = {'Q3': 'Visiting w. others',
                           # 'Q7': 'How found out',
                           'Q10': 'Satisfaction',
                           }
        MAJOR_QUESTIONS = list(CROSSTAB_TITLES.keys())
        MAJOR_QUESTIONS = sorted(MAJOR_QUESTIONS, key=lambda k: float(k[1:]))
        MINOR_QUESTIONS = list(CROSSTAB_TITLES)

# end crosstab definitions
