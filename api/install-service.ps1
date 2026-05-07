# install-service.ps1
# Sets up makemoney journal infrastructure as Windows services + scheduled tasks
# Run once as Administrator

$WebDir = "C:\Users\dansk\Claude\web-makemoney"
$Python = "python"

Write-Host "=== makemoney.gobizit.ai — Service Setup ===" -ForegroundColor Cyan

# ── 1. Check pip dependencies ────────────────────────────────────────────────
Write-Host "`n[1/4] Installing Python dependencies..."
& $Python -m pip install flask requests --quiet
Write-Host "  Dependencies OK" -ForegroundColor Green

# ── 2. Install Flask subscriber API as NSSM service ─────────────────────────
Write-Host "`n[2/4] Setting up Flask API service (NSSM)..."
$nssm = "nssm"
if (-not (Get-Command $nssm -ErrorAction SilentlyContinue)) {
    Write-Host "  NSSM not found. Install with: winget install nssm" -ForegroundColor Yellow
    Write-Host "  Then re-run this script."
} else {
    & $nssm install makemoney-api $Python "$WebDir\api\subscribe.py"
    & $nssm set makemoney-api AppDirectory $WebDir
    & $nssm set makemoney-api DisplayName "Make Money AI - Subscriber API"
    & $nssm set makemoney-api Description "Flask API for makemoney.gobizit.ai subscriber capture"
    & $nssm set makemoney-api AppStdout "$WebDir\api\subscribe.log"
    & $nssm set makemoney-api AppStderr "$WebDir\api\subscribe-error.log"
    & $nssm start makemoney-api
    Write-Host "  Flask API service installed + started on port 5055" -ForegroundColor Green
}

# ── 3. Register daily journal generator (Task Scheduler) ────────────────────
Write-Host "`n[3/4] Registering daily journal generator (08:30 daily)..."

$Action = New-ScheduledTaskAction `
    -Execute $Python `
    -Argument "$WebDir\api\generate_journal.py --what both" `
    -WorkingDirectory $WebDir

$Trigger = New-ScheduledTaskTrigger -Daily -At "08:30AM"

$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 5) `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false

Register-ScheduledTask `
    -TaskName "makemoney-daily-journal" `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description "Daily journal generator for makemoney.gobizit.ai — runs both Danny review + AI actions log" `
    -Force

Write-Host "  Task registered: makemoney-daily-journal @ 08:30 daily" -ForegroundColor Green

# ── 4. Register daily notifier (09:00 daily — after generator runs) ──────────
Write-Host "`n[4/4] Registering daily notifier (09:00 daily)..."

$NotifyAction = New-ScheduledTaskAction `
    -Execute $Python `
    -Argument "$WebDir\api\notify_subscribers.py --entry $WebDir\journals\latest.html --frequency daily" `
    -WorkingDirectory $WebDir

$NotifyTrigger = New-ScheduledTaskTrigger -Daily -At "09:00AM"

Register-ScheduledTask `
    -TaskName "makemoney-daily-notify" `
    -Action $NotifyAction `
    -Trigger $NotifyTrigger `
    -Settings $Settings `
    -Description "Daily email notification for makemoney.gobizit.ai daily subscribers" `
    -Force

Write-Host "  Task registered: makemoney-daily-notify @ 09:00 daily" -ForegroundColor Green

# ── Summary ──────────────────────────────────────────────────────────────────
Write-Host "`n=== Setup Complete ===" -ForegroundColor Cyan
Write-Host "Services:"
Write-Host "  makemoney-api      - Flask subscriber API (port 5055)"
Write-Host "  makemoney-daily-journal - Daily journal generator (08:30)"
Write-Host "  makemoney-daily-notify  - Daily email notifier (09:00)"
Write-Host ""
Write-Host "NEXT STEPS (required before going live):"
Write-Host "  1. Add ZOHO_CLIENT_ID + ZOHO_CLIENT_SECRET to:"
Write-Host "     C:\Users\dansk\.claude\secrets\make-money\.env"
Write-Host "  2. Update Caddyfile with snippet from:"
Write-Host "     C:\Users\dansk\Claude\web-makemoney\api\caddy-snippet.txt"
Write-Host "  3. Reload Caddy: caddy reload --config <path-to-Caddyfile>"
Write-Host ""
Write-Host "Test subscriber capture:"
Write-Host '  curl -X POST http://127.0.0.1:5055/api/subscribe -H "Content-Type: application/json" -d "{\"email\":\"test@example.com\",\"frequency\":\"daily\"}"'
