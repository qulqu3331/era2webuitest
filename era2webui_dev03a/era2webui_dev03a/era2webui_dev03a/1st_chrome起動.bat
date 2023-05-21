set DIRNAME="%~dp0%chromeuserdata"

start chrome.exe 127.0.0.1:7860 -remote-debugging-port=9222 --user-data-dir=%DIRNAME%