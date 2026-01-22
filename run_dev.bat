@echo off
REM run_dev.bat - Avvia TablHero in development mode (Windows CMD)
REM Uso: run_dev.bat

setlocal enabledelayedexpansion

echo.
echo ════════════════════════════════════════════════════════════════
echo          TABLHERO - Development Mode
echo ════════════════════════════════════════════════════════════════
echo.

REM STEP 1: Attiva Virtual Environment
echo [1/4] Attivando Virtual Environment...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo [OK] Virtual Environment attivato
) else (
    echo [ERROR] Virtual Environment non trovato!
    echo Esegui: python -m venv venv
    pause
    exit /b 1
)

echo.

REM STEP 2: Configura variabili d'ambiente
echo [2/4] Configurando variabili d'ambiente...
set FLASK_ENV=development
set FLASK_DEBUG=True
echo    FLASK_ENV = development
echo    FLASK_DEBUG = True
echo [OK] Variabili d'ambiente configurate

echo.

REM STEP 3: Installa dipendenze se necessarie
echo [3/4] Controllando dipendenze...
if exist requirements.txt (
    echo      [CHECK] requirements.txt trovato
    echo      [CHECK] Verificando pip packages...
    
    REM Controlla se Flask è installato (dipendenza principale)
    pip show flask >nul 2>&1
    if errorlevel 1 (
        echo      [INSTALL] Installando dipendenze...
        pip install -r requirements.txt -q
        if errorlevel 1 (
            echo [ERROR] Errore nell'installazione delle dipendenze!
            pause
            exit /b 1
        )
        echo [OK] Dipendenze installate con successo
    ) else (
        echo [OK] Tutte le dipendenze sono già installate
    )
) else (
    echo [ERROR] requirements.txt non trovato!
    pause
    exit /b 1
)

echo.

REM STEP 4: Avvia l'app
echo [4/4] Avviando TablHero...
echo.
echo ════════════════════════════════════════════════════════════════
echo  Applicazione avviata! Accedi a: http://localhost:5000
echo  Premi CTRL+C per fermare l'applicazione
echo ════════════════════════════════════════════════════════════════
echo.

python app.py

echo.
echo [INFO] Applicazione fermata
echo.

pause
