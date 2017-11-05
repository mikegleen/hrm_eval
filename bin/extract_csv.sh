#!/bin/bash
#
# extract_csv.sh
# --------------
#
# Search the "exports" directory for zip files. Process the first one found.
#
# Usage:
# Download the zip file to the 'exports' directory.
# When exporting, selecting options "All Responses", "Original View",
#   "Expanded", "Actual Answer Text".
# The zip file name must be of the format <datadir>_<exportname>.zip.
# The <datadir> field should be in the format yyyy-mm-dd.
# The <exportname> field should reflect the parameters used to export the file
# from SurveyMonkey. This is just for information and is not used in processing.
#
# This script will unzip the file to exports/<datadir>/response/<exportname>/
# and then create the cleaned CSV file.
#
# The exported data can be in one sheet or two. If in two sheets, the script
# will merge them. The number of columns to skip in the second sheet is hard
# coded in config.py.
#
# Also move the zip file from the exports directory to the exports/oldzipfiles
# directory.
#
# After this setup is done, get_emails.py will be executed; see the doc for that
# program.
#
CSVFILENAME="Heath Robinson Museum Visitor Survey.csv"

expand_one () {
RESPDIR=exports/$DATADIR/response
CSVDIR=$RESPDIR/$EXPORTNAME/CSV
CLEANDIR=exports/$DATADIR/cleaned
echo Creating $RESPDIR
mkdir -p $RESPDIR
# Rename the unzipped directory to be just the date.
unzip exports/${DATADIR}_${EXPORTNAME}.zip -d $RESPDIR/$EXPORTNAME
mv exports/${DATADIR}_${EXPORTNAME}.zip exports/old_zipfiles
#
mkdir -p $CLEANDIR
[ -e "temp" ] || mkdir temp
python3 src/remove_nuls.py "$CSVDIR/$CSVFILENAME" temp/rem_nuls.csv
python3 src/clean_title.py temp/rem_nuls.csv temp/clean_title.csv
python3 ~/pyprj/misc/put_bom.py temp/clean_title.csv $CLEANDIR/$EXPORTNAME.csv
#rm temp/*
python3 src/get_emails.py --dryrun $CLEANDIR/$EXPORTNAME.csv
echo
echo -e ${GREEN}If the dry run was ok, execute the following line to extract the
echo -e email addresses and update the database:${NC}
echo python3 src/get_emails.py $CLEANDIR/$EXPORTNAME.csv
}
#
#         Main Program
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color
set -e
pushd ~/pyprj/hrm/evaluation
for zipfile in exports/*.zip; do
if [[ $zipfile == "exports/*.zip" ]]; then
    echo -e "${RED}Cannot find any ZIP files in ~/pyprj/hrm/evaluation/exports.${NC}"
    break
fi
echo Extracting $zipfile
# zipfile = "exports/yyyy-mm-dd_exportname.zip"
DATADIR=`python3 -c "print('$zipfile'.split('_',1)[0])"`
# DATADIR = "exports/yyyy-mm-dd"
DATADIR=`python3 -c "print('$DATADIR'.split('/')[1])"`
# DATADIR = "yyyy-mm-dd"
EXPORTNAME=`python3 -c "print('$zipfile'[:-4].split('_', 1)[1])"`
# EXPORTNAME = "exportname"
echo $DATADIR $EXPORTNAME
expand_one
break
done
