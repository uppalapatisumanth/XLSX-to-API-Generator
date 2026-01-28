@echo off
echo Starting Debug Batch > debug_probe.txt
python --version >> debug_probe.txt 2>&1
echo Running run_server.py >> debug_probe.txt
python run_server.py >> debug_probe.txt 2>&1
echo Done >> debug_probe.txt
type debug_probe.txt
