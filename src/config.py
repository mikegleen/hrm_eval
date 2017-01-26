"""
Configuration file for processing SurveyMonkey CSV files.

This configuration assumes that the CSV file has been cleaned up by
get_response.sh which adds a row at the front containing the question numbers.

To use the unmodified export from SurveyMonkey, change skiprows to 2.

"""
from excel_cols import col2num

skiprows = 3
DEFCOL = {
    'postcode': 'HW',
    'want_newsletter': 'JR',
    'want_notify': 'JS',
    'volunteer': 'JT',
    'email_addr': 'JX',
}
# updated 2017-01-25:
DEFCOL = {
    'postcode': 'HX',
    'want_newsletter': 'JS',
    'want_notify': 'JT',
    'volunteer': 'JU',
    'email_addr': 'JY',
}
defcol = {dc: col2num(DEFCOL[dc]) for dc in DEFCOL}
