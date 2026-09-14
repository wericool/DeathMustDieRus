<#
  A/B test: install a config, launch the game, screenshot at intervals,
  dump Player.log signals, kill the game.
  Usage: pwsh -File 96_abtest2.ps1 -Mode A|B
  A = new catalog + ru bundles, original fonts
  B = new catalog + ru bundles + font patch
#>
param([Parameter(Mandatory=$true)][string]$Mode)

Add-Type -AssemblyName System.Windows.Forms, System.Drawing
$game = 'D:\Steam\steamapps\common\Death Must Die'
$data = Join-Path $game 'Death Must Die_Data'
$aa   = Join-Path $data 'StreamingAssets\aa'
$win  = Join-Path $aa 'StandaloneWindows64'
$build = 'E:\Games\DeathMustDieRus\03_build'
$backup = 'E:\Games\DeathMustDieRus\backup_game'
$out = 'E:\Games\DeathMustDieRus\09_test'
$log = Join-Path $env:USERPROFILE 'AppData\LocalLow\Realm Archive\Death Must Die\Player.log'

# --- kill game if running
$p = Get-Process -Name 'Death Must Die' -ErrorAction SilentlyContinue
if ($p) { $p | Stop-Process -Force; Start-Sleep -Seconds 2 }

# --- always start from vanilla
Copy-Item (Join-Path $backup 'catalog.json') (Join-Path $aa 'catalog.json') -Force
Copy-Item (Join-Path $backup 'StandaloneWindows64\localization-string-tables-english(en)_assets_all.bundle') $win -Force
Copy-Item (Join-Path $backup 'StandaloneWindows64\localization-string-tables-bulgarian(bg)_assets_all.bundle') $win -Force
Copy-Item (Join-Path $backup 'sharedassets0.assets') $data -Force
Copy-Item (Join-Path $backup 'resources.assets') $data -Force

# --- apply config
Copy-Item (Join-Path $build 'catalog.json') (Join-Path $aa 'catalog.json') -Force
Copy-Item (Join-Path $build 'StandaloneWindows64\localization-string-tables-english(en)_assets_all.bundle') $win -Force
Copy-Item (Join-Path $build 'StandaloneWindows64\localization-string-tables-bulgarian(bg)_assets_all.bundle') $win -Force
if ($Mode -eq 'B') {
    Copy-Item (Join-Path $build 'Data\sharedassets0.assets') $data -Force
    Copy-Item (Join-Path $build 'Data\resources.assets') $data -Force
}
Write-Host "config $Mode installed"

# --- clear old log
if (Test-Path $log) { Remove-Item $log -Force }

# --- launch
Start-Process -FilePath (Join-Path $game 'Death Must Die.exe') -WorkingDirectory $game

function Grab([string]$name) {
    $b = [System.Windows.Forms.SystemInformation]::VirtualScreen
    $bmp = New-Object System.Drawing.Bitmap($b.Width, $b.Height)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($b.X, $b.Y, 0, 0, $bmp.Size)
    $bmp.Save((Join-Path $out $name), [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose()
    Write-Host "saved $name"
}

Start-Sleep -Seconds 90
Grab ("ab_${Mode}_90s.png")
Start-Sleep -Seconds 30
Grab ("ab_${Mode}_120s.png")

Write-Host '--- player.log signals ---'
if (Test-Path $log) {
    Select-String -Path $log -Pattern 'Invalid path|LoadTableOperation|NullReferenceException|UpdateAffix|RemoteProviderException' |
        Select-Object -First 12 | ForEach-Object { $_.Line.Substring(0, [Math]::Min(160, $_.Line.Length)) }
    $nre = Select-String -Path $log -Pattern 'NullReferenceException'
    Write-Host ("NRE count: " + $nre.Count)
} else { Write-Host 'no Player.log' }

$p = Get-Process -Name 'Death Must Die' -ErrorAction SilentlyContinue
if ($p) { $p | Stop-Process -Force; Write-Host 'game killed' } else { Write-Host 'game NOT running (crashed or never started)' }
