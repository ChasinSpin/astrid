#!/bin/sh
if [ $# -lt 1 ];then
	echo "Usage: $0 file1 [file2 .. fileN]"
	exit 1
fi

echo "### flake8..."
flake8 $*
echo
echo "### pydocstyle..."
pydocstyle $*
echo
#echo "### pylint..."
#pylint $*
