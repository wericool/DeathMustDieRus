<#
    Death Must Die — удаление русификатора
    ======================================

    Возвращает игру в исходное состояние: восстанавливает из backup_game (рядом со скриптом)
    английские/болгарские таблицы строк, catalog.json и оригинальные
    sharedassets0.assets / resources.assets.

    Запуск:
        powershell -ExecutionPolicy Bypass -File Uninstall-Rus.ps1
        powershell -ExecutionPolicy Bypass -File Uninstall-Rus.ps1 -GamePath "D:\Steam\steamapps\common\Death Must Die"

    Файлы резервной копии не удаляются — их можно использовать повторно.
#>
[CmdletBinding()]
param(
    [string]$GamePath = "",
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

function Write-Step($m) { Write-Host "==> $m" -ForegroundColor Cyan }
function Write-Ok($m)   { Write-Host "    $m" -ForegroundColor Green }
function Write-Warn2($m){ Write-Host "    $m" -ForegroundColor Yellow }
function Write-Err($m)  { Write-Host $m -ForegroundColor Red }

function Find-GamePath {
    $candidates = @()
    if ($GamePath) { $candidates += $GamePath }
    $candidates += (Split-Path -Parent $PSScriptRoot)
    $steam = $null
    foreach ($k in @('HKCU:\Software\Valve\Steam', 'HKLM:\SOFTWARE\WOW6432Node\Valve\Steam')) {
        try {
            $p = (Get-ItemProperty -Path $k -ErrorAction Stop).SteamPath
            if ($p) { $steam = $p; break }
        } catch {}
    }
    if ($steam) {
        $vdf = Join-Path $steam 'steamapps\libraryfolders.vdf'
        $roots = @($steam)
        if (Test-Path $vdf) {
            foreach ($m in Select-String -Path $vdf -Pattern '"path"\s+"(.+?)"') {
                $roots += ($m.Matches[0].Groups[1].Value -replace '\\\\', '\')
            }
        }
        foreach ($r in $roots) { $candidates += (Join-Path $r 'steamapps\common\Death Must Die') }
    }
    foreach ($c in $candidates) {
        if ($c -and (Test-Path (Join-Path $c 'Death Must Die.exe'))) { return (Resolve-Path $c).Path }
    }
    return $null
}

$game = Find-GamePath
if (-not $game) {
    Write-Err "Не удалось найти папку игры Death Must Die."
    Write-Host "Укажите её вручную: -GamePath `"D:\Steam\steamapps\common\Death Must Die`""
    exit 1
}
Write-Step "Папка игры: $game"

$data  = Join-Path $game 'Death Must Die_Data'
$aa    = Join-Path $data 'StreamingAssets\aa'
$aaWin = Join-Path $aa 'StandaloneWindows64'

$backup = Join-Path $PSScriptRoot 'backup_game'
if (-not (Test-Path $backup)) {
    Write-Err "Не найдена папка резервных копий: $backup"
    Write-Host "Удаление невозможно — оригинальные файлы не сохранены."
    Write-Host "Восстановите игру через Steam: Library -> Death Must Die -> Properties -> Installed Files -> Verify integrity."
    exit 1
}

$proc = Get-Process -Name 'Death Must Die' -ErrorAction SilentlyContinue
if ($proc) {
    if ($Force) {
        $proc | Stop-Process -Force
        Start-Sleep -Seconds 2
    } else {
        Write-Step "Игра запущена, закрываю..."
        $proc | ForEach-Object { $_.CloseMainWindow() | Out-Null }
        Start-Sleep -Seconds 4
        $proc = Get-Process -Name 'Death Must Die' -ErrorAction SilentlyContinue
        if ($proc) { $proc | Stop-Process -Force; Start-Sleep -Seconds 2 }
    }
}

Write-Step "Восстановление"
$restored = 0

foreach ($f in @(
    'localization-string-tables-english(en)_assets_all.bundle',
    'localization-string-tables-bulgarian(bg)_assets_all.bundle'
)) {
    $srcF = Join-Path (Join-Path $backup 'StandaloneWindows64') $f
    if (Test-Path $srcF) {
        Copy-Item $srcF (Join-Path $aaWin $f) -Force
        Write-Ok "восстановлен $f"
        $restored++
    } else { Write-Warn2 "нет копии для $f — пропущено" }
}

$catB = Join-Path $backup 'catalog.json'
if (Test-Path $catB) {
    Copy-Item $catB (Join-Path $aa 'catalog.json') -Force
    Write-Ok "восстановлен catalog.json"
    $restored++
} else { Write-Warn2 "нет копии catalog.json — пропущено" }

foreach ($f in @('sharedassets0.assets', 'resources.assets')) {
    $srcF = Join-Path $backup $f
    if (Test-Path $srcF) {
        Copy-Item $srcF (Join-Path $data $f) -Force
        Write-Ok "восстановлен $f"
        $restored++
    } else { Write-Warn2 "нет копии $f — пропущено" }
}

Write-Host ""
if ($restored -gt 0) {
    Write-Host "Готово! Игра восстановлена в исходное состояние (английский язык)." -ForegroundColor Green
} else {
    Write-Host "Ничего не восстановлено." -ForegroundColor Red
}
Write-Host "Установить заново: Install-Rus.ps1" -ForegroundColor DarkGray
