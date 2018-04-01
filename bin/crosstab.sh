#!/bin/bash
#
# crosstab.sh
# ———————————
#
# Input is the cleaned CSV file (in the "cleaned" dir)
# 
set -e
pushd ~/pyprj/hrm/evaluation
OUTPUTDIR="results/surveymonkey/crosstabs"
INCSV=$(python3 <<END
import os.path as op
print(op.basename('$1'))
END
) # This close parenthesis closes the here document
# echo $INCSV
BASENAME=`python3 -c "print('$INCSV'.split('.')[0])"`
# echo $BASENAME
OUTPATH="$OUTPUTDIR/c${BASENAME}.xlsx"
echo Creating: $OUTPATH
mkdir -p $OUTPUTDIR
[ -e "temp" ] || mkdir temp
# Skip split/aggregate if we're just testing changes to crosstabs.
# Do split/agg if agg.csv doesn't exist or the output doesn't exist or
# the input is newer than the output.
if [ ! -e temp/agg.csv -o ! -e $OUTPATH -o "$1" -nt $OUTPATH ] ; then
	python src/split.py $1 temp/split.csv
	python src/aggregate.py temp/split.csv temp/agg.csv
else
	echo -e "\033[32mSkipping split/aggregation.\033[0m"
fi
python src/crosstabs3.py temp/agg.csv $OUTPATH
