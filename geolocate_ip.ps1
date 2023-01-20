# Following PS script will read a file, parse IP addresses, remove duplicate entries, gets country of these IP's and retrieves them as a table.
# Usage: run this script by provides file includes IP addresses as parameter

Param(
  [parameter(mandatory=$true)][string]$filename
)

$filename = Get-Content $filename
$file = $filename | sort -unique
$regex = "\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
$matches = [regex]::Matches($file, $regex) | sort -Unique

$records = @()

foreach ($match in $matches) {
    $ip = $match.Value
    $country = (Invoke-WebRequest "http://ip-api.com/json/$ip" -UseBasicParsing).Content | ConvertFrom-Json
    ### Write-Host "IP: $ip  Country: $($country.country)" 

    $records += New-Object PSObject -Property @{
        IP = $ip
        Country = $($country.country)
}
}

$records | Out-GridView -Title "IP by Country"
