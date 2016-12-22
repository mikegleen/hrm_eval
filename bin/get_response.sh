#!/bin/bash
function process {
    INFILE=$RESPPATH/$DATADIR/CSV/Sheet_1.csv
    # ls $INFILE
    python3 src/remove_nuls.py $INFILE temp/remove_nuls.txt
    python3 src/clean_title.py temp/remove_nuls.txt temp/clean_title.txt
    python3 src/assign_nums.py temp/clean_title.txt temp/precleaned.csv
    python3 ~/pyprj/misc/put_bom.py temp/precleaned.csv $CLEANDIR/$DATADIR/cleaned.csv
}

DATADIR=Data_All_Num_2016-12-18
RESPPATH=exports/response
CLEANDIR=exports/cleaned
INFILE=$RESPPATH/$DATADIR/CSV/Sheet_1.csv
# ls $INFILE
python3 src/remove_nuls.py $INFILE temp/remove_nuls.txt
python3 src/clean_title.py temp/remove_nuls.txt temp/clean_title.txt
[ -e "$CLEANDIR/$DATADIR" ] || mkdir $CLEANDIR/$DATADIR
python3 src/assign_nums.py temp/clean_title.txt temp/precleaned.csv
python3 ~/pyprj/misc/put_bom.py temp/precleaned.csv $CLEANDIR/$DATADIR/cleaned.csv
rm temp/*
