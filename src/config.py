"""
Configuration file for processing SurveyMonkey CSV files.

This configuration assumes that the CSV file has been cleaned up by
get_response.sh which adds a row at the top containing the question numbers and
merges multiple CSV files into a single spreadsheet.

To use the unmodified export from SurveyMonkey, change skiprows to 2 and adjust
the column numbers accordingly.

"""
from excel_cols import col2num

SKIPCOLS = 9
SKIPROWS = 3
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
