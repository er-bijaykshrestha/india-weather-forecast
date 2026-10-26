# Push this project to GitHub (Windows PowerShell).
#   .\scripts\push_to_github.ps1 -RepoUrl https://github.com/YOUR-USERNAME/india-weather-forecast.git
param(
    [Parameter(Mandatory = $true)][string]$RepoUrl,
    [string]$Message = "Add India weather analysis and forecasting project"
)

Set-Location (Split-Path -Parent $PSScriptRoot)   # project root

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Git is not installed. Download it from https://git-scm.com/download/win and re-open VS Code." -ForegroundColor Red
    exit 1
}

Write-Host "`n--- Step 1: pre-push checks ---" -ForegroundColor Cyan
python scripts/check_before_push.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nFix the problems above, then run this script again." -ForegroundColor Red
    exit 1
}

Write-Host "`n--- Step 2: stage files ---" -ForegroundColor Cyan
if (-not (Test-Path ".git")) { git init }
git add .
git status --short

$answer = Read-Host "`nCommit and push these files to $RepoUrl ? (y/n)"
if ($answer -ne "y") { Write-Host "Cancelled."; exit 0 }

Write-Host "`n--- Step 3: commit and push ---" -ForegroundColor Cyan
git commit -m $Message
git branch -M main
$remotes = git remote
if ($remotes -contains "origin") { git remote set-url origin $RepoUrl } else { git remote add origin $RepoUrl }
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nDone! Open $($RepoUrl -replace '\.git$','') in your browser." -ForegroundColor Green
} else {
    Write-Host "`nPush failed. Read the message above (sign-in or repo URL problems are the most common)." -ForegroundColor Red
}
