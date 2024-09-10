#!/usr/bin/env bash

python3 "/Users/vaibhavjaiswal/Library/CloudStorage/OneDrive-Niltech/Shared Drive-Niltech/Ongoing Projects/Vaibhav Ongoing/Attendance Management System Dual Camera/camera_share.py" &
sleep 5
python3 "/Users/vaibhavjaiswal/Library/CloudStorage/OneDrive-Niltech/Shared Drive-Niltech/Ongoing Projects/Vaibhav Ongoing/Attendance Management System Dual Camera/camera_share2.py" &
sleep 5
python3 "/Users/vaibhavjaiswal/Library/CloudStorage/OneDrive-Niltech/Shared Drive-Niltech/Ongoing Projects/Vaibhav Ongoing/Attendance Management System Dual Camera/new_recognition_login.py" &
sleep 5
python3 "/Users/vaibhavjaiswal/Library/CloudStorage/OneDrive-Niltech/Shared Drive-Niltech/Ongoing Projects/Vaibhav Ongoing/Attendance Management System Dual Camera/new_recognition_logout.py" &
sleep 5
python3 "/Users/vaibhavjaiswal/Library/CloudStorage/OneDrive-Niltech/Shared Drive-Niltech/Ongoing Projects/Vaibhav Ongoing/Attendance Management System Dual Camera/main.py" &
sleep 10
open "http://127.0.0.1:5000"
wait
