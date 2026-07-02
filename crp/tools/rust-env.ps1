# Dot-source to set up the Rust build environment for crp-telemetry on this
# Windows host. The default MSVC toolchain cannot link here (VS 2026 is
# installed without the Windows SDK, so kernel32.lib is missing; Git's
# coreutils link.exe also shadows MSVC link on PATH). We therefore build
# with the self-contained GNU toolchain, plus dlltool from WinLibs MinGW
# (installed user-scope via: winget install BrechtSanders.WinLibs.POSIX.UCRT).

$winlibs = Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\BrechtSanders.WinLibs*" -Directory |
    Select-Object -First 1
if (-not $winlibs) { throw "WinLibs not found. Install: winget install BrechtSanders.WinLibs.POSIX.UCRT" }
$mingwBin = Join-Path $winlibs.FullName "mingw64\bin"
if (-not (Test-Path (Join-Path $mingwBin "dlltool.exe"))) { throw "dlltool.exe not found under $mingwBin" }

$env:Path = "$env:USERPROFILE\.cargo\bin;$mingwBin;$env:Path"
$env:CRP_CARGO_TOOLCHAIN = "+stable-x86_64-pc-windows-gnu"
Write-Host "Rust env ready. Use: cargo $env:CRP_CARGO_TOOLCHAIN <cmd> --manifest-path crp/telemetry/Cargo.toml"
