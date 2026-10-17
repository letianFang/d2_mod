[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$D2RPath
)

$ErrorActionPreference = 'Stop'

$gameRoot = [System.IO.Path]::GetFullPath($D2RPath)
$gameExe = Join-Path $gameRoot 'D2R.exe'
if (-not (Test-Path -LiteralPath $gameExe -PathType Leaf)) {
    throw "D2R.exe was not found in the specified directory: $gameRoot"
}

$source = Join-Path $PSScriptRoot 'mods\FarmHub'
$modsRoot = Join-Path $gameRoot 'mods'
$destination = Join-Path $modsRoot 'FarmHub'

New-Item -ItemType Directory -Path $modsRoot -Force | Out-Null
Copy-Item -LiteralPath $source -Destination $modsRoot -Recurse -Force

# Remove only the explicitly retired resource; the game then uses its original.
$retiredEntrance = Join-Path $destination 'FarmHub.mpq\data\hd\roomtiles\act_3_travincal_to_mephisto.json'
if (Test-Path -LiteralPath $retiredEntrance -PathType Leaf) {
    Remove-Item -LiteralPath $retiredEntrance
}

Write-Host "FarmHub installed to: $destination"
Write-Host 'Launch arguments (CN corpse display): -mod FarmHub -txt -assettestmode 1'
Write-Host 'Offline characters only. Read the save-data notes in README.md before first launch.'
