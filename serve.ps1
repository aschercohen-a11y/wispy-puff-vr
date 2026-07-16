# Wispy Puff VR - lance le serveur local + le tunnel HTTPS (cloudflared)
# Usage : clic droit > "Executer avec PowerShell", ou dans un terminal : ./serve.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host "== Serveur local sur http://localhost:8080 ==" -ForegroundColor Cyan
$server = Start-Process -FilePath "python" -ArgumentList "-m","http.server","8080" -PassThru -WindowStyle Minimized

Start-Sleep -Seconds 1
Write-Host "== Tunnel HTTPS (cloudflared) - l'URL a ouvrir dans le Quest s'affiche ci-dessous ==" -ForegroundColor Cyan
Write-Host "   (Ctrl+C pour tout arreter)" -ForegroundColor DarkGray
try {
  & "$root\tools\cloudflared.exe" tunnel --url http://localhost:8080
} finally {
  if ($server -and -not $server.HasExited) { Stop-Process -Id $server.Id -Force }
  Write-Host "Serveur arrete." -ForegroundColor Yellow
}
