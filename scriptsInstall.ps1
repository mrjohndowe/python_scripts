[CmdletBinding()]
param(
    [string]$ProjectPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Color {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Message,

        [ValidateSet("Black", "DarkBlue", "DarkGreen", "DarkCyan", "DarkRed", "DarkMagenta", "DarkYellow", "Gray", "Blue", "Green", "Cyan", "Red", "Magenta", "Yellow", "White")]
        [ConsoleColor]$ForegroundColor = "DarkGreen",

        [ValidateSet("Black", "DarkBlue", "DarkGreen", "DarkCyan", "DarkRed", "DarkMagenta", "DarkYellow", "Gray", "Blue", "Green", "Cyan", "Red", "Magenta", "Yellow", "White")]
        [ConsoleColor]$BackgroundColor = "Black",

        [boolean]$UpperCase
    )

    if ($UpperCase) {
        $Message = $Message.ToUpperInvariant()
    }

    Write-Host $Message `
        -ForegroundColor $ForegroundColor `
        -BackgroundColor $BackgroundColor
    [Console]::ResetColor()
}

function Write-Wait {
    param(
        [string]$Message = "Waiting",
        [int]$Seconds = 3
    )

    for ($i = $Seconds; $i -ge 1; $i--) {
        Write-Host "`r$Message... $i " -NoNewline
        Start-Sleep -Seconds 1
    }

    Write-Host "`r$Message... Done!    "
}


function Write-ColorWait {
    param(
        [string]$Message = "Waiting",
        [ConsoleColor]$ForegroundColor = "White",
        [ConsoleColor]$BackgroundColor = "Black",
        [bool]$UpperCase = $false,
        [int]$Seconds = 5
    )

    if ($UpperCase) {
        $Message = $Message.ToUpperInvariant()
    }

    for ($i = $Seconds; $i -ge 1; $i--) {
        Write-Host "`r$Message... $i " -NoNewline `
            -ForegroundColor $ForegroundColor `
            -BackgroundColor $BackgroundColor

        Start-Sleep -Seconds 1
    }

    Write-Host "`r$Message... Done!    " `
        -ForegroundColor $ForegroundColor `
        -BackgroundColor $BackgroundColor

    [Console]::ResetColor()
}


function Create-Banner {
    $palette = @(
        [ConsoleColor]::DarkCyan,
        [ConsoleColor]::Cyan,
        [ConsoleColor]::Blue,
        [ConsoleColor]::DarkBlue,
        [ConsoleColor]::White,
        [ConsoleColor]::Red
    )
    $banner = @'
  _// //                             _//                     _//                  _//             _// _//
_//    _//               _/          _//                     _//                  _//             _// _//
 _//         _///_/ _///   _/ _//  _/_/ _/ _////             _//_// _//   _//// _/_/ _/   _//     _// _//   _//    _/ _///
   _//     _//    _//   _//_/  _//   _//  _//                _// _//  _//_//      _//   _//  _//  _// _// _/   _//  _//
      _// _//     _//   _//_/   _//  _//    _///             _// _//  _//  _///   _//  _//   _//  _// _//_///// _// _//
_//    _// _//    _//   _//_// _//   _//      _//            _// _//  _//    _//  _//  _//   _//  _// _//_/         _//
  _// //     _///_///   _//_//        _// _// _//            _//_///  _//_// _//   _//   _// _///_///_///  _////   _///
                           _//
'@ -split "`r?`n"

    $width = ($banner | Measure-Object -Property Length -Maximum).Maximum
    $bandWidth = [Math]::Max(1, [Math]::Ceiling($width / $palette.Count))
    Write-Host ('=' * $width) -ForegroundColor Cyan
    foreach ($line in $banner) {
        for ($position = 0; $position -lt $line.Length; $position++) {
            if ([char]::IsWhiteSpace($line[$position])) {
                Write-Host $line[$position] -NoNewline
                continue
            }
            $paletteIndex = [Math]::Min(
                [Math]::Floor($position / $bandWidth),
                $palette.Count - 1
            )
            Write-Host $line[$position] -NoNewline -ForegroundColor $palette[$paletteIndex]
        }
        Write-Host ""
    }
    Write-Host ('=' * $width) -ForegroundColor Cyan
    $title = " Installation Menu "
    $padding = [Math]::Max(0, $width - $title.Length)
    Write-Host (('=' * [Math]::Floor($padding / 2)) + $title + ('=' * [Math]::Ceiling($padding / 2))) `
        -ForegroundColor Green
    [Console]::ResetColor()
    Write-Host ""
}

function Write-NextConfig {
    param(
        [Parameter(Mandatory)]
        [string]$TargetDirectory
    )

    $nextConfigPath = Join-Path $TargetDirectory "next.config.ts"
    $content = @'
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  allowedDevOrigins: ["10.0.0.101", "10.0.0.0/24"],
  // allowedDevOrigins: ["10.0.0.0/24"],
};

export default nextConfig;
'@

    [System.IO.File]::WriteAllText($nextConfigPath, $content, [System.Text.Encoding]::UTF8)
    Write-Color "Updated $nextConfigPath" Green Black
}

function Write-LocalEnvironment {
    param(
        [Parameter(Mandatory)]
        [string]$TargetDirectory
    )

    $environmentPath = Join-Path $TargetDirectory ".env.local"
    $content = @'
# DATABASE_URL=./database/phonebook.sqlite
DATABASE_URL=mysql://scriptsuser:mYhAd1MewFEja@localhost:3306/testscripts

'@

    [System.IO.File]::WriteAllText($environmentPath, $content, [System.Text.Encoding]::UTF8)
    Write-Color "Created/replaced $environmentPath (database URL hidden)" Green Black
}

function Select-ProjectFolders {
    param(
        [Parameter(Mandatory)]
        [string]$Prompt
    )

    $scriptsDirectory = "D:\scripts"
    $candidateFolders = @()
    if (Test-Path -LiteralPath $scriptsDirectory -PathType Container) {
        $candidateFolders = @(
            Get-ChildItem -LiteralPath $scriptsDirectory -Directory -ErrorAction SilentlyContinue |
                Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName "package.json") } |
                Sort-Object -Property Name |
                Select-Object -ExpandProperty FullName
        )
    }

    Write-Color $Prompt Cyan Black 1
    if ($candidateFolders.Count -eq 0) {
        Write-Color "No project folders with package.json were detected under $scriptsDirectory." Yellow Black
    }
    else {
        for ($index = 0; $index -lt $candidateFolders.Count; $index++) {
            Write-Color "$($index + 1). $($candidateFolders[$index])" Green Black
        }
    }
    if ($candidateFolders.Count -gt 1) {
        Write-Color "B. Select all detected folders" Green Black
    }
    Write-Color "C. Enter a custom folder path" Green Black
    Write-Color "M. Return to the main menu" Yellow Black

    while ($true) {
        $choice = (Read-Host "Choose a folder option").Trim()
        if ($choice -match '^\d+$') {
            $index = [int]$choice - 1
            if ($index -ge 0 -and $index -lt $candidateFolders.Count) {
                return $candidateFolders[$index]
            }
        }
        elseif ($choice -match '^(b|both)$' -and $candidateFolders.Count -gt 1) {
            return $candidateFolders
        }
        elseif ($choice -match '^c$') {
            $customPath = (Read-Host "Enter the folder path").Trim().Trim('"')
            if (Test-Path -LiteralPath $customPath -PathType Container) {
                return (Resolve-Path -LiteralPath $customPath).Path
            }
            Write-Color "Folder not found: $customPath" Black Red
        }
        elseif ($choice -match '^m$') {
            return
        }
        else {
            Write-Color "Choose a listed number, B, C, or M." Black Yellow
        }
    }
}

$showMenu = [string]::IsNullOrWhiteSpace($ProjectPath)
$continueRunning = $true

while ($continueRunning) {
    Clear-Host
    Create-Banner

    $runCompatibilityScript = $false
    $configAction = ""
    $ProjectPaths = @()
    $selection = "3"

    if ($showMenu) {
        Write-Color "Select an action:" Green Black 1
        Write-Color "1. Install, build, and run Option A" Green Black 1
        Write-Color "2. Install, build, and run Option B" Green Black 1
        Write-Color "3. Install, build, and run a folder" Green Black 1
        Write-Color "4. Run SQLite/MySQL compatibility script" Green Black 1
        Write-Color "5. Replace next.config.ts in a folder" Green Black 1
        Write-Color "6. Create/replace .env.local in a folder" Green Black 1
        Write-Color "7. Exit" Black Red 1
        $selection = Read-Host "Choose an option [1-7]"
    }

    switch ($selection) {
        "1" { $ProjectPaths = @("D:\scripts\OptionA") }
        "2" { $ProjectPaths = @("D:\scripts\OptionB") }
        "3" {
            if ($showMenu) {
                $ProjectPaths = @(Select-ProjectFolders -Prompt "Select folder(s) to install, build, and run.")
            }
            else {
                $ProjectPaths = @($ProjectPath)
            }
        }
        "4" { $runCompatibilityScript = $true }
        "5" {
            $configAction = "nextConfig"
            $ProjectPaths = @(Select-ProjectFolders -Prompt "Select folder(s) for next.config.ts.")
        }
        "6" {
            $configAction = "environment"
            $ProjectPaths = @(Select-ProjectFolders -Prompt "Select folder(s) for .env.local.")
        }
        "7" {
            Write-ColorWait "Exiting. No more commands will run." Black Red 1
            $continueRunning = $false
        }
        default {
            Write-Color "Invalid selection. Choose a number from 1 through 7." Black Yellow 1
        }
    }

    if (-not $continueRunning) {
        break
    }

    if ($runCompatibilityScript) {
        $compatibilityScript = "D:\scripts\apply_sqlite_mysql_compat.ps1"
        if (-not (Test-Path -LiteralPath $compatibilityScript -PathType Leaf)) {
            Write-Color "Compatibility script not found: $compatibilityScript" Black Red 1
        }
        else {
            & $compatibilityScript
            if (-not $?) {
                Write-Color "Compatibility script failed." Black Red 1
            }
        }
    }
    elseif ($configAction) {
        foreach ($targetPath in $ProjectPaths) {
            $resolvedTargetDirectory = Resolve-Path -LiteralPath $targetPath -ErrorAction SilentlyContinue
            if (-not $resolvedTargetDirectory -or -not (Test-Path -LiteralPath $resolvedTargetDirectory -PathType Container)) {
                Write-Color "Project folder not found: $targetPath" Black Red 1
            }
            elseif ($configAction -eq "nextConfig") {
                Write-NextConfig -TargetDirectory $resolvedTargetDirectory
            }
            else {
                Write-LocalEnvironment -TargetDirectory $resolvedTargetDirectory
            }
        }
    }
    elseif ($selection -in @("1", "2", "3")) {
        foreach ($selectedProjectPath in $ProjectPaths) {
            $resolvedProjectPath = Resolve-Path -LiteralPath $selectedProjectPath -ErrorAction SilentlyContinue
            if (-not $resolvedProjectPath -or -not (Test-Path -LiteralPath $resolvedProjectPath -PathType Container)) {
                Write-Color "Project folder not found: $selectedProjectPath" Black Red 1
                continue
            }

            $packageJsonPath = Join-Path $resolvedProjectPath "package.json"
            if (-not (Test-Path -LiteralPath $packageJsonPath -PathType Leaf)) {
                Write-Color "No package.json found in project directory: $resolvedProjectPath" Black Red 1
                continue
            }
            $packageJson = Get-Content -LiteralPath $packageJsonPath -Raw | ConvertFrom-Json
            if (-not $packageJson.scripts.dev -or -not $packageJson.scripts.build) {
                Write-Color "Project must define npm 'build' and 'dev' scripts." Black Red 1
                continue
            }

            $npmCommand = Get-Command "npm.cmd" -ErrorAction SilentlyContinue
            if (-not $npmCommand) {
                $npmCommand = Get-Command "npm" -ErrorAction SilentlyContinue
            }

            if (-not $npmCommand) {
                Write-Color "npm was not found on PATH." Black Red 1
                continue
            }

            Push-Location -LiteralPath $resolvedProjectPath
            try {
                $commands = @(
                    @{ Label = "npm install"; Arguments = @("install") },
                    @{ Label = "npm install-scripts approve -all"; Arguments = @("install-scripts", "approve", "-all") },
                    @{ Label = "npm run build -- --webpack"; Arguments = @("run", "build", "--", "--webpack") }
                )

                $commandsSucceeded = $true
                foreach ($command in $commands) {
                    Write-Color "Running $($command.Label) ..." Green Black 1
                    $arguments = $command.Arguments
                    & $npmCommand.Source @arguments
                    if ($LASTEXITCODE -ne 0) {
                        Write-Color "$($command.Label) failed with exit code $LASTEXITCODE" Black Red 1
                        $commandsSucceeded = $false
                        break
                    }
                }

                if ($commandsSucceeded) {
                    $devProcess = Start-Process `
                        -FilePath $npmCommand.Source `
                        -ArgumentList @("run", "dev", "--", "--webpack") `
                        -WorkingDirectory $resolvedProjectPath `
                        -PassThru
                    Write-Color "Started npm run dev -- --webpack (PID $($devProcess.Id))." Green Black 1
                }
            }
            finally {
                Pop-Location
            }
        }
    }
    else {
        Write-Color "No action was run." Black Yellow 1
    }

    if (-not $showMenu) {
        $continueRunning = $false
    }
    else {
        Write-ColorWait -Message "Returning to the main menu in 5 seconds..." Cyan Black 1
        $ProjectPath = $null
    }
}
