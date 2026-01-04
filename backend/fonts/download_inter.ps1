$ErrorActionPreference = "Stop"

# Downloads Inter Regular TTF into this folder.
# Source: official Inter site (rsms.me).

$OutFile = Join-Path $PSScriptRoot "Inter-Regular.ttf"
$Url = "https://rsms.me/inter/font-files/Inter-Regular.ttf"

Write-Host "Downloading Inter-Regular.ttf..."
Invoke-WebRequest -Uri $Url -OutFile $OutFile
Write-Host "Saved: $OutFile"
