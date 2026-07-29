[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("codex", "claude", "claude-code", "pi", "agy", "antigravity", "all")]
    [string]$Harness,

    [Parameter(Mandatory = $true)]
    [string]$Skill,

    [switch]$UseSymlink
)

$ErrorActionPreference = "Stop"
$RepositoryRoot = Split-Path -Parent $PSScriptRoot
$Source = Join-Path $RepositoryRoot "skills\$Skill"

if (-not (Test-Path (Join-Path $Source "SKILL.md"))) {
    throw "Skill not found: $Source"
}

function Install-Skill {
    param([Parameter(Mandatory = $true)][string]$DestinationRoot)

    $Destination = Join-Path $DestinationRoot $Skill
    New-Item -ItemType Directory -Force -Path $DestinationRoot | Out-Null

    if (Test-Path $Destination) {
        throw "Refusing to replace existing path: $Destination"
    }

    if ($UseSymlink) {
        New-Item -ItemType SymbolicLink -Path $Destination -Target $Source | Out-Null
        Write-Host "Installed symlink: $Destination -> $Source"
    }
    else {
        Copy-Item -Recurse -Path $Source -Destination $Destination
        Write-Host "Installed copy: $Destination"
    }
}

function Install-CodexOrPi {
    Install-Skill (Join-Path $HOME ".agents\skills")
}

function Install-Claude {
    Install-Skill (Join-Path $HOME ".claude\skills")
}

function Install-Agy {
    Install-Skill (Join-Path $HOME ".gemini\config\skills")
}

switch ($Harness) {
    { $_ -in @("codex", "pi") } { Install-CodexOrPi; break }
    { $_ -in @("claude", "claude-code") } { Install-Claude; break }
    { $_ -in @("agy", "antigravity") } { Install-Agy; break }
    "all" {
        Install-CodexOrPi
        Install-Claude
        Install-Agy
    }
}

