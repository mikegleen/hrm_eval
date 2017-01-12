#!/bin/bash
#
# Two input parameters are required, the data directory under "exports" and
# the subdirectory under .../response.
#
# Example:
#   called as: ./get_response.sh 2016-12-31 condensed_actual
#   input:  exports/2016-12-31/response/condensed_actual/CSV/Sheet_1.csv
#   output: exports/2016-12-31/cleaned/condensed_actual.csv
#
# In this case DATADIR is 2016-12-31 and EXPORTNAME is condensed_actual.
# The exported data can be in one sheet or two. If in two sheets, the script
# will merge them. The number of columns to skip in the second sheet is hard
# coded in merge_csv.py.
#
DATADIR=$1
EXPORTNAME=$2

RESPDIR=exports/$DATADIR/response/$EXPORTNAME/CSV
CLEANDIR=exports/$DATADIR/cleaned
set -e
[ -e "$CLEANDIR" ] || mkdir -p $CLEANDIR
[ -e "temp" ] || mkdir temp
python3 src/remove_nuls.py $RESPDIR/Sheet_1.csv temp/rem_nuls_1.csv
if [ -e "$RESPDIR/Sheet_2.csv" ]
then
    python3 src/remove_nuls.py $RESPDIR/Sheet_2.csv temp/rem_nuls_2.csv
    python3 src/merge_csv.py temp/rem_nuls_1.csv temp/rem_nuls_2.csv temp/merged.csv
else
    cp temp/rem_nuls_1.csv temp/merged.csv
fi
python3 src/clean_title.py temp/merged.csv temp/clean_title.csv
python3 ~/pyprj/misc/put_bom.py temp/clean_title.csv $CLEANDIR/$EXPORTNAME.csv
#rm temp/*
