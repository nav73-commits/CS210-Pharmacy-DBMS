@echo off
echo ======================================================
echo PHARMACY DBMS: PUSH TO GITHUB
echo ======================================================

echo [1/5] Initializing Git...
git init

echo [2/5] Adding all files (including Database)...
git add .

echo [3/5] Creating commit...
git commit -m "Final Project Submission: Pharmacy DBMS with Analytics"

echo [4/5] Connecting to Remote Repository...
git remote add origin https://github.com/nav73-commits/CS210-Pharmacy-DBMS.git
git branch -M main

echo [5/5] Pushing to GitHub...
echo (You may be asked to log in to GitHub in a popup window)
git push -u origin main

echo ======================================================
echo PUSH COMPLETE! Check your repo at:
echo https://github.com/nav73-commits/CS210-Pharmacy-DBMS
echo ======================================================
pause
