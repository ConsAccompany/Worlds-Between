param(
    [switch]$QuickCheck
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$enginePath = Join-Path $projectRoot 'work\tooling\godot-4-7-2\Godot_v4.7.2-stable_win64_console.exe'
$gamePath = Join-Path $projectRoot 'game'
$outputPath = Join-Path $projectRoot 'outputs'

if (-not (Test-Path -LiteralPath $enginePath -PathType Leaf)) {
    throw "Godot executable missing: $enginePath"
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

& $enginePath --path $gamePath 2>&1 | Tee-Object -Variable gameOutput
$gameExitCode = $LASTEXITCODE

$receiptLine = $gameOutput | ForEach-Object { [string]$_ } | Where-Object { $_ -match '^PLAYTEST_RECEIPT (.+)$' } | Select-Object -Last 1
if ($receiptLine -and $receiptLine -match '^PLAYTEST_RECEIPT (.+)$') {
    $receiptPath = $Matches[1]
    $expectedDirectory = Join-Path $env:APPDATA 'Godot\app_userdata\Worlds Between\saves\playtests'
    $resolvedReceipt = (Resolve-Path -LiteralPath $receiptPath).Path
    $resolvedDirectory = (Resolve-Path -LiteralPath $expectedDirectory).Path
    if (-not $resolvedReceipt.StartsWith($resolvedDirectory + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Unexpected receipt location: $resolvedReceipt"
    }
    Copy-Item -LiteralPath $resolvedReceipt -Destination (Join-Path $outputPath (Split-Path -Leaf $resolvedReceipt))
    Write-Host "Playtest receipt copied to: $outputPath"
} else {
    Write-Host 'No city report was submitted in this session, so no completed playtest receipt was copied.'
}

exit $gameExitCode
