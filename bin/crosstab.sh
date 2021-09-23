#!/bin/bash
###
### crosstab.sh
### ———————————
###
### Input is the cleaned CSV file (in the "cleaned" dir). This must have a name
### like "310.csv".
###
### Output is two XLSX files in the output directory, one with the full
### crosstabs and one with question 16 excluded.
###
### Parameters after the first are passed to crosstabs3.py.
###
HOMEDIR='/Users/mlg/pyprj/hrm/evaluation'
OUTPUTDIR="results/surveymonkey/crosstabs"
help() {
	grep -E '^###' $0 | sed -E 's/### ?//'
}
if [[ $# == 0 ]] || [[ "$1" == "-h" ]] ; then
help
echo Output directory: $HOMEDIR/$OUTPUTDIR
exit 1
fi
CONDAENV=py8
RED='\033[0;31m'
GREEN='\033[0;32m'
NOCOLOR='\033[0m'
set -e
if [[ "$CONDA_DEFAULT_ENV" != $CONDAENV ]]; then
    echo Activating $CONDAENV...
    eval "$(conda shell.bash hook)"
    conda activate $CONDAENV
fi
pushd $HOMEDIR
echo Output directory: $HOMEDIR/$OUTPUTDIR
INCSV=$(python3 <<END
import os.path as op
print(op.basename('$1'))
END
) # This close parenthesis closes the here document
# echo $INCSV
BASENAME=`python3 -c "print('$INCSV'.split('.')[0])"`
# echo $BASENAME
OUTPATH="$OUTPUTDIR/crosstab_${BASENAME}.xlsx"
OUTPATH2="$OUTPUTDIR/crosstab_${BASENAME}-2.xlsx"
echo Creating: $OUTPATH
mkdir -p $OUTPUTDIR
[ -e "temp" ] || mkdir temp
# Skip split/aggregate if we're just testing changes to crosstabs.
# Do split/agg if agg.csv doesn't exist or the output doesn't exist or
# the input is newer than the output.
if [ ! -e temp/agg.csv -o ! -e $OUTPATH -o "$1" -nt $OUTPATH ] ; then
	python src/split.py "$1" temp/split.csv
	python src/aggregate.py temp/split.csv temp/agg.csv
	python src/aggregate.py temp/split.csv temp/agg2.csv --exclude q16
else
	echo -e "${GREEN}Skipping split/aggregation.${NOCOLOR}"
fi
shift
python src/crosstabs4.py temp/agg.csv $OUTPATH $*
python src/crosstabs4.py temp/agg2.csv $OUTPATH2 $*
