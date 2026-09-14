Add-Type -AssemblyName System.Windows.Forms, System.Drawing

$exe = 'D:\Steam\steamapps\common\Death Must Die\Death Must Die.exe'
$out = 'E:\Games\DeathMustDieRus\09_test'

Write-Host "starting game..."
Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe)

function Grab([string]$name) {
    $b = [System.Windows.Forms.SystemInformation]::VirtualScreen
    $bmp = New-Object System.Drawing.Bitmap($b.Width, $b.Height)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($b.X, $b.Y, 0, 0, $bmp.Size)
    $p = Join-Path $out $name
    $bmp.Save($p, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose()
    Write-Host "saved $p"
}

Start-Sleep -Seconds 45
Grab 'shot_45s.png'
Start-Sleep -Seconds 20
Grab 'shot_65s.png'

$p = Get-Process -Name 'Death Must Die' -ErrorAction SilentlyContinue
if ($p) { Write-Host ("game running, MainWindowTitle=" + $p.MainWindowTitle) } else { Write-Host "game NOT running" }
