@echo off

:: 1. 작업 디렉토리로 이동 (D드라이브)
d:
cd D:\CCTV_Anomaly_Detection\sctipts\aihub_uploader

:: 2. Git Bash를 실행하여 우리 스크립트(upload_all.sh)를 가동
:: -log 옵션을 통해 별도의 창에서 로그를 실시간으로 보여줍니다.
"C:\Program Files\Git\bin\bash.exe" --login -i -c "./upload_all.sh"

pause