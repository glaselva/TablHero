# run_dev.ps1 - Avvia TablHero in development mode
# Uso: .\run_dev.ps1

Write-Host ""
Write-Host "TABLHERO - Development Mode"
Write-Host ""

# STEP 1: Attiva Virtual Environment
Write-Host "[1/4] Attivando Virtual Environment..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
    Write-Host "[OK] Virtual Environment attivato" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Virtual Environment non trovato!" -ForegroundColor Red
    Write-Host "        Esegui: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# STEP 2: Configura variabili d'ambiente
Write-Host "[2/4] Configurando variabili d'ambiente..." -ForegroundColor Yellow
$env:FLASK_ENV = "development"
$env:FLASK_DEBUG = "True"
Write-Host "      FLASK_ENV = development" -ForegroundColor Green
Write-Host "      FLASK_DEBUG = True" -ForegroundColor Green
Write-Host "[OK] Variabili d'ambiente configurate" -ForegroundColor Green

Write-Host ""

# STEP 3: Installa dipendenze se necessarie
Write-Host "[3/4] Controllando dipendenze..." -ForegroundColor Yellow
$requirementsPath = "requirements.txt"

if (Test-Path $requirementsPath) {
    Write-Host "      [CHECK] requirements.txt trovato" -ForegroundColor Green
    
    # Verifica se Flask è installato (dipendenza principale)
    Write-Host "      [CHECK] Verificando pip packages..." -ForegroundColor Yellow
    
    try {
        # Controlla se Flask è già installato
        $flaskCheck = & pip show flask 2>&1 | Select-String "Name: Flask"
        
        if ($flaskCheck) {
            Write-Host "[OK] Tutte le dipendenze sono già installate" -ForegroundColor Green
        } else {
            Write-Host "      [INSTALL] Installando dipendenze..." -ForegroundColor Yellow
            & pip install -r $requirementsPath -q
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[OK] Dipendenze installate con successo" -ForegroundColor Green
            } else {
                Write-Host "[ERROR] Errore nell'installazione delle dipendenze!" -ForegroundColor Red
                exit 1
            }
        }
    } catch {
        Write-Host "[ERROR] Errore nel verificare dipendenze: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[ERROR] requirements.txt non trovato!" -ForegroundColor Red
    exit 1
}

Write-Host ""

# STEP 4: Avvia l'app
Write-Host "[4/4] Avviando TablHero..." -ForegroundColor Yellow
Write-Host ""
Write-Host "=============================================================" -ForegroundColor Green
Write-Host "Applicazione avviata!" -ForegroundColor Green
Write-Host "Accedi a: http://localhost:5000" -ForegroundColor Green
Write-Host "Premi CTRL+C per fermare l'applicazione" -ForegroundColor Green
Write-Host "=============================================================" -ForegroundColor Green
Write-Host ""

python app.py

Write-Host ""
Write-Host "[INFO] Applicazione fermata" -ForegroundColor Yellow
Write-Host ""
