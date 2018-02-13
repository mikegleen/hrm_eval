#!/bin/bash
#
# crosstab.sh
# ———————————
#
# 
set -e
pushd ~/pyprj/hrm/evaluation
OUTPUTDIR="results/surveymonkey"
INCSV=$(python3 <<END
import os.path as op
print(op.basename('$1'))
END
) # This close parenthesis closes the here document
# echo $INCSV
BASENAME=`python3 -c "print('$INCSV'.split('.')[0])"`
# echo $BASENAME
OUTPATH="$OUTPUTDIR/${BASENAME}.xlsx"
echo Creating: $OUTPATH
mkdir -p $OUTPUTDIR
[ -e "temp" ] || mkdir temp
if [ ! -e temp/agg.csv -o ! -e $OUTPATH -o $1 -nt $OUTPATH ] ; then
	python src/aggregate.py $1 temp/agg.csv
else
	echo -e "\033[32mSkipping aggregation.\033[0m"
fi
python src/crosstabs3.py temp/agg.csv $OUTPATH
