@echo off
setlocal

:: Määritä muuttujat
set REPO_URL=https://github.com/WinSer2003/HHBrowser.git
set GIT_INSTALLER_URL=https://github.com/git-for-windows/git/releases/latest/download/Git-2.40.0-64-bit.exe
set GIT_INSTALLER_PATH=%TEMP%\GitInstaller.exe

:: Määritä nykyinen kansio
set CURRENT_FOLDER=%CD%
set DESTINATION_FOLDER=%CURRENT_FOLDER%\HHBrowser

:: Luo HHBrowser-kansio, jos se ei vielä ole olemassa
if not exist "%DESTINATION_FOLDER%" (
    echo Luodaan kohdekansio: %DESTINATION_FOLDER%
    mkdir "%DESTINATION_FOLDER%"
) else (
    echo Kohdekansio "%DESTINATION_FOLDER%" on jo olemassa.
)

:: Tarkista, onko Git asennettu
where git >nul 2>nul
if errorlevel 1 (
    echo Git ei ole asennettu. Asennetaan Git...

    :: Lataa Gitin asennustiedosto
    powershell -Command "Invoke-WebRequest -Uri '%GIT_INSTALLER_URL%' -OutFile '%GIT_INSTALLER_PATH%'"
    if %ERRORLEVEL% neq 0 (
        echo Virhe Gitin asennustiedoston latauksessa.
        exit /b %ERRORLEVEL%
    )

    :: Suorita asennus
    echo Asennetaan Git...
    start /wait "" "%GIT_INSTALLER_PATH%" /VERYSILENT /NORESTART
    if %ERRORLEVEL% neq 0 (
        echo Virhe Gitin asennuksessa.
        exit /b %ERRORLEVEL%
    )

    :: Poista asennustiedosto
    del "%GIT_INSTALLER_PATH%"
    if %ERRORLEVEL% neq 0 (
        echo Virhe asennustiedoston poistamisessa.
        exit /b %ERRORLEVEL%
    )
) else (
    echo Git on jo asennettu.
)

:: Siirry kohdekansioon
cd /d "%DESTINATION_FOLDER%"

:: Poista mahdollinen aikaisempi klonattu repositorio
if exist "%DESTINATION_FOLDER%\.git" (
    echo Poistetaan aikaisempi klonattu repositorio...
    rmdir /s /q "%DESTINATION_FOLDER%"
    if %ERRORLEVEL% neq 0 (
        echo Virhe aikaisemman repositorion poistamisessa.
        exit /b %ERRORLEVEL%
    )
)

:: Klonaa GitHub-repositorio
echo Klonataan GitHub-repositorio: %REPO_URL%
git clone %REPO_URL%
if %ERRORLEVEL% neq 0 (
    echo Virhe repositorion kloonaamisessa.
    exit /b %ERRORLEVEL%
)

echo Clone and move complete!
endlocal
pause
