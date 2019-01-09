#!/bin/bash
#
# condensed.sh
# --------------
#
# This is a modification of "extract_csv.sh" that processes a file saved
# from SurveyMonkey with the condensed format and numerical values instead
# of actual text.
#
# Run this script in the ~/pyprj/hrm/evaluation directory. Note that the
# exports subdirectory is a symbolic link to ~/Downloads/hrm/evaluation/data_exports.
# This script will search the "exports" directory for zip files and process
# the first one found.
#
# Output:
# -------
# A directory is created with the name in the format "yyyy-mm-dd" with
# sub-directories "response" and "cleaned". The "response" directory contains
# the un-zipped files from the downloaded zip file. The "cleaned" directory
# contains the output CSV file from the extraction and cleaning toolchain.
#
# Usage:
# ------
# To download the zip file to the 'exports' directory:
# Log on to www.surveymonkey.com.
# Select "My Surveys" on the top menu.
# Select Heath Robinson Museum Visitor Survey / Analyze.
# Click SAVE AS / Export file / Export All / All responses data.
# On the popup "Export Survey Data" select:
# File format: XLS
# Data view:   Original View
# Columns:     Expanded <-- Changed to "Condensed"  
# Cells:       Actual Answer Text <-- Changed to "Numerical Values (1-n)"
# File:        The zip file name must be of the format <datadir>_<lastnum>.zip.
# The <datadir> field should be in the format yyyy-mm-dd.
# The <lastnum> field should be the number of the last survey in the export.
#
# Download the file to hrm/evaluation/exports. 
# This script will unzip the file to exports/<datadir>/response/<exportname>/
# and then create the cleaned CSV file. It will also move the zip file from the
# exports directory to the exports/oldzipfiles directory.
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
mv exports/${DATADIR}_${EXPORTNAME}.zip exports/old_zipfiles
}
#
#         Main Program
#
if [[ "$CONDA_DEFAULT_ENV" != "py6" ]]; then
    echo Activating py6...
    . activate py6
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
expand_one
break
done
