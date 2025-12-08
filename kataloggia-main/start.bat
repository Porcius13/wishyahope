@echo off
cd /d %~dp0
python run_local.py > output.txt 2>&1
type output.txt
