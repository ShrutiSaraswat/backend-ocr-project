Started by user admin
Obtained Jenkinsfile from git https://github.com/ShrutiSaraswat/backend-ocr-project
[Pipeline] Start of Pipeline
[Pipeline] node
Running on Jenkins in C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project
[Pipeline] { (hide)
[Pipeline] stage
[Pipeline] { (Declarative: Checkout SCM)
[Pipeline] checkout
Selected Git installation does not exist. Using Default
The recommended git tool is: NONE
No credentials specified
 > git.exe rev-parse --resolve-git-dir C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project\.git # timeout=10
Fetching changes from the remote Git repository
 > git.exe config remote.origin.url https://github.com/ShrutiSaraswat/backend-ocr-project # timeout=10
Fetching upstream changes from https://github.com/ShrutiSaraswat/backend-ocr-project
 > git.exe --version # timeout=10
 > git --version # 'git version 2.51.0.windows.2'
 > git.exe fetch --tags --force --progress -- https://github.com/ShrutiSaraswat/backend-ocr-project +refs/heads/*:refs/remotes/origin/* # timeout=10
 > git.exe rev-parse "refs/remotes/origin/main^{commit}" # timeout=10
Checking out Revision 3950255d88a4e90c4a355082ae8ab5e98d9f771b (refs/remotes/origin/main)
 > git.exe config core.sparsecheckout # timeout=10
 > git.exe checkout -f 3950255d88a4e90c4a355082ae8ab5e98d9f771b # timeout=10
Commit message: "."
 > git.exe rev-list --no-walk afb2f6ef70e2736db7debc917838ec80b635b1b9 # timeout=10
[Pipeline] }
[Pipeline] // stage
[Pipeline] withEnv
[Pipeline] {
[Pipeline] withCredentials
Masking supported pattern matches of %S3_BUCKET% or %S3_REGION% or %S3_SECRET_KEY% or %S3_ACCESS_KEY%
[Pipeline] {
[Pipeline] withEnv
[Pipeline] {
[Pipeline] stage
[Pipeline] { (Clone Repository)
[Pipeline] echo
📥 Cloning public GitHub repository...
[Pipeline] git
Selected Git installation does not exist. Using Default
The recommended git tool is: NONE
No credentials specified
 > git.exe rev-parse --resolve-git-dir C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project\.git # timeout=10
Fetching changes from the remote Git repository
 > git.exe config remote.origin.url https://github.com/ShrutiSaraswat/backend-ocr-project.git # timeout=10
Fetching upstream changes from https://github.com/ShrutiSaraswat/backend-ocr-project.git
 > git.exe --version # timeout=10
 > git --version # 'git version 2.51.0.windows.2'
 > git.exe fetch --tags --force --progress -- https://github.com/ShrutiSaraswat/backend-ocr-project.git +refs/heads/*:refs/remotes/origin/* # timeout=10
 > git.exe rev-parse "refs/remotes/origin/main^{commit}" # timeout=10
Checking out Revision 3950255d88a4e90c4a355082ae8ab5e98d9f771b (refs/remotes/origin/main)
 > git.exe config core.sparsecheckout # timeout=10
 > git.exe checkout -f 3950255d88a4e90c4a355082ae8ab5e98d9f771b # timeout=10
 > git.exe branch -a -v --no-abbrev # timeout=10
 > git.exe branch -D main # timeout=10
 > git.exe checkout -b main 3950255d88a4e90c4a355082ae8ab5e98d9f771b # timeout=10
Commit message: "."
[Pipeline] }
[Pipeline] // stage
[Pipeline] stage
[Pipeline] { (Set up Python Environment)
[Pipeline] echo
🐍 Creating Python virtual environment...
[Pipeline] bat

C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project>python -m venv venv 

C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project>call venv\Scripts\activate 
Requirement already satisfied: pip in c:\programdata\jenkins\.jenkins\workspace\ocr-project\venv\lib\site-packages (25.3)
Requirement already satisfied: Flask==3.0.3 in c:\programdata\jenkins\.jenkins\workspace\ocr-project\venv\lib\site-packages (from -r requirements.txt (line 2)) (3.0.3)
Requirement already satisfied: Flask-Cors==5.0.0 in c:\programdata\jenkins\.jenkins\workspace\ocr-project\venv\lib\site-packages (from -r requirements.txt (line 3)) (5.0.0)
Requirement already satisfied: Werkzeug==3.0.4 in c:\programdata\jenkins\.jenkins\workspace\ocr-project\venv\lib\site-packages (from -r requirements.txt (line 4)) (3.0.4)
Requirement already satisfied: boto3==1.35.54 in c:\programdata\jenkins\.jenkins\workspace\ocr-project\venv\lib\site-packages (from -r requirements.txt (line 7)) (1.35.54)
Requirement already satisfied: botocore==1.35.54 in c:\programdata\jenkins\.jenkins\workspace\ocr-project\venv\lib\site-packages (from -r requirements.txt (line 8)) (1.35.54)
Requirement already satisfied: python-dotenv==1.0.1 in c:\programdata\jenkins\.jenkins\workspace\ocr-project\venv\lib\site-packages (from -r requirements.txt (line 11)) (1.0.1)
Requirement already satisfied: requests==2.32.3 in c:\programdata\jenkins\.jenkins\workspace\ocr-project\venv\lib\site-packages (from -r requirements.txt (line 14)) (2.32.3)
Requirement already satisfied: gunicorn==23.0.0 in c:\programdata\jenkins\.jenkins\workspace\ocr-project\venv\lib\site-packages (from -r requirements.txt (line 17)) (23.0.0)
Requirement already satisfied: Jinja2>=3.1.2 in c:\programdata\jenkins\.jenkins\workspace\ocr-project\venv\lib\site-packages (from Flask==3.0.3->-r requirements.txt (line 2)) (3.1.6)
Requirement already satisfied: itsdangerous>=2.1.2 in c:\programdata\jenkins\.jenkins\workspace\ocr-project\venv\lib\site-packages (from Flask==3.0.3->-r requirements.txt (line 2)) (2.2.0)
Requirement already satisfied: click>=8.1.3 in c:\programdata\jenkins\.jenkins\workspace\ocr-project\venv\lib\site-packages (from Flask==3.0.3->-r requirements.txt (line 2)) (8.3.0)
Requirement already satisfied: blinker>=1.6.2 in c:\programdata\jenkins\.jenkins\workspace\ocr-project\venv\lib\site-packages (from Flask==3.0.3->-r requirements.txt (line 2)) (1.9.0)
Requirement already satisfied: MarkupSafe>=2.1.1 in c:\programdata\jenkins\.jenkins\workspace\ocr-project\venv\lib\site-packages (from Werkzeug==3.0.4->-r requirements.txt (line 4)) (3.0.3)
Requirement already satisfied: jmespath<2.0.0,>=0.7.1 in c:\programdata\jenkins\.jenkins\workspace\ocr-project\venv\lib\site-packages (from boto3==1.35.54->-r requirements.txt (line 7)) (1.0.1)
Requirement already satisfied: s3transfer<0.11.0,>=0.10.0 in c:\programdata\jenkins\.jenkins\workspace\ocr-project\venv\lib\site-packages (from boto3==1.35.54->-r requirements.txt (line 7)) (0.10.4)
Requirement already satisfied: python-dateutil<3.0.0,>=2.1 in c:\programdata\jenkins\.jenkins\workspace\ocr-project\venv\lib\site-packages (from botocore==1.35.54->-r requirements.txt (line 8)) (2.9.0.post0)
Requirement already satisfied: urllib3!=2.2.0,<3,>=1.25.4 in c:\programdata\jenkins\.jenkins\workspace\ocr-project\venv\lib\site-packages (from botocore==1.35.54->-r requirements.txt (line 8)) (2.5.0)
Requirement already satisfied: charset-normalizer<4,>=2 in c:\programdata\jenkins\.jenkins\workspace\ocr-project\venv\lib\site-packages (from requests==2.32.3->-r requirements.txt (line 14)) (3.4.4)
Requirement already satisfied: idna<4,>=2.5 in c:\programdata\jenkins\.jenkins\workspace\ocr-project\venv\lib\site-packages (from requests==2.32.3->-r requirements.txt (line 14)) (3.11)
Requirement already satisfied: certifi>=2017.4.17 in c:\programdata\jenkins\.jenkins\workspace\ocr-project\venv\lib\site-packages (from requests==2.32.3->-r requirements.txt (line 14)) (2025.10.5)
Requirement already satisfied: packaging in c:\programdata\jenkins\.jenkins\workspace\ocr-project\venv\lib\site-packages (from gunicorn==23.0.0->-r requirements.txt (line 17)) (25.0)
Requirement already satisfied: six>=1.5 in c:\programdata\jenkins\.jenkins\workspace\ocr-project\venv\lib\site-packages (from python-dateutil<3.0.0,>=2.1->botocore==1.35.54->-r requirements.txt (line 8)) (1.17.0)
Requirement already satisfied: colorama in c:\programdata\jenkins\.jenkins\workspace\ocr-project\venv\lib\site-packages (from click>=8.1.3->Flask==3.0.3->-r requirements.txt (line 2)) (0.4.6)
[Pipeline] }
[Pipeline] // stage
[Pipeline] stage
[Pipeline] { (Verify Dependencies)
[Pipeline] echo
🔍 Verifying environment setup...
[Pipeline] bat

C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project>chcp 65001  1>NUL 

C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project>call venv\Scripts\activate 
Environment ready - dependencies imported successfully.
[Pipeline] }
[Pipeline] // stage
[Pipeline] stage
[Pipeline] { (Run Tests)
[Pipeline] echo
🧪 Running tests if any...
[Pipeline] bat

C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project>call venv\Scripts\activate 
C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project\venv\Scripts\python.exe: No module named pytest
[Pipeline] }
[Pipeline] // stage
[Pipeline] stage
[Pipeline] { (Deploy Application)
[Pipeline] echo
🚀 Starting Flask OCR service...
[Pipeline] bat

C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project>call venv\Scripts\activate 
Starting Flask server and logging output...
Start-Process : This command cannot be run because "RedirectStandardOutput" and "RedirectStandardError" are same. Give 
different inputs and Run your command again.
At line:1 char:1
+ Start-Process python -ArgumentList 'server.py' -RedirectStandardOutpu ...
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : InvalidOperation: (:) [Start-Process], InvalidOperationException
    + FullyQualifiedErrorId : InvalidOperationException,Microsoft.PowerShell.Commands.StartProcessCommand
 
ERROR: Input redirection is not supported, exiting the process immediately.
✅ Flask server started on port 5000!
[Pipeline] }
[Pipeline] // stage
[Pipeline] stage
[Pipeline] { (Verify Server Health)
[Pipeline] echo
🔎 Checking Flask health endpoint (with retry)...
[Pipeline] bat

C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project>setlocal enabledelayedexpansion 

C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project>set RETRIES=3 

C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project>set COUNT=1 

C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project>echo Attempt !COUNT! of !RETRIES! 
Attempt 1 of 3

C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project>curl -s http://localhost:5000/health   1>nul 2>&1  && (
echo ✅ Flask health check passed!  
 exit /b 0 
) 

C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project>if !COUNT! LSS !RETRIES! (
set /a COUNT+=1  
 echo Waiting before retry...  
 timeout /t 5  1>nul  
 goto RETRY 
) 
Waiting before retry...
ERROR: Input redirection is not supported, exiting the process immediately.

C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project>echo Attempt !COUNT! of !RETRIES! 
Attempt 2 of 3

C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project>curl -s http://localhost:5000/health   1>nul 2>&1  && (
echo ✅ Flask health check passed!  
 exit /b 0 
) 

C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project>if !COUNT! LSS !RETRIES! (
set /a COUNT+=1  
 echo Waiting before retry...  
 timeout /t 5  1>nul  
 goto RETRY 
) 
Waiting before retry...
ERROR: Input redirection is not supported, exiting the process immediately.

C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project>echo Attempt !COUNT! of !RETRIES! 
Attempt 3 of 3

C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project>curl -s http://localhost:5000/health   1>nul 2>&1  && (
echo ✅ Flask health check passed!  
 exit /b 0 
) 

C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project>if !COUNT! LSS !RETRIES! (
set /a COUNT+=1  
 echo Waiting before retry...  
 timeout /t 5  1>nul  
 goto RETRY 
) 

C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project>echo ❌ Health check failed after !RETRIES! attempts. 
❌ Health check failed after 3 attempts.

C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project>exit /b 1 
[Pipeline] }
[Pipeline] // stage
[Pipeline] stage
[Pipeline] { (Declarative: Post Actions)
[Pipeline] echo
📅 Build completed at: Wed Nov 05 01:29:25 IST 2025
[Pipeline] echo
🛑 Stopping any running Flask process...
[Pipeline] bat

C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project>for /F "tokens=5" %a in ('netstat -ano | find ":5000"') do (if not "%a" == "0" (taskkill /PID %a /F   1>nul 2>&1  || echo Could not kill PID %a ) ) 

C:\ProgramData\Jenkins\.jenkins\workspace\OCR-project>exit /b 0 
[Pipeline] echo
❌ Build or deployment failed. Check console output.
[Pipeline] archiveArtifacts
Archiving artifacts
[Pipeline] }
[Pipeline] // stage
[Pipeline] }
[Pipeline] // withEnv
[Pipeline] }
[Pipeline] // withCredentials
[Pipeline] }
[Pipeline] // withEnv
[Pipeline] }
[Pipeline] // node
[Pipeline] End of Pipeline
ERROR: script returned exit code 1
Finished: FAILURE