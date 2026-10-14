param(
    [switch]$QuickCheck
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$enginePath = Join-Path $projectRoot 'work\tooling\godot-4-7-2\Godot_v4.7.2-stable_win64_console.exe'
$guiEnginePath = Join-Path $projectRoot 'work\tooling\godot-4-7-2\Godot_v4.7.2-stable_win64.exe'
$gamePath = Join-Path $projectRoot 'game'
$outputPath = Join-Path $projectRoot 'outputs'
$receiptDirectory = Join-Path $env:APPDATA 'Godot\app_userdata\Worlds Between\saves\playtests'

if (-not (Test-Path -LiteralPath $enginePath -PathType Leaf)) {
    throw "Godot executable missing: $enginePath"
}
if (-not (Test-Path -LiteralPath $guiEnginePath -PathType Leaf)) {
    throw "Godot GUI executable missing: $guiEnginePath"
}
if (-not (Test-Path -LiteralPath (Join-Path $gamePath 'project.godot') -PathType Leaf)) {
    throw "Game project missing: $gamePath"
}

if ($QuickCheck) {
    & $enginePath --headless --path $gamePath --quit-after 1
    exit $LASTEXITCODE
}

Write-Host 'Worlds Between - M7 local playtest'
Write-Host 'Start a new game. Complete the three science-region surveys, relay and ruins records, then submit the city report.'
Write-Host 'The game records elapsed time and route events when the report is submitted.'

$receiptPattern = '^rpg-2-star-ocean-the-second_scifi-region_playtest-receipt_m7_\d{8}-\d{6}-[0-9a-f]{8}\.json$'
$before = @()
if (Test-Path -LiteralPath $receiptDirectory -PathType Container) {
    $before = @(Get-ChildItem -LiteralPath $receiptDirectory -File | Where-Object { $_.Name -match $receiptPattern } | ForEach-Object { $_.Name })
}

# The game window is interactive. The web server that calls this script remains hidden.
$gameProcess = Start-Process -FilePath $guiEnginePath -ArgumentList @('--path', ('"' + $gamePath + '"')) -WindowStyle Normal -PassThru -Wait
$gameExitCode = $gameProcess.ExitCode

$newReceipts = @()
if (Test-Path -LiteralPath $receiptDirectory -PathType Container) {
    $newReceipts = @(Get-ChildItem -LiteralPath $receiptDirectory -File | Where-Object { $_.Name -match $receiptPattern -and $before -notcontains $_.Name } | Sort-Object LastWriteTimeUtc -Descending)
}
$receipt = $newReceipts | Select-Object -First 1
if ($receipt) {
    $data = Get-Content -LiteralPath $receipt.FullName -Raw | ConvertFrom-Json
    if ($data.schemaVersion -ne 1 -or $data.project -ne 'rpg-2-star-ocean-the-second' -or $data.milestone -ne 'M7' -or $data.reportCompleted -ne $true) {
        throw "Invalid playtest receipt: $($receipt.FullName)"
    }
    Copy-Item -LiteralPath $receipt.FullName -Destination (Join-Path $outputPath $receipt.Name)
    Write-Host "Playtest receipt copied to: $outputPath"
} else {
    Write-Host 'No city report was submitted in this session, so no completed playtest receipt was copied.'
}

exit $gameExitCode
