# Wispy Puff VR - PREVIEW LOCALE sur PC (sans casque)
# Double-clic droit > "Executer avec PowerShell"  (ou ./preview.ps1 dans un terminal)
# Ouvre la scene 3D dans ton navigateur. Clic-glisser = tourner, molette = zoom.
# Laisse cette fenetre OUVERTE pendant que tu regardes ; ferme-la pour arreter.
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
Write-Host "Preview locale : http://localhost:8080/  (Ctrl+C ou ferme la fenetre pour arreter)" -ForegroundColor Cyan
Start-Sleep -Milliseconds 800
Start-Process "http://localhost:8080/"
python -m http.server 8080
