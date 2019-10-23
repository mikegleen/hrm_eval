#!/bin/bash
#
# extract_csv.sh
# --------------
#
# Run this script in the ~/pyprj/hrm/evaluation directory. Note that the
# *exports* subdirectory is a symbolic link to
# ~/Downloads/hrm/evaluation/data_exports.
# This script will search the "exports" directory for zip files and process
# the first one found.
#
# Output:
# -------
#
# The updated JSON file is saved in directory data/email_addrs. The oldest
# JSON file is deleted and the latest 10 are saved.
#
# Reports are written to directory results/new_emails.
#
# Usage:
# ------
#
# Download the zip file to the 'exports' directory:
# Log on to www.surveymonkey.com.
# Select "My Surveys" on the top menu.
# Select Heath Robinson Museum Visitor Survey / Analyze.
# Click SAVE AS / Export file / Export All / All responses data.
# On the popup "Export Survey Data" select:
# File format: CSV
# Data view:   Original View
# Columns:     Expanded
# Cells:       Actual Answer Text
# File:        The zip file name must be of the format <datadir>_<lastnum>.zip.
# The <datadir> field should be in the format yyyy-mm-dd.
# The <lastnum> field should be the number of the last survey in the export.
#
# Download the file to hrm/evaluation/exports. 
# This script will unzip the file to exports/<datadir>/response/<exportname>/
# and then create the cleaned CSV file.
#
#
# The exported data can be in one sheet or two. If in two sheets, the script
# will merge them. The number of columns to skip in the second sheet is hard
# coded in config.py.
#
# Also move the zip file from the exports directory to the exports/oldzipfiles
# directory.
#
# 2018-08-31: get_emails processing removed.
# After this setup is done, get_emails.py will be executed; see the doc for 
# that program.
#
# 2018-11-06 Add call to bin/crosstabs.sh
#

# This file is in the CSV directory in the zip file which we expand below.
CSVFILENAME="Heath Robinson Museum Visitor Survey.csv"

expand_one () {
RESPDIR=exports/$DATADIR/response
CLEANDIR=exports/$DATADIR/cleaned
CSVDIR=$RESPDIR/$EXPORTNAME/CSV
echo Creating $RESPDIR
mkdir -p $RESPDIR
# Rename the unzipped directory to be just the date.
unzip exports/${DATADIR}_${EXPORTNAME}.zip -d $RESPDIR/$EXPORTNAME
#
mkdir -p $CLEANDIR
[ -e "temp" ] || mkdir temp
python3 src/remove_nuls.py "$CSVDIR/$CSVFILENAME" temp/rem_nuls.csv
python3 src/clean_title.py temp/rem_nuls.csv temp/clean_title.csv
python3 ~/pyprj/misc/put_bom.py temp/clean_title.csv $CLEANDIR/$EXPORTNAME.csv
#rm temp/*
# python3 src/get_emails.py --dryrun $CLEANDIR/$EXPORTNAME.csv
mv exports/${DATADIR}_${EXPORTNAME}.zip exports/old_zipfiles
# echo
# echo -e ${GREEN}If the dry run was ok, execute the following line to extract the
# echo -e email addresses and update the database:${NOCOLOR}
# echo python3 src/get_emails.py $CLEANDIR/$EXPORTNAME.csv
bin/crosstab.sh $CLEANDIR/$EXPORTNAME.csv
}
#
#         Main Program
#
if [[ "$CONDA_DEFAULT_ENV" != "py7" ]]; then
    echo Activating py7...
    eval "$(conda shell.bash hook)"
    conda activate py7
fi
RED='\033[0;31m'
GREEN='\033[0;32m'
NOCOLOR='\033[0m'
set -e
pushd ~/pyprj/hrm/evaluation
for zipfile in exports/*.zip; do
if [[ $zipfile == "exports/*.zip" ]]; then
    echo -e "${RED}Cannot find any ZIP files in ~/pyprj/hrm/evaluation/exports.${NOCOLOR}"
    break
fi
echo Extracting $zipfile
# zipfile = "exports/yyyy-mm-dd_exportname.zip"
DATADIR=`python3 -c "print('$zipfile'.split('_',1)[0])"`
# DATADIR = "exports/yyyy-mm-dd"
DATADIR=`python3 -c "print('$DATADIR'.split('/')[1])"`
# DATADIR = "yyyy-mm-dd"
EXPORTNAME=`python3 -c "print('$zipfile'[:-4].split('_', 1)[1])"`
# EXPORTNAME = "152"
echo $DATADIR $EXPORTNAME
# Sanity check valid file name.
re='^[0-9]+-[0-9]+-[0-9]+$'
if ! [[ $DATADIR =~ $re ]] ; then
	echo -e "${RED}error: Not a date${NOCOLOR}" >&2; exit 1
fi
re='^[0-9]+$'
if ! [[ $EXPORTNAME =~ $re ]] ; then
	echo -e "${RED}error: Not a number${NOCOLOR}" >&2; exit 1
fi
expand_one
break
done
