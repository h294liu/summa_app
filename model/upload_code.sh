#!/bin/bash
set -e 

#reference: https://stackoverflow.com/questions/12799719/how-to-upload-a-project-to-github
# copy and upload code to an existing github repo

cp ~/work/sharp/basins/scripts/*.py .
cp ~/work/sharp/basins/scripts/*.sh .

git add .
git commit -m "update files"
git push -u origin master