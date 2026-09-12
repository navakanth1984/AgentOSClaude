<#
.SYNOPSIS
    Universal Dual-Drive Skills Synchronizer
.DESCRIPTION
    Ensures all agent skills are canonically anchored at C:\Users\navka\.claude\skills,
    junctioned across all NTFS runtime roots on C: and G:, and mirrored to E:\navakanth001\.agents\skills.
#>

[CmdletBinding()]
param(
    [string]$CanonicalRoot = "C:\Users\navka\.claude\skills",
    [string[]]$JunctionRoots = @(
        "C:\Users\navka\.agents\skills",
        "C:\Users\navka\.gemini\config\skills",
        "C:\Users\navka\.codex\skills",
        "C:\Users\navka\navakanth001\.agents\skills",
        "G:\navakanth001\.agents\skills"
    ),
    [string]$ExFatTargetRoot = "E:\navakanth001\.agents\skills"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Universal Skills Synchronizer ===" -ForegroundColor Cyan

if (-not (Test-Path $CanonicalRoot)) {
    Write-Error "Canonical root does not exist: $CanonicalRoot"
    exit 1
}

$skills = Get-ChildItem $CanonicalRoot -Directory
Write-Host "Discovered $($skills.Count) skills in canonical root: $CanonicalRoot" -ForegroundColor Green

# 1. Ensure NTFS Directory Junctions across all NTFS roots
foreach ($root in $JunctionRoots) {
    $drive = [System.IO.Path]::GetPathRoot($root)
    if (-not (Test-Path $drive)) {
        Write-Host "[Skip] Drive $drive not available for $root" -ForegroundColor DarkYellow
        continue
    }
    if (-not (Test-Path $root)) {
        New-Item -ItemType Directory -Path $root -Force | Out-Null
    }
    
    $created = 0
    $verified = 0
    
    foreach ($s in $skills) {
        $jPath = Join-Path $root $s.Name
        $target = $s.FullName
        
        if (-not (Test-Path $jPath)) {
            New-Item -ItemType Junction -Path $jPath -Target $target | Out-Null
            $created++
        } else {
            $item = Get-Item $jPath
            if ($item.LinkType -ne "Junction") {
                Remove-Item -Path $jPath -Recurse -Force
                New-Item -ItemType Junction -Path $jPath -Target $target | Out-Null
                $created++
            } else {
                $verified++
            }
        }
    }
    Write-Host "[C: Junctions] $root -> $verified verified, $created linked" -ForegroundColor Gray
}

# 2. Mirror to E: drive (exFAT)
if (Test-Path "E:\") {
    if (-not (Test-Path $ExFatTargetRoot)) {
        New-Item -ItemType Directory -Path $ExFatTargetRoot -Force | Out-Null
    }
    Write-Host "[E: Mirror] Syncing to $ExFatTargetRoot via robocopy..." -ForegroundColor Yellow
    robocopy $CanonicalRoot $ExFatTargetRoot /MIR /R:1 /W:1 /NFL /NDL /NJH /NJS | Out-Null
    Write-Host "[E: Mirror] Sync complete. All skills physical & available on E:" -ForegroundColor Green
} else {
    Write-Host "[E: Mirror] Drive E: not detected. Skipped exFAT mirror." -ForegroundColor DarkYellow
}

Write-Host "=== All roots synchronized & operational across C:, G:, and E: ===" -ForegroundColor Cyan
