# Install every skill in this repo into Claude's skills folder, plus the pinned third-party skills (Windows).
#   .\install.ps1                                   # -> %USERPROFILE%\.claude\skills
#   .\install.ps1 -Target .\.claude\skills          # one project only
#   .\install.ps1 -NoUpstream                       # only the skills in this repo
#   .\install.ps1 -Kit                              # also install the motion-film kit's node + python dependencies
param([string]$Target = "$HOME\.claude\skills", [switch]$NoUpstream, [switch]$Kit)
$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot; $SrcDir = "$HOME\.claude\skill-src"
New-Item -ItemType Directory -Force $Target, $SrcDir | Out-Null
foreach ($t in "git", "python", "node", "ffmpeg") {
  if (-not (Get-Command $t -ErrorAction SilentlyContinue)) { throw "missing: $t - install it and re-run" } }
$Manifest = Get-Content "$Root\manifest.json" -Raw | ConvertFrom-Json

function Replace-Skill([string]$name) {
  if ([string]::IsNullOrWhiteSpace($name)) { throw "empty skill name" }
  $dst = Join-Path $Target $name
  if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
  return $dst }

Write-Host "== skills from this repo -> $Target"
Get-ChildItem "$Root\skills" -Directory | ForEach-Object {
  $src = $_.FullName; $dst = Replace-Skill $_.Name
  $ex = "$src\example"
  $xd = @("node_modules", "__pycache__", ".hyperframes", "$ex\assets", "$ex\renders", "$ex\audio", "$ex\music", "$ex\sfx", "$ex\storyboard")
  robocopy $src $dst /E /NFL /NDL /NJH /NJS /XD $xd /XF "$ex\index.html" "$ex\events.json" | Out-Null
  if ($LASTEXITCODE -ge 8) { throw "copy failed for $($_.Name)" }
  Write-Host "  $($_.Name)" }

function Fetch([string]$name) {
  $u = $Manifest.upstream | Where-Object name -eq $name; $dir = Join-Path $SrcDir $name
  if (-not (Test-Path "$dir\.git")) { git clone --quiet $u.repo $dir }
  git -C $dir fetch --quiet origin $u.commit 2>$null
  if ($LASTEXITCODE -ne 0) { git -C $dir fetch --quiet origin }
  git -C $dir checkout --quiet $u.commit
  Write-Host "  $name @ $($u.commit.Substring(0, 10))"; return $dir }

if (-not $NoUpstream) {
  Write-Host "== third-party skills (pinned)"
  $three = Fetch "threejs-skills"
  Get-ChildItem "$three\skills" -Directory | ForEach-Object {
    $d = Replace-Skill $_.Name; Copy-Item $_.FullName $d -Recurse; Write-Host "    $($_.Name)" }
  Fetch "earshot" | Out-Null; Fetch "clipwing" | Out-Null; Fetch "ffmpeg-skill" | Out-Null
  $cli = ($Manifest.upstream | Where-Object name -eq "hyperframes").cli
  Push-Location (Split-Path $Target)
  try { npx --yes $cli skills update } catch { Write-Host "  ! run 'npx hyperframes skills update' yourself" }
  Pop-Location
  Write-Host "  earshot's Python environment (~1.1 GB of models) is set up on first use by the earshot skill."
}
if ($Kit) {
  Push-Location "$Target\motion-film\kit\node"; npm install --no-audit --no-fund; npm run build:3d; Pop-Location
  python -m pip install -r "$Target\motion-film\kit\requirements.txt"
}
python "$Root\scripts\check_skills.py" $Target
Write-Host "== done"
