### Kaspersky Scan Engine - Download and Scan 
# This short script was created for a Kaspersky Scan Engine project based on specific customer requirements.
# KSE does not have download and scan feature, and we are using this script as cover that requirement.
# It downloads a file from given URL, sends a request to Kaspersky Scan Engine, and retrieves results.

# Example command:
# powershell.exe .\KSE_DownloadAndScan.ps1 127.0.0.1:1234 https://secure.eYcar.org/eYcar.com
# Make sure that the URL includes full filename with extension. If there is a suffix in URL (like ?dl=1) it will not accept.

# Argument 0: KSE Server IP and Port
# Argument 1: File to be downloaded and scanned

$url = $args[1] 
$kse_server1 = $args[0]
$kse_server = "http://" + $kse_server1 + "/api/v3.0/scanfile"
Write-Output "KSE Server Address =" $kse_server

## Downloader

$outFolderPath = "C:\Temp"

# Check if folder exists, if yes continue, if not create and continue 
if (Test-Path $outFolderPath) {

$outFilePath = Join-Path $outFolderPath (Split-Path -Leaf $url)
Invoke-WebRequest -Uri $url -OutFile $outFilePath
$outFilePath = $outFilePath -replace "\\", "\/"
Write-Output $outFilePath
}

else 
{New-Item $outFolderPath -ItemType Directory

$outFilePath = Join-Path $outFolderPath (Split-Path -Leaf $url)
Invoke-WebRequest -Uri $url -OutFile $outFilePath
$outFilePath = $outFilePath -replace "\\", "\/"
Write-Output $outFilePath
}

## HTTP Request details

$headers = "Content-Type", "application/json"
$request = 
 @"
{
    `"timeout`": `"10000`",
    `"object`": `"$($outFilePath)`"
}
"@

# Time counter
$StartTime = $(get-date)

# HTTP Request
Invoke-RestMethod $kse_server -Method 'POST'  -Body $request

# Time counter
Write-Output ("Time Spent", "{0}" -f ($(get-date)-$StartTime))

# Arbitrary sleep
Start-Sleep -Seconds 1

# Deletes downloaded and scanned item
Remove-Item -Path $outFilePath -Force 
