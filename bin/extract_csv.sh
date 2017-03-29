#!/bin/bash
#
# extract_csv.sh
# --------------
#
# Search the "exports" directory for zip files. Process the first one found.
#
# Usage:
# Download the zip file to the 'exports' directory.
# The zip file name must be of the format <datadir>_<exportname>.zip.
# The <datadir> field should be in the format yyyy-mm-dd.
# The <exportname> field should reflect the parameters used to export the file
# from SurveyMonkey. This is just for information and is not used in processing.
#
# This script will unzip the file to exports/<datadir>/response/<exportname> and
# then proceed to create the cleaned CSV file.
#
# The exported data can be in one sheet or two. If in two sheets, the script
# will merge them. The number of columns to skip in the second sheet is hard
# coded in merge_csv.py.
#
# Also move the zip file from the exports directory to the newly created
# response directory.
#

expand_one () {
RESPDIR=exports/$DATADIR/response
CSVDIR=$RESPDIR/$EXPORTNAME/CSV
CLEANDIR=exports/$DATADIR/cleaned
mkdir -p $RESPDIR
# Rename the unzipped directory to be just the date.
unzip exports/${DATADIR}_${EXPORTNAME}.zip -d $RESPDIR/$EXPORTNAME
mv exports/${DATADIR}_${EXPORTNAME}.zip $RESPDIR
#
mkdir -p $CLEANDIR
[ -e "temp" ] || mkdir temp
python3 src/remove_nuls.py $CSVDIR/Sheet_1.csv temp/rem_nuls_1.csv
if [ -e "$CSVDIR/Sheet_2.csv" ]
then
    python3 src/remove_nuls.py $CSVDIR/Sheet_2.csv temp/rem_nuls_2.csv
    python3 src/merge_csv.py temp/rem_nuls_1.csv temp/rem_nuls_2.csv temp/merged.csv
else
    mv temp/rem_nuls_1.csv temp/merged.csv
fi
python3 src/clean_title.py temp/merged.csv temp/clean_title.csv
python3 ~/pyprj/misc/put_bom.py temp/clean_title.csv $CLEANDIR/$EXPORTNAME.csv
#rm temp/*
python3 src/get_emails.py --dryrun $CLEANDIR/$EXPORTNAME.csv
echo python3 src/get_emails.py $CLEANDIR/$EXPORTNAME.csv
}
# 
set -e
pushd ~/pyprj/hrm/evaluation
for zipfile in exports/*.zip; do
# zipfile = "exports/yyyy-mm-dd_exportname.zip"
DATADIR=`python3 -c "print('$zipfile'.split('_',1)[0])"`
# DATADIR = "exports/yyyy-mm-dd"
DATADIR=`python3 -c "print('$DATADIR'.split('/')[1])"`
# DATADIR = "yyyy-mm-dd"
EXPORTNAME=`python3 -c "print('$zipfile'[:-4].split('_', 1)[1])"`
# EXPORTNAME = "exportname" without the trailing ".csv"
echo $DATADIR $EXPORTNAME
expand_one
break
done
