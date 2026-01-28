@echo off
echo Starting > debug_bat.txt
d:\ais\api\backend\venv\Scripts\python.exe generate_suprabhat.py >> debug_bat.txt 2>&1
echo Finished >> debug_bat.txt
