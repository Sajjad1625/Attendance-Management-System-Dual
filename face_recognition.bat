@echo off
tasklist | find /i "python.exe" && taskkill /im "python.exe" /F || echo process "python.exe" not running
timeout 2 /nobreak
start /B C:/Users/sajja/AppData/Local/Programs/Python/Python39/python.exe "c:/Users/sajja/OneDrive/Desktop/Attendance Management System Dual/camera_share.py"
timeout 6 /nobreak
start /B C:/Users/sajja/AppData/Local/Programs/Python/Python39/python.exe "c:/Users/sajja/OneDrive/Desktop/Attendance Management System Dual/camera_share2.py"
timeout 6 /nobreak
start /B C:/Users/sajja/AppData/Local/Programs/Python/Python39/python.exe "c:/Users/sajja/OneDrive/Desktop/Attendance Management System Dual/new_recognition_login.py"
timeout 6 /nobreak
start /B C:/Users/sajja/AppData/Local/Programs/Python/Python39/python.exe "c:/Users/sajja/OneDrive/Desktop/Attendance Management System Dual/new_recognition_logout.py"
timeout 6 /nobreak
start /B C:/Users/sajja/AppData/Local/Programs/Python/Python39/python.exe "c:/Users/sajja/OneDrive/Desktop/Attendance Management System Dual/main.py"
timeout 10 /nobreak
start /B msedge "http://localhost:5000"
pause