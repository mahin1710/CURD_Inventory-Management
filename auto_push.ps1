# STOCKMASTER — PROMPT 02: DATABASE FOUNDATION

Continue the existing StockMaster project.

Set up SQLite with SQLAlchemy ORM.

Requirements:
1. Configure database.py.
2. Create a persistent SQLite database file.
3. Configure SQLAlchemy engine and session management.
4. Create models.py.
5. Create Product, Category and StockMovement database models.
6. Define primary keys and foreign keys.
7. Define relationships:
- One category has multiple products.
- One product has multiple stock movements.
8. Add created_at and updated_at fields where appropriate.
9. Enable foreign key constraints.
10. Create database tables automatically during application initialization.
11. Verify database connection and table creation.

Do not implement CRUD APIs yet.

Preserve the existing application and verify everything works before stopping.# Auto-push script for CURD_Inventory-Management
# Pushes changes to https://github.com/mahin1710/CURD_Inventory-Management every 10 minutes

$repoDir = "C:\Users\mahed\Desktop\CURD_Inventory"
Set-Location $repoDir

$logFile = Join-Path $repoDir ".git\auto_push.log"
$tokenFile = Join-Path $repoDir ".git\github_token"
$githubToken = ""
if (Test-Path $tokenFile) {
    $githubToken = (Get-Content $tokenFile -Raw).Trim()
}
elseif ($env:GITHUB_TOKEN) {
    $githubToken = $env:GITHUB_TOKEN.Trim()
}

if ($githubToken) {
    $remoteUrl = "https://$($githubToken)@github.com/mahin1710/CURD_Inventory-Management.git"
    git remote set-url origin $remoteUrl
}

git branch -M main

function Log-Msg([string]$msg, [string]$color = "White") {
    $line = "[$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))] $msg"
    Write-Host $line -ForegroundColor $color
    Add-Content -Path $logFile -Value $line -ErrorAction SilentlyContinue
}

Log-Msg "===================================================" "Cyan"
Log-Msg "  CURD Inventory - GitHub 10-Min Auto-Push" "Cyan"
Log-Msg "  Repository: https://github.com/mahin1710/CURD_Inventory-Management" "Green"
Log-Msg "===================================================" "Cyan"
Log-Msg "Monitoring started. Checking for changes every 10 minutes (600s)." "Gray"

$intervalSeconds = 600

while ($true) {
    try {
        Set-Location $repoDir
        $status = git status --porcelain

        if ($status) {
            Log-Msg "Changes detected. Staging and committing..." "Yellow"
            git add .
            $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
            git commit -m "Auto-sync update: $timestamp"
            Log-Msg "Pushing to GitHub (origin/main)..." "Yellow"
            
            $env:GIT_TERMINAL_PROMPT = "0"
            $output = git push origin main 2>&1
            Log-Msg "$output" "Green"
            Log-Msg "Successfully synced to GitHub!" "Green"
        }
        else {
            Log-Msg "Workspace clean. No changes to commit." "Gray"
        }
    }
    catch {
        Log-Msg "Error during auto-push: $_" "Red"
    }

    Start-Sleep -Seconds $intervalSeconds
}
