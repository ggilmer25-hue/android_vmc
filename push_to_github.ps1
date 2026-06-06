# Push current project to GitHub and trigger Actions
# Usage: set GITHUB_TOKEN env var or enter PAT when prompted.
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$cwd = Split-Path -Parent $MyInvocation.MyCommand.Definition
Write-Host "Working directory: $cwd"

$possibleGitPaths = @(
    "C:\Program Files\Git\cmd\git.exe",
    "C:\Program Files\Git\bin\git.exe",
    "C:\Program Files (x86)\Git\cmd\git.exe",
    "C:\Program Files (x86)\Git\bin\git.exe"
)

$gitPath = $possibleGitPaths | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $gitPath) {
    Write-Error "No se encontró git en rutas conocidas. Instala Git y vuelve a ejecutar este script."
    exit 2
}

$token = $env:GITHUB_TOKEN
if (-not $token) {
    $token = Read-Host "Introduce tu GitHub Personal Access Token (repo)"
}

if (-not $token) {
    Write-Error "No se proporcionó token. Aborte."
    exit 3
}

Push-Location $cwd
try {
    & $gitPath config --local user.email "actions@github.com"
    & $gitPath config --local user.name "Automated Push"

    if (-not (Test-Path .git)) {
        & $gitPath init
        & $gitPath add .
        & $gitPath commit -m "Add project and CI workflow" 2>$null || Write-Host "No hay cambios para commitear"
    } else {
        & $gitPath add .
        & $gitPath commit -m "Update project and CI workflow" -a 2>$null || Write-Host "No hay cambios para commitear"
    }

    & $gitPath branch -M main
    & $gitPath remote remove origin -ErrorAction SilentlyContinue
    $remote = "https://$($token)@github.com/ggilmer25-hue/android_vmc.git"
    & $gitPath remote add origin $remote
    & $gitPath push -u origin main --force
    Write-Host "Push completado. Revisa GitHub Actions en: https://github.com/ggilmer25-hue/android_vmc/actions"
} finally {
    Pop-Location
}

Write-Host "Recuerda revocar el token desde GitHub si lo incrustaste en el entorno."