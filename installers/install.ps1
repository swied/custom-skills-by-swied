[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("codex", "claude", "claude-code", "pi", "agy", "antigravity", "all")]
    [string]$Harness,

    [Parameter(Mandatory = $true)]
    [string]$Skill,

    [switch]$Update,
    [switch]$Uninstall,
    [switch]$UseSymlink
)

$ErrorActionPreference = "Stop"

if ($Update -and $Uninstall) {
    throw "Choose only one action: -Update or -Uninstall."
}
if ($Uninstall -and $UseSymlink) {
    throw "-UseSymlink is valid only when installing or updating."
}

$Action = if ($Uninstall) { "uninstall" } elseif ($Update) { "update" } else { "install" }
$RepositoryRoot = Split-Path -Parent $PSScriptRoot
$Source = Join-Path $RepositoryRoot "skills\$Skill"
$MarkerName = ".portable-agent-skill-install"
$MarkerValue = "custom-skills-by-swied:$Skill"

if ($Action -ne "uninstall" -and -not (Test-Path (Join-Path $Source "SKILL.md"))) {
    throw "Skill not found: $Source"
}

function Get-InstalledItem {
    param([Parameter(Mandatory = $true)][string]$Destination)

    Get-Item -Force -ErrorAction SilentlyContinue $Destination
}

function Test-OwnedInstallation {
    param([Parameter(Mandatory = $true)][string]$Destination)

    $Item = Get-InstalledItem $Destination
    if ($null -eq $Item) {
        return $false
    }

    if ($Item.LinkType -eq "SymbolicLink") {
        return [string]$Item.Target -eq $Source
    }

    $Marker = Join-Path $Destination $MarkerName
    return (Test-Path $Marker) -and ((Get-Content -Raw $Marker).TrimEnd() -eq $MarkerValue)
}

function Install-Copy {
    param(
        [Parameter(Mandatory = $true)][string]$DestinationRoot,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    $StagingRoot = Join-Path $DestinationRoot (".$Skill.install." + [guid]::NewGuid().ToString("N"))
    $StagedCopy = Join-Path $StagingRoot $Skill
    New-Item -ItemType Directory -Path $StagingRoot | Out-Null

    try {
        Copy-Item -Recurse -Path $Source -Destination $StagedCopy
        Set-Content -Path (Join-Path $StagedCopy $MarkerName) -Value $MarkerValue

        if ($Action -eq "update") {
            $Previous = Join-Path $StagingRoot "previous"
            Move-Item -Path $Destination -Destination $Previous
            try {
                Move-Item -Path $StagedCopy -Destination $Destination
            }
            catch {
                Move-Item -Path $Previous -Destination $Destination
                throw "Update failed; restored previous installation: $Destination"
            }
        }
        else {
            Move-Item -Path $StagedCopy -Destination $Destination
        }
    }
    finally {
        if (Test-Path $StagingRoot) {
            Remove-Item -Recurse -Force $StagingRoot
        }
    }
}

function Install-Symlink {
    param(
        [Parameter(Mandatory = $true)][string]$DestinationRoot,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    if ($Action -eq "install") {
        New-Item -ItemType SymbolicLink -Path $Destination -Target $Source | Out-Null
        return
    }

    $StagingRoot = Join-Path $DestinationRoot (".$Skill.install." + [guid]::NewGuid().ToString("N"))
    $StagedLink = Join-Path $StagingRoot $Skill
    $Previous = Join-Path $StagingRoot "previous"
    New-Item -ItemType Directory -Path $StagingRoot | Out-Null

    try {
        New-Item -ItemType SymbolicLink -Path $StagedLink -Target $Source | Out-Null
        Move-Item -Path $Destination -Destination $Previous
        try {
            Move-Item -Path $StagedLink -Destination $Destination
        }
        catch {
            Move-Item -Path $Previous -Destination $Destination
            throw "Update failed; restored previous installation: $Destination"
        }
    }
    finally {
        if (Test-Path $StagingRoot) {
            Remove-Item -Recurse -Force $StagingRoot
        }
    }
}

function Manage-Skill {
    param([Parameter(Mandatory = $true)][string]$DestinationRoot)

    $Destination = Join-Path $DestinationRoot $Skill
    New-Item -ItemType Directory -Force -Path $DestinationRoot | Out-Null
    $InstalledItem = Get-InstalledItem $Destination

    switch ($Action) {
        "install" {
            if ($null -ne $InstalledItem) {
                throw "Refusing to replace existing path: $Destination. Use -Update to refresh an installation created by this installer."
            }

            if ($UseSymlink) {
                Install-Symlink $DestinationRoot $Destination
                Write-Host "Installed symlink: $Destination -> $Source"
            }
            else {
                Install-Copy $DestinationRoot $Destination
                Write-Host "Installed copy: $Destination"
            }
        }
        "update" {
            if ($null -eq $InstalledItem) {
                throw "Cannot update missing installation: $Destination. Install it first."
            }
            if (-not (Test-OwnedInstallation $Destination)) {
                throw "Refusing to update path not owned by this installer: $Destination"
            }

            if ($UseSymlink -and $InstalledItem.LinkType -eq "SymbolicLink") {
                Write-Host "Already current (symlink): $Destination -> $Source"
            }
            elseif ($UseSymlink) {
                Install-Symlink $DestinationRoot $Destination
                Write-Host "Updated as symlink: $Destination -> $Source"
            }
            else {
                Install-Copy $DestinationRoot $Destination
                Write-Host "Updated copy: $Destination"
            }
        }
        "uninstall" {
            if ($null -eq $InstalledItem) {
                Write-Host "Not installed: $Destination"
                return
            }
            if (-not (Test-OwnedInstallation $Destination)) {
                throw "Refusing to uninstall path not owned by this installer: $Destination"
            }

            Remove-Item -Recurse -Force $Destination
            Write-Host "Uninstalled: $Destination"
        }
    }
}

function Manage-CodexOrPi {
    Manage-Skill (Join-Path $HOME ".agents\skills")
}

function Manage-Claude {
    Manage-Skill (Join-Path $HOME ".claude\skills")
}

function Manage-Agy {
    Manage-Skill (Join-Path $HOME ".gemini\config\skills")
}

switch ($Harness) {
    { $_ -in @("codex", "pi") } { Manage-CodexOrPi; break }
    { $_ -in @("claude", "claude-code") } { Manage-Claude; break }
    { $_ -in @("agy", "antigravity") } { Manage-Agy; break }
    "all" {
        Manage-CodexOrPi
        Manage-Claude
        Manage-Agy
    }
}
