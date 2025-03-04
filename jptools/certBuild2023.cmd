set SCONSOPTIONS=%*

set TIMESERVER=http://timestamp.comodoca.com/

call miscDepsJp\include\python-jtalk\vcsetup.cmd
cd /d %~dp0
cd ..

nmake /?
@if not "%ERRORLEVEL%"=="0" goto onerror

patch -v
@if not "%ERRORLEVEL%"=="0" goto onerror

cd miscDepsJp\jptools
call build-and-test.cmd
@if not "%ERRORLEVEL%"=="0" goto onerror
cd ..\..

call jptools\setupMiscDepsJp.cmd

set SIGNTOOL="C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe"

%SIGNTOOL% sign /a /fd SHA256 /tr %TIMESERVER% /td SHA256 source\synthDrivers\jtalk\libmecab.dll
@if not "%ERRORLEVEL%"=="0" goto onerror
timeout /T 5 /NOBREAK

%SIGNTOOL% sign /a /fd SHA256 /tr %TIMESERVER% /td SHA256 source\synthDrivers\jtalk\libopenjtalk.dll
@if not "%ERRORLEVEL%"=="0" goto onerror
timeout /T 5 /NOBREAK

set SCONSARGS=certTimestampServer=%TIMESERVER% version=%VERSION% updateVersionType=%UPDATEVERSIONTYPE% %SCONSOPTIONS%

call scons.bat source user_docs launcher release=1 publisher=%PUBLISHER% %SCONSARGS%
@if not "%ERRORLEVEL%"=="0" goto onerror

cd jptools
call pack_jtalk_addon.cmd
call pack_kgs_addon.cmd
cd ..
call jptools\buildControllerClient.cmd %SCONSARGS%
set PYTHONUTF8=1
call jptools\tests.cmd
call jpchar\tests.cmd

set VERIFYLOG=output\nvda_%VERSION%_verify.log
del /Q %VERIFYLOG%

%SIGNTOOL% verify /pa output\*.exe >> %VERIFYLOG%
@if not "%ERRORLEVEL%"=="0" goto onerror

%SIGNTOOL% verify /pa dist\*.exe >> %VERIFYLOG%
@if not "%ERRORLEVEL%"=="0" goto onerror

for /r "dist\synthDrivers\jtalk" %%i in (*.dll *.exe) do (
    %SIGNTOOL% verify /pa "%%i" >> %VERIFYLOG%
    @if not "%ERRORLEVEL%"=="0" goto onerror
)
for /r "dist\lib" %%i in (*.dll *.exe) do (
    if "%%~nxi" neq "Microsoft.UI.UIAutomation.dll" (
        %SIGNTOOL% verify /pa "%%i" >> %VERIFYLOG%
        @if not "%ERRORLEVEL%"=="0" goto onerror
    )
)
for /r "dist\lib64" %%i in (*.dll *.exe) do (
    %SIGNTOOL% verify /pa "%%i" >> %VERIFYLOG%
    @if not "%ERRORLEVEL%"=="0" goto onerror
)
for /r "dist\libArm64" %%i in (*.dll *.exe) do (
    %SIGNTOOL% verify /pa "%%i" >> %VERIFYLOG%
    @if not "%ERRORLEVEL%"=="0" goto onerror
)

echo %UPDATEVERSIONTYPE% %VERSION%
exit /b 0

:onerror
echo nvdajp build error %ERRORLEVEL%
@if "%PAUSE%"=="1" pause
exit /b -1
