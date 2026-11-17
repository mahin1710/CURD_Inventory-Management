# Auto-push script for CURD_Inventory-Management
# Pushes changes to https://github.com/mahin1710/CURD_Inventory-Management every 10 minutes

$repoDir = "C:\Users\mahed\Desktop\CURD_Inventory"
Set-Location $repoDir

$tokenFile = Join-Path $repoDir ".git\github_token"
$githubToken = ""
if (Test-Path $tokenFile) {
    $githubToken = (Get-Content $tokenFile -Raw).Trim()
} elseif ($env:GITHUB_TOKEN) {
    $githubToken = $env:GITHUB_TOKEN.Trim()
}

if ($githubToken) {
    $remoteUrl = "https://$($githubToken)@github.com/mahin1710/CURD_Inventory-Management.git"
    git remote set-url origin $remoteUrl
}

git branch -M main

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  CURD Inventory - GitHub 10-Min Auto-Push" -ForegroundColor Cyan
Write-Host "  Repository: https://github.com/mahin1710/CURD_Inventory-Management" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "Running in background... Checking for changes every 10 minutes (600s)." -ForegroundColor Gray

# Interval in seconds (10 minutes = 600 seconds)
$intervalSeconds = 600

while ($true) {
    try {
        Set-Location $repoDir
        $status = git status --porcelain
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

        if ($status) {
            Write-Host "[$timestamp] Changes detected. Staging and committing..." -ForegroundColor Yellow
            git add .
            git commit -m "Auto-sync update: $timestamp"
            Write-Host "[$timestamp] Pushing to GitHub (origin/main)..." -ForegroundColor Yellow
            
            $env:GIT_TERMINAL_PROMPT = "0"
            $output = git push origin main 2>&1
            Write-Host "[$timestamp] $output" -ForegroundColor Green
            Write-Host "[$timestamp] Successfully synced to GitHub!" -ForegroundColor Green
        } else {
            Write-Host "[$timestamp] Workspace clean. No changes to commit." -ForegroundColor Gray
        }
    } catch {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Write-Host "[$timestamp] Error during auto-push: $_" -ForegroundColor Red
    }

    Start-Sleep -Seconds $intervalSeconds
}
