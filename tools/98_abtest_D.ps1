<#
  Test D: AnotherRus catalog + OUR ru bundles + OUR font patch (sharedassets0/resources).
#>
param()
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
$game = 'D:\Steam\steamapps\common\Death Must Die'
$data = Join-Path $game 'Death Must Die_Data'
$aa   = Join-Path $data 'StreamingAssets\aa'
$win  = Join-Path $aa 'StandaloneWindows64'
$backup = 'E:\Games\DeathMustDieRus\backup_game'
$other  = 'E:\Games\DeathMustDieRus\AnotherRus\Death Must Die_Data\StreamingAssets\aa'
$build  = 'E:\Games\DeathMustDieRus\03_build'
$out = 'E:\Games\DeathMustDieRus\09_test'
$log = Join-Path $env:USERPROFILE 'AppData\LocalLow\Realm Archive\Death Must Die\Player.log'

$p = Get-Process -Name 'Death Must Die' -ErrorAction SilentlyContinue
if ($p) { $p | Stop-Process -Force; Start-Sleep -Seconds 2 }

# vanilla base
Copy-Item (Join-Path $backup 'catalog.json') (Join-Path $aa 'catalog.json') -Force
Copy-Item (Join-Path $backup 'StandaloneWindows64\localization-string-tables-english(en)_assets_all.bundle') $win -Force
Copy-Item (Join-Path $backup 'StandaloneWindows64\localization-string-tables-bulgarian(bg)_assets_all.bundle') $win -Force
Copy-Item (Join-Path $backup 'sharedassets0.assets') $data -Force
Copy-Item (Join-Path $backup 'resources.assets') $data -Force

# D: AnotherRus catalog + our bundles + our fonts
Copy-Item (Join-Path $other 'catalog.json') (Join-Path $aa 'catalog.json') -Force
Copy-Item (Join-Path $build 'StandaloneWindows64\localization-string-tables-english(en)_assets_all.bundle') $win -Force
Copy-Item (Join-Path $build 'StandaloneWindows64\localization-string-tables-bulgarian(bg)_assets_all.bundle') $win -Force
Copy-Item (Join-Path $build 'Data\sharedassets0.assets') $data -Force
Copy-Item (Join-Path $build 'Data\resources.assets') $data -Force
Write-Host 'config D installed'

if (Test-Path $log) { Remove-Item $log -Force }
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
Grab 'ab_D_90s.png'
Start-Sleep -Seconds 30
Grab 'ab_D_120s.png'

Write-Host '--- player.log signals ---'
if (Test-Path $log) {
    $sig = Select-String -Path $log -Pattern 'Invalid path|LoadTableOperation|NullReferenceException|RemoteProviderException'
    Write-Host ("signal lines: " + $sig.Count)
    $sig | Select-Object -First 8 | ForEach-Object { $_.Line.Substring(0, [Math]::Min(160, $_.Line.Length)) }
} else { Write-Host 'no Player.log' }

$p = Get-Process -Name 'Death Must Die' -ErrorAction SilentlyContinue
if ($p) { $p | Stop-Process -Force; Write-Host 'game killed' } else { Write-Host 'game NOT running' }
