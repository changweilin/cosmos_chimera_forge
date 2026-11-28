<#
.SYNOPSIS
Migrate staged files from <repo>/cosmos_chimera into the sibling cosmos_chimera repository
with conflict detection, 3-way merge, rollback, formatting, validation, and Conventional Commit support.

.DESCRIPTION
Reads cosmos_chimera/manifest.json, verifies staged file SHA-256 hashes, checks git state and
target conflicts (using _base/ snapshots for 3-way merge on diverged update targets), applies
changes inside a rollback transaction, optionally formats migrated files per .editorconfig and
.gitattributes, optionally runs target repository checks, and optionally creates a scoped
Conventional Commit containing only the manifest files.

.EXAMPLE
powershell -ExecutionPolicy Bypass -File tools/migrate_cosmos_chimera_staging.ps1 -DryRun -Commit

.EXAMPLE
powershell -ExecutionPolicy Bypass -File tools/migrate_cosmos_chimera_staging.ps1 -Format -RunChecks

.EXAMPLE
powershell -ExecutionPolicy Bypass -File tools/migrate_cosmos_chimera_staging.ps1 -Commit
#>
[CmdletBinding()]
param(
    [string]$StagingDir,
    [string]$TargetRepo,
    [switch]$DryRun,
    [switch]$Move,
    [switch]$Force,
    [switch]$Format,
    [switch]$RunChecks,
    [switch]$SkipChecks,
    [switch]$Commit,
    [string]$CommitMessage,
    [switch]$RequireCleanRepo
)

$ErrorActionPreference = "Stop"

$forgeRoot = Split-Path -Parent $PSScriptRoot
if (-not $StagingDir) {
    $StagingDir = Join-Path $forgeRoot "cosmos_chimera"
}
if (-not $TargetRepo) {
    $TargetRepo = Join-Path (Split-Path -Parent $forgeRoot) "cosmos_chimera"
}

$shouldFormat = [bool]($Format -or $Commit)
$shouldRunChecks = [bool](($RunChecks -or $Commit) -and (-not $SkipChecks))

function Get-FileSha256Lower {
    param([Parameter(Mandatory = $true)][string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Invoke-GitCapture {
    param(
        [Parameter(Mandatory = $true)][string]$Repo,
        [Parameter(Mandatory = $true)][string[]]$GitArgs
    )
    $prev = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & git -C $Repo @GitArgs 2>&1
        $code = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $prev
    }
    $text = ($output | ForEach-Object { $_.ToString() }) -join "`n"
    return [pscustomobject]@{
        ExitCode = $code
        Output   = $text.Trim()
    }
}

function Invoke-ThreeWayMerge {
    param(
        [Parameter(Mandatory = $true)][string]$TargetFile,
        [Parameter(Mandatory = $true)][string]$BaseFile,
        [Parameter(Mandatory = $true)][string]$StagedFile,
        [Parameter(Mandatory = $true)][string]$OutFile
    )
    $pyCode = @'
import subprocess, sys
dst, base, src, out_path = sys.argv[1:5]
res = subprocess.run(
    ["git", "merge-file", "-p", "-L", "target", "-L", "base", "-L", "staged", dst, base, src],
    capture_output=True,
)
if res.returncode == 0:
    with open(out_path, "wb") as f:
        f.write(res.stdout)
sys.exit(res.returncode)
'@
    $pyFile = Join-Path ([System.IO.Path]::GetTempPath()) ("cosmimera_merge_" + [System.Guid]::NewGuid().ToString("N") + ".py")
    [System.IO.File]::WriteAllText($pyFile, $pyCode, (New-Object System.Text.UTF8Encoding($false)))
    $prev = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & python $pyFile $TargetFile $BaseFile $StagedFile $OutFile 2>&1
        $code = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $prev
        if (Test-Path -LiteralPath $pyFile -PathType Leaf) {
            Remove-Item -LiteralPath $pyFile -Force
        }
    }
    return [pscustomobject]@{
        ExitCode = $code
        Output   = (($output | ForEach-Object { $_.ToString() }) -join "`n").Trim()
    }
}

function Format-TargetFiles {
    param([Parameter(Mandatory = $true)][string[]]$Paths)
    $pyCode = @'
import json, sys
from pathlib import Path

for raw_path in sys.argv[1:]:
    p = Path(raw_path)
    raw = p.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    text = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    ext = p.suffix.lower()
    if ext == ".json":
        def reject_const(s):
            raise ValueError(f"Nonstandard JSON constant {s!r} in {p}")
        obj = json.loads(text, parse_constant=reject_const)
        formatted = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
    elif ext == ".md":
        # .editorconfig: [*.md] trim_trailing_whitespace = false
        formatted = text.rstrip("\n") + "\n"
    else:
        lines = [ln.rstrip(" \t") for ln in text.split("\n")]
        formatted = "\n".join(lines).rstrip("\n") + "\n"
    p.write_bytes(formatted.encode("utf-8"))
'@
    $pyFile = Join-Path ([System.IO.Path]::GetTempPath()) ("cosmimera_fmt_" + [System.Guid]::NewGuid().ToString("N") + ".py")
    [System.IO.File]::WriteAllText($pyFile, $pyCode, (New-Object System.Text.UTF8Encoding($false)))
    $prev = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & python $pyFile @Paths 2>&1
        $code = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $prev
        if (Test-Path -LiteralPath $pyFile -PathType Leaf) {
            Remove-Item -LiteralPath $pyFile -Force
        }
    }
    if ($code -ne 0) {
        $msg = ($output | ForEach-Object { $_.ToString() }) -join "`n"
        throw "Formatting failed (exit $code): $msg"
    }
}

if (-not (Test-Path -LiteralPath $StagingDir -PathType Container)) {
    Write-Error "Staging directory not found: $StagingDir"
    exit 2
}
$manifestPath = Join-Path $StagingDir "manifest.json"
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    Write-Error "Staging manifest not found: $manifestPath"
    exit 2
}
if (-not (Test-Path -LiteralPath $TargetRepo -PathType Container)) {
    Write-Error "Target cosmos_chimera repository not found: $TargetRepo"
    exit 2
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $manifest.files -or $manifest.files.Count -eq 0) {
    Write-Error "No files listed in manifest: $manifestPath"
    exit 2
}

$commitSubject = if ($CommitMessage) { $CommitMessage.Trim() } else { [string]$manifest.default_commit_subject }
if ($Commit) {
    $ccRegex = '^(feat|fix|docs|refactor|test|chore|build|ci|perf|style)(\([a-z0-9,._/-]+\))?!?: .+'
    if (-not $commitSubject -or ($commitSubject -notmatch $ccRegex)) {
        Write-Error "Invalid Conventional Commit subject: '$commitSubject'"
        exit 2
    }
}

$manifestRelPaths = @($manifest.files | ForEach-Object { $_.path })
$gitCheck = Invoke-GitCapture -Repo $TargetRepo -GitArgs @("rev-parse", "--is-inside-work-tree")
$isGitRepo = ($gitCheck.ExitCode -eq 0 -and $gitCheck.Output -eq "true")

if ($Commit -and -not $isGitRepo) {
    Write-Error "Cannot use -Commit because target directory is not a git repository: $TargetRepo"
    exit 2
}

$conflicts = @()

if ($isGitRepo) {
    foreach ($headName in @("MERGE_HEAD", "REBASE_HEAD", "CHERRY_PICK_HEAD")) {
        $gp = Invoke-GitCapture -Repo $TargetRepo -GitArgs @("rev-parse", "--git-path", $headName)
        if ($gp.ExitCode -eq 0 -and $gp.Output) {
            $headPath = if ([System.IO.Path]::IsPathRooted($gp.Output)) { $gp.Output } else { Join-Path $TargetRepo $gp.Output }
            if (Test-Path -LiteralPath $headPath) {
                $conflicts += "GIT_OPERATION_IN_PROGRESS: $headName exists in target repository"
            }
        }
    }

    if ($RequireCleanRepo) {
        $fullStatus = Invoke-GitCapture -Repo $TargetRepo -GitArgs @("status", "--porcelain")
        if ($fullStatus.ExitCode -eq 0 -and $fullStatus.Output) {
            $conflicts += "REPO_NOT_CLEAN: target repository has uncommitted changes"
        }
    }

    $targetStatus = Invoke-GitCapture -Repo $TargetRepo -GitArgs (@("status", "--porcelain", "--") + $manifestRelPaths)
    if ($targetStatus.ExitCode -eq 0 -and $targetStatus.Output -and -not $Force) {
        foreach ($line in ($targetStatus.Output -split "`n")) {
            if ($line.Trim()) {
                $conflicts += "TARGET_PATH_DIRTY: $($line.Trim()) (commit/stash target path or use -Force)"
            }
        }
    }

    if ($Commit) {
        $staged = Invoke-GitCapture -Repo $TargetRepo -GitArgs @("diff", "--cached", "--name-only")
        if ($staged.ExitCode -eq 0 -and $staged.Output) {
            $manifestSet = New-Object 'System.Collections.Generic.HashSet[string]'
            foreach ($p in $manifestRelPaths) { [void]$manifestSet.Add($p) }
            foreach ($sPath in ($staged.Output -split "`n")) {
                $trimmed = $sPath.Trim()
                if ($trimmed -and -not $manifestSet.Contains($trimmed)) {
                    $conflicts += "UNRELATED_STAGED_CHANGES: index already stages '$trimmed'; unstage it before -Commit"
                }
            }
        }
    }
}

$mergeTempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("cosmimera_merge_" + [System.Guid]::NewGuid().ToString("N"))
$plan = @()

try {
    foreach ($entry in $manifest.files) {
        $rel = $entry.path -replace "/", [System.IO.Path]::DirectorySeparatorChar
        $src = Join-Path $StagingDir $rel
        $dst = Join-Path $TargetRepo $rel
        $expectedStaged = ([string]$entry.staged_sha256).ToLowerInvariant()

        if (-not (Test-Path -LiteralPath $src -PathType Leaf)) {
            $conflicts += "MISSING_STAGED: $src"
            continue
        }
        $actualStaged = Get-FileSha256Lower -Path $src
        if ($actualStaged -ne $expectedStaged) {
            $conflicts += "STAGED_HASH_MISMATCH: $($entry.path) (expected $expectedStaged, got $actualStaged)"
            continue
        }

        $dstExists = Test-Path -LiteralPath $dst -PathType Leaf
        if (-not $dstExists) {
            if ($entry.action -eq "update" -and -not $Force) {
                $conflicts += "MISSING_TARGET_FOR_UPDATE: $($entry.path) (use -Force to create)"
                continue
            }
            $plan += [pscustomobject]@{
                RelPath    = $entry.path
                Source     = $src
                CopySource = $src
                Target     = $dst
                Op         = "CREATE"
                Sha256     = $expectedStaged
            }
            continue
        }

        $dstSha = Get-FileSha256Lower -Path $dst
        if ($dstSha -eq $expectedStaged) {
            $plan += [pscustomobject]@{
                RelPath    = $entry.path
                Source     = $src
                CopySource = $src
                Target     = $dst
                Op         = "SKIP"
                Sha256     = $expectedStaged
            }
            continue
        }

        if ($entry.action -eq "create") {
            if ($Force) {
                $plan += [pscustomobject]@{
                    RelPath    = $entry.path
                    Source     = $src
                    CopySource = $src
                    Target     = $dst
                    Op         = "OVERWRITE"
                    Sha256     = $expectedStaged
                }
            }
            else {
                $conflicts += "TARGET_EXISTS_DIFFERENT: $($entry.path) (target sha=$dstSha; use -Force to overwrite)"
            }
            continue
        }

        if ($entry.action -eq "update") {
            $expectedBase = ([string]$entry.expected_base_sha256).ToLowerInvariant()
            if ($dstSha -eq $expectedBase) {
                $plan += [pscustomobject]@{
                    RelPath    = $entry.path
                    Source     = $src
                    CopySource = $src
                    Target     = $dst
                    Op         = "UPDATE"
                    Sha256     = $expectedStaged
                }
            }
            elseif ($Force) {
                $plan += [pscustomobject]@{
                    RelPath    = $entry.path
                    Source     = $src
                    CopySource = $src
                    Target     = $dst
                    Op         = "OVERWRITE"
                    Sha256     = $expectedStaged
                }
            }
            elseif ($entry.base_path) {
                $baseRel = $entry.base_path -replace "/", [System.IO.Path]::DirectorySeparatorChar
                $baseFile = Join-Path $StagingDir $baseRel
                if (-not (Test-Path -LiteralPath $baseFile -PathType Leaf)) {
                    $conflicts += "MISSING_BASE_SNAPSHOT: $($entry.base_path)"
                    continue
                }
                if (-not (Test-Path -LiteralPath $mergeTempDir -PathType Container)) {
                    New-Item -ItemType Directory -Path $mergeTempDir -Force | Out-Null
                }
                $mergedOut = Join-Path $mergeTempDir ($entry.path -replace "/", "__")
                $mRes = Invoke-ThreeWayMerge -TargetFile $dst -BaseFile $baseFile -StagedFile $src -OutFile $mergedOut
                if ($mRes.ExitCode -eq 0 -and (Test-Path -LiteralPath $mergedOut -PathType Leaf)) {
                    $mergedSha = Get-FileSha256Lower -Path $mergedOut
                    $plan += [pscustomobject]@{
                        RelPath    = $entry.path
                        Source     = $src
                        CopySource = $mergedOut
                        Target     = $dst
                        Op         = "MERGE_3WAY"
                        Sha256     = $mergedSha
                    }
                }
                elseif ($mRes.ExitCode -gt 0) {
                    $conflicts += "MERGE_3WAY_CONFLICT: $($entry.path) has overlapping edits ($($mRes.ExitCode) conflict region(s); resolve manually or use -Force)"
                }
                else {
                    $conflicts += "MERGE_3WAY_ERROR: $($entry.path) ($($mRes.Output))"
                }
            }
            else {
                $conflicts += "BASE_HASH_DIVERGED: $($entry.path) (expected base=$expectedBase, actual=$dstSha; use -Force to overwrite)"
            }
            continue
        }

        $conflicts += "UNKNOWN_ACTION: $($entry.action) on $($entry.path)"
    }

    if ($conflicts.Count -gt 0) {
        Write-Host "Preflight failed with $($conflicts.Count) conflict(s):" -ForegroundColor Red
        foreach ($c in $conflicts) {
            Write-Host "  - $c" -ForegroundColor Red
        }
        exit 1
    }

    $modeLabel = if ($DryRun) { "DryRun" } elseif ($Move) { "Move" } else { "Copy" }
    Write-Host "Preflight OK ($($plan.Count) files; target=$TargetRepo; mode=$modeLabel; format=$shouldFormat; checks=$shouldRunChecks; commit=$Commit)" -ForegroundColor Cyan
    foreach ($item in $plan) {
        Write-Host ("  [{0,-10}] {1}" -f $item.Op, $item.RelPath)
    }
    if ($Commit) {
        Write-Host "  Commit subject: $commitSubject" -ForegroundColor DarkCyan
    }

    if ($DryRun) {
        Write-Host "DryRun complete. No files were modified." -ForegroundColor Yellow
        exit 0
    }

    # Transactional apply + format + checks with automatic rollback
    $backupDir = Join-Path ([System.IO.Path]::GetTempPath()) ("cosmimera_bak_" + [System.Guid]::NewGuid().ToString("N"))
    $backedUp = New-Object System.Collections.Generic.List[object]
    $createdFiles = New-Object System.Collections.Generic.List[string]
    $createdDirs = New-Object System.Collections.Generic.List[string]

    try {
        foreach ($item in $plan) {
            if ($item.Op -eq "SKIP") {
                continue
            }
            $dst = $item.Target
            if (Test-Path -LiteralPath $dst -PathType Leaf) {
                if (-not (Test-Path -LiteralPath $backupDir -PathType Container)) {
                    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
                }
                $bakPath = Join-Path $backupDir ($item.RelPath -replace "/", "__")
                [System.IO.File]::Copy($dst, $bakPath, $true)
                $backedUp.Add([pscustomobject]@{ Target = $dst; Backup = $bakPath })
            }
            else {
                $parent = Split-Path -Parent $dst
                $missingChain = New-Object System.Collections.Generic.List[string]
                $cursor = $parent
                while ($cursor -and -not (Test-Path -LiteralPath $cursor -PathType Container)) {
                    $missingChain.Add($cursor)
                    $cursor = Split-Path -Parent $cursor
                }
                for ($idx = $missingChain.Count - 1; $idx -ge 0; $idx--) {
                    New-Item -ItemType Directory -Path $missingChain[$idx] -Force | Out-Null
                    $createdDirs.Add($missingChain[$idx])
                }
                $createdFiles.Add($dst)
            }

            [System.IO.File]::Copy($item.CopySource, $dst, $true)
            $writtenSha = Get-FileSha256Lower -Path $dst
            if ($writtenSha -ne $item.Sha256) {
                throw "Post-copy SHA-256 verification failed for $dst"
            }
        }

        if ($shouldFormat) {
            $toFormat = @($plan | Where-Object { $_.Op -ne "SKIP" } | ForEach-Object { $_.Target })
            if ($toFormat.Count -gt 0) {
                Format-TargetFiles -Paths $toFormat
                Write-Host "Formatted $($toFormat.Count) migrated file(s) per .editorconfig/.gitattributes (UTF-8 no BOM, LF)." -ForegroundColor Cyan
            }
        }

        if ($shouldRunChecks) {
            Write-Host "Running post-migration checks in $TargetRepo..." -ForegroundColor Cyan
            Push-Location $TargetRepo
            try {
                & python tools/tests/test_move_balance.py
                if ($LASTEXITCODE -ne 0) { throw "test_move_balance.py failed with exit code $LASTEXITCODE" }

                $tmpRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("cosmimera_val_" + [System.Guid]::NewGuid().ToString("N"))
                New-Item -ItemType Directory -Path $tmpRoot -Force | Out-Null
                try {
                    $batchName = $manifest.batch_id
                    foreach ($kind in @("creatures", "moves", "relations")) {
                        $dstKind = Join-Path $tmpRoot $kind
                        New-Item -ItemType Directory -Path $dstKind -Force | Out-Null
                        Copy-Item -Path (Join-Path $TargetRepo "Data\_catalog\$kind\*.json") -Destination $dstKind
                    }
                    $dstTraits = Join-Path $tmpRoot "traits"
                    New-Item -ItemType Directory -Path $dstTraits -Force | Out-Null
                    Get-ChildItem -Path (Join-Path $TargetRepo "Data\_incoming") -Recurse -Filter "traits.json" | ForEach-Object {
                        $tag = $_.Directory.Parent.Name
                        Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $dstTraits "$tag--traits.json")
                    }
                    foreach ($pair in @(
                        @("Data\field-utilities", "field-utilities"),
                        @("Data\_incoming\p3-31-ecology-draft-01\niches", "niches"),
                        @("Data\_incoming\$batchName\eggs", "eggs"),
                        @("Data\_incoming\$batchName\encyclopedia", "encyclopedia")
                    )) {
                        $sDir = Join-Path $TargetRepo $pair[0]
                        if (Test-Path -LiteralPath $sDir -PathType Container) {
                            $dDir = Join-Path $tmpRoot $pair[1]
                            New-Item -ItemType Directory -Path $dDir -Force | Out-Null
                            Copy-Item -Path (Join-Path $sDir "*.json") -Destination $dDir
                        }
                    }
                    & python tools/validate_data.py --root $tmpRoot --schemas Data/schemas --retired-ids Data/retired-ids.txt
                    if ($LASTEXITCODE -ne 0) { throw "validate_data.py failed with exit code $LASTEXITCODE" }
                }
                finally {
                    if (Test-Path -LiteralPath $tmpRoot) {
                        Remove-Item -LiteralPath $tmpRoot -Recurse -Force
                    }
                }
            }
            finally {
                Pop-Location
            }
        }
    }
    catch {
        Write-Host "Error during migration: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Rolling back changes in $TargetRepo..." -ForegroundColor Yellow
        foreach ($cf in $createdFiles) {
            if (Test-Path -LiteralPath $cf -PathType Leaf) {
                Remove-Item -LiteralPath $cf -Force
            }
        }
        for ($idx = $createdDirs.Count - 1; $idx -ge 0; $idx--) {
            $d = $createdDirs[$idx]
            if ((Test-Path -LiteralPath $d -PathType Container) -and ((Get-ChildItem -LiteralPath $d -Force | Measure-Object).Count -eq 0)) {
                Remove-Item -LiteralPath $d -Force
            }
        }
        foreach ($b in $backedUp) {
            if (Test-Path -LiteralPath $b.Backup -PathType Leaf) {
                [System.IO.File]::Copy($b.Backup, $b.Target, $true)
            }
        }
        if (Test-Path -LiteralPath $backupDir) {
            Remove-Item -LiteralPath $backupDir -Recurse -Force
        }
        Write-Host "Rollback complete." -ForegroundColor Yellow
        exit 1
    }

    if (Test-Path -LiteralPath $backupDir) {
        Remove-Item -LiteralPath $backupDir -Recurse -Force
    }

    if ($Commit) {
        $ignoreRes = Invoke-GitCapture -Repo $TargetRepo -GitArgs (@("check-ignore", "--") + $manifestRelPaths)
        $ignoredSet = New-Object 'System.Collections.Generic.HashSet[string]'
        if ($ignoreRes.ExitCode -eq 0 -and $ignoreRes.Output) {
            foreach ($ig in ($ignoreRes.Output -split "`n")) {
                $t = $ig.Trim()
                if ($t) { [void]$ignoredSet.Add($t) }
            }
        }
        $commitRelPaths = @($manifestRelPaths | Where-Object { -not $ignoredSet.Contains($_) })
        if ($ignoredSet.Count -gt 0) {
            Write-Host "Note: $($ignoredSet.Count) gitignored manifest path(s) will be synced on disk only and excluded from git commit." -ForegroundColor DarkGray
        }
        if ($commitRelPaths.Count -eq 0) {
            Write-Host "Nothing to commit (all manifest files are gitignored)." -ForegroundColor Yellow
        }
        else {
            $addRes = Invoke-GitCapture -Repo $TargetRepo -GitArgs (@("add", "--") + $commitRelPaths)
            if ($addRes.ExitCode -ne 0) {
                Write-Error "git add failed: $($addRes.Output)"
                exit 1
            }
            $diffCheck = Invoke-GitCapture -Repo $TargetRepo -GitArgs (@("diff", "--cached", "--name-only", "--") + $commitRelPaths)
            if ($diffCheck.ExitCode -ne 0) {
                Write-Error "git diff --cached failed: $($diffCheck.Output)"
                exit 1
            }
            if (-not $diffCheck.Output) {
                Write-Host "Nothing to commit (all trackable manifest files are already committed and up to date)." -ForegroundColor Yellow
            }
            else {
                $msgFile = Join-Path ([System.IO.Path]::GetTempPath()) ("cosmimera_commit_" + [System.Guid]::NewGuid().ToString("N") + ".txt")
                try {
                    $bodyLines = @()
                    if (-not $CommitMessage -and $manifest.default_commit_body) {
                        $bodyLines = @($manifest.default_commit_body | ForEach-Object { [string]$_ })
                    }
                    $msgText = if ($bodyLines.Count -gt 0) {
                        $commitSubject + "`n`n" + ($bodyLines -join "`n") + "`n"
                    }
                    else {
                        $commitSubject + "`n"
                    }
                    [System.IO.File]::WriteAllText($msgFile, $msgText, (New-Object System.Text.UTF8Encoding($false)))

                    $commitRes = Invoke-GitCapture -Repo $TargetRepo -GitArgs (@("commit", "--only", "-F", $msgFile, "--") + $commitRelPaths)
                    if ($commitRes.ExitCode -ne 0) {
                        Write-Error "git commit failed: $($commitRes.Output)"
                        exit 1
                    }
                    $headRes = Invoke-GitCapture -Repo $TargetRepo -GitArgs @("rev-parse", "--short", "HEAD")
                    Write-Host "Committed $($commitRelPaths.Count) manifest file(s) as $($headRes.Output): $commitSubject" -ForegroundColor Green
                }
                finally {
                    if (Test-Path -LiteralPath $msgFile) {
                        Remove-Item -LiteralPath $msgFile -Force
                    }
                }
            }
        }
    }

    if ($Move) {
        foreach ($item in $plan) {
            if (Test-Path -LiteralPath $item.Source -PathType Leaf) {
                Remove-Item -LiteralPath $item.Source -Force
            }
        }
        foreach ($sub in @("Data", "docs", "tools", "_base")) {
            $subPath = Join-Path $StagingDir $sub
            if (Test-Path -LiteralPath $subPath -PathType Container) {
                if ($sub -eq "_base") {
                    Remove-Item -LiteralPath $subPath -Recurse -Force
                    continue
                }
                $dirs = Get-ChildItem -LiteralPath $subPath -Recurse -Directory | Sort-Object { $_.FullName.Length } -Descending
                foreach ($d in $dirs) {
                    if ((Get-ChildItem -LiteralPath $d.FullName -Force | Measure-Object).Count -eq 0) {
                        Remove-Item -LiteralPath $d.FullName -Force
                    }
                }
                if ((Get-ChildItem -LiteralPath $subPath -Force | Measure-Object).Count -eq 0) {
                    Remove-Item -LiteralPath $subPath -Force
                }
            }
        }
        Write-Host "Moved $($plan.Count) staged file(s) and pruned staged payload directories." -ForegroundColor Green
    }
    elseif (-not $Commit) {
        Write-Host "Copied $($plan.Count) staged file(s) to $TargetRepo." -ForegroundColor Green
    }
}
finally {
    if (Test-Path -LiteralPath $mergeTempDir) {
        Remove-Item -LiteralPath $mergeTempDir -Recurse -Force
    }
}

exit 0
