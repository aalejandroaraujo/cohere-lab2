# ============================================================
# Cohere Lab 2 - One-shot prerequisites install (WINDOWS / PowerShell)
# Runs start to finish in a SINGLE execution: installs Python, Azure CLI,
# VS Code extensions, creates the venv, installs packages, verifies.
#
# Handles the classic "Python installed mid-script but not on PATH yet"
# problem by locating python.exe directly after install (no new terminal needed).
#
# First time only, allow local scripts for your user:
#   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
#   Unblock-File .\install-prereqs.ps1
# Then:  .\install-prereqs.ps1
# ============================================================

$ErrorActionPreference = "Stop"
Write-Host "=== Cohere Lab 2 prereqs - one-shot install (Windows) ===" -ForegroundColor Cyan

# ------------------------------------------------------------
# Locate a REAL python.exe (never the Microsoft Store alias stub).
# Searches PATH first, then known winget/python.org install locations.
# Returns the full path to python.exe, or $null.
# ------------------------------------------------------------
function Find-RealPython {
    # 1) anything on PATH that is not the WindowsApps Store alias
    foreach ($cmd in @("python", "py")) {
        $src = (Get-Command $cmd -ErrorAction SilentlyContinue).Source
        if ($src -and ($src -notlike "*WindowsApps*")) {
            try {
                $v = & $src --version 2>&1
                if ($LASTEXITCODE -eq 0 -and $v -match "Python 3") { return $src }
            } catch { }
        }
    }
    # 2) known install locations (winget / python.org), newest first
    $candidates = @()
    $candidates += Get-ChildItem "$env:LocalAppData\Programs\Python\Python3*\python.exe" -ErrorAction SilentlyContinue
    $candidates += Get-ChildItem "C:\Program Files\Python3*\python.exe" -ErrorAction SilentlyContinue
    $candidates = $candidates | Sort-Object FullName -Descending
    foreach ($c in $candidates) {
        try {
            $v = & $c.FullName --version 2>&1
            if ($LASTEXITCODE -eq 0 -and $v -match "Python 3") { return $c.FullName }
        } catch { }
    }
    return $null
}

# ------------------------------------------------------------
# 1. Python
# ------------------------------------------------------------
Write-Host "`n[1/6] Python..." -ForegroundColor Yellow
$python = Find-RealPython
if (-not $python) {
    Write-Host "Installing Python 3.12 via winget..."
    winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements | Out-Null
    Start-Sleep -Seconds 3
    $python = Find-RealPython   # locate it directly, no new terminal needed
}
if (-not $python) {
    Write-Host "Could not locate python.exe after install." -ForegroundColor Red
    Write-Host "Disable the Store alias (Settings > Apps > Advanced app settings > App execution aliases)," -ForegroundColor Red
    Write-Host "then open a NEW terminal and re-run." -ForegroundColor Red
    exit 1
}
Write-Host "Using Python: $python  ($(& $python --version))" -ForegroundColor Green

# ------------------------------------------------------------
# 2. Azure CLI
# ------------------------------------------------------------
Write-Host "`n[2/6] Azure CLI..." -ForegroundColor Yellow
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    winget install -e --id Microsoft.AzureCLI --accept-package-agreements --accept-source-agreements | Out-Null
    Write-Host "Azure CLI installed (available in new terminals)."
} else {
    Write-Host "Azure CLI present." -ForegroundColor Green
}

# ------------------------------------------------------------
# 3. VS Code + extensions
# ------------------------------------------------------------
Write-Host "`n[3/6] VS Code + extensions..." -ForegroundColor Yellow
if (-not (Get-Command code -ErrorAction SilentlyContinue)) {
    winget install -e --id Microsoft.VisualStudioCode --accept-package-agreements --accept-source-agreements | Out-Null
    Write-Host "VS Code installed. Re-run later to add extensions, or add them in-app." -ForegroundColor Yellow
} else {
    code --install-extension ms-python.python | Out-Null
    code --install-extension ms-toolsai.jupyter | Out-Null
    Write-Host "VS Code extensions installed." -ForegroundColor Green
}

# ------------------------------------------------------------
# 4. Virtual environment (in the current folder)
# ------------------------------------------------------------
Write-Host "`n[4/6] Virtual environment in $(Get-Location)..." -ForegroundColor Yellow
if (-not (Test-Path ".\.venv")) {
    & $python -m venv .venv
}
$venvPy = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
    Write-Host "venv creation failed." -ForegroundColor Red
    exit 1
}
Write-Host "venv ready: $venvPy" -ForegroundColor Green

# ------------------------------------------------------------
# 5. Install packages (call the venv python directly, no activation needed)
# ------------------------------------------------------------
Write-Host "`n[5/6] Installing packages..." -ForegroundColor Yellow
& $venvPy -m pip install --upgrade pip | Out-Null
if (Test-Path ".\requirements.txt") {
    & $venvPy -m pip install -r requirements.txt
} else {
    Write-Host "requirements.txt not found in this folder, skipping package install." -ForegroundColor Yellow
}

# ------------------------------------------------------------
# 6. Verify
# ------------------------------------------------------------
Write-Host "`n[6/6] Verifying..." -ForegroundColor Yellow
& $venvPy --version
try {
    & $venvPy -c "import cohere, requests, numpy, faiss, dotenv; print('Python packages OK')"
    Write-Host "`n=== SUCCESS. Next: copy .env.example to .env, fill endpoints/keys, then: .\.venv\Scripts\python.exe connection_test.py ===" -ForegroundColor Green
} catch {
    Write-Host "Package import failed, review the pip output above." -ForegroundColor Red
}

Write-Host "`nNote: to use 'python' and 'az' in a normal terminal, open a NEW terminal after this script." -ForegroundColor DarkGray
