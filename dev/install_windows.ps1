# dev/install_windows.ps1
# Windows installation script for Prometheus Daemon
# Requires PowerShell 5.1+ and Administrator privileges for some features

param(
    [switch]$SkipOptional,
    [switch]$Verbose
)

Write-Host "🔧 Installing dependencies for Windows..." -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  Note: Running without administrator privileges. Some features may be limited." -ForegroundColor Yellow
    Write-Host ""
}

# Function to check if a command exists
function Test-Command {
    param($Command)
    return $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

# Function to install with winget if available
function Install-WithWinget {
    param($PackageId, $PackageName)
    
    if (Test-Command "winget") {
        Write-Host "📦 Installing $PackageName via winget..." -ForegroundColor Green
        winget install --id $PackageId --accept-source-agreements --accept-package-agreements
        return $true
    }
    return $false
}

# Check for Python
Write-Host "🐍 Checking Python installation..." -ForegroundColor Cyan
if (Test-Command "python") {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✓ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "   ✗ Python not found. Installing..." -ForegroundColor Yellow
    if (-not (Install-WithWinget "Python.Python.3.11" "Python 3.11")) {
        Write-Host "   Please install Python manually from https://python.org" -ForegroundColor Red
        exit 1
    }
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}

# Check for pip
Write-Host "📦 Checking pip installation..." -ForegroundColor Cyan
if (Test-Command "pip") {
    Write-Host "   ✓ pip found" -ForegroundColor Green
} else {
    Write-Host "   Installing pip..." -ForegroundColor Yellow
    python -m ensurepip --upgrade
}

# Install Python requirements
Write-Host "📚 Installing Python dependencies..." -ForegroundColor Cyan
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    Write-Host "   ✓ Python dependencies installed" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  requirements.txt not found" -ForegroundColor Yellow
}

# Optional: Install Rust (for sandbox/runtime_executor.rs)
if (-not $SkipOptional) {
    Write-Host "🦀 Checking Rust installation..." -ForegroundColor Cyan
    if (Test-Command "rustc") {
        $rustVersion = rustc --version 2>&1
        Write-Host "   ✓ Rust found: $rustVersion" -ForegroundColor Green
    } else {
        Write-Host "   Installing Rust..." -ForegroundColor Yellow
        if (-not (Install-WithWinget "Rustlang.Rust.MSVC" "Rust")) {
            Write-Host "   ⚠️  Please install Rust manually from https://rustup.rs" -ForegroundColor Yellow
        }
    }
}

# Optional: Install FFmpeg (for audio processing)
if (-not $SkipOptional) {
    Write-Host "🎬 Checking FFmpeg installation..." -ForegroundColor Cyan
    if (Test-Command "ffmpeg") {
        Write-Host "   ✓ FFmpeg found" -ForegroundColor Green
    } else {
        Write-Host "   Installing FFmpeg..." -ForegroundColor Yellow
        if (-not (Install-WithWinget "Gyan.FFmpeg" "FFmpeg")) {
            Write-Host "   ⚠️  Please install FFmpeg manually from https://ffmpeg.org" -ForegroundColor Yellow
        }
    }
}

# Create necessary directories
Write-Host "📁 Creating daemon directories..." -ForegroundColor Cyan
$appData = $env:LOCALAPPDATA
$daemonPath = Join-Path $appData "Prometheus Daemon"
$directories = @(
    (Join-Path $daemonPath "Data"),
    (Join-Path $daemonPath "Logs"),
    (Join-Path $daemonPath "Cache"),
    (Join-Path $daemonPath "Config")
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "   ✓ Created: $dir" -ForegroundColor Green
    }
}

# Windows-specific compatibility notice
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  PROMETHEUS DAEMON - WINDOWS COMPATIBILITY MODE" -ForegroundColor White
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "  The daemon is installed and ready to run on Windows." -ForegroundColor White
Write-Host ""
Write-Host "  Note: For FULL symbolic OS capabilities, ThothOS is recommended." -ForegroundColor Yellow
Write-Host "  Windows runs with the following limitations:" -ForegroundColor Yellow
Write-Host "    • No symbolic kernel access" -ForegroundColor Gray
Write-Host "    • Limited sensor integration" -ForegroundColor Gray
Write-Host "    • Compatibility layer enabled" -ForegroundColor Gray
Write-Host "    • Conservative performance mode" -ForegroundColor Gray
Write-Host ""
Write-Host "  The daemon will automatically detect ThothOS and enable" -ForegroundColor White
Write-Host "  full native capabilities when running on it." -ForegroundColor White
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ Daemon environment setup complete on Windows." -ForegroundColor Green
Write-Host ""
Write-Host "To start the daemon, run:" -ForegroundColor Cyan
Write-Host "   python main.py" -ForegroundColor White
Write-Host ""
