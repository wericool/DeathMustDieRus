<#
    Death Must Die — установщик русификатора
    ========================================

    Что делает:
      1. находит папку игры Death Must Die;
      2. сохраняет оригинальные файлы в ..\backup_game (для удаления);
      3. подменяет английские таблицы строк русскими (и болгарские — на случай,
         если игра когда-нибудь переключится на локаль bg);
      4. отключает CRC у изменённых Addressables-бандлов в catalog.json
         (иначе игра откажется их грузить);
      5. ставит пропатченные sharedassets0.assets / resources.assets,
         разрешающие шрифту добавлять кириллические глифы (мульти-атлас);
      6. выставляет язык en в настройках — русский подставлен именно вместо него,
         отдельного пункта выбора языка в игре нет.

    Запуск:
        powershell -ExecutionPolicy Bypass -File Install-Rus.ps1
        powershell -ExecutionPolicy Bypass -File Install-Rus.ps1 -GamePath "D:\Steam\steamapps\common\Death Must Die"

    Удаление: Uninstall-Rus.ps1
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

# ---------------------------------------------------------------- поиск игры
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
if (-not (Test-Path $aaWin)) { throw "Не найдена папка Addressables: $aaWin" }
if (-not (Test-Path (Join-Path $game 'Death Must Die.exe'))) { throw "В папке нет Death Must Die.exe" }

# ---------------------------------------------------------------- проверка сборки
$src = Join-Path $PSScriptRoot 'StandaloneWindows64'
$bundles = @(
    'localization-string-tables-english(en)_assets_all.bundle',
    'localization-string-tables-bulgarian(bg)_assets_all.bundle'
)
$assets = @('sharedassets0.assets', 'resources.assets')

foreach ($f in $bundles) {
    if (-not (Test-Path (Join-Path $src $f))) { throw "Отсутствует файл сборки: StandaloneWindows64\$f" }
}
foreach ($f in $assets) {
    if (-not (Test-Path (Join-Path $PSScriptRoot "Data\$f"))) { throw "Отсутствует файл сборки: Data\$f" }
}
if (-not (Test-Path (Join-Path $PSScriptRoot 'catalog.json'))) { throw "Отсутствует catalog.json" }

# ---------------------------------------------------------------- игра запущена?
$proc = Get-Process -Name 'Death Must Die' -ErrorAction SilentlyContinue
if ($proc) {
    if ($Force) {
        Write-Warn2 "Игра запущена — останавливаю процесс."
        $proc | Stop-Process -Force
        Start-Sleep -Seconds 2
    } else {
        Write-Step "Игра запущена, закрываю..."
        $proc | ForEach-Object { $_.CloseMainWindow() | Out-Null }
        Start-Sleep -Seconds 4
        $proc = Get-Process -Name 'Death Must Die' -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Warn2 "Игра не закрылась сама — завершаю принудительно."
            $proc | Stop-Process -Force
            Start-Sleep -Seconds 2
        }
    }
}

# ---------------------------------------------------------------- резервные копии
$backup = Join-Path $PSScriptRoot '..\backup_game'
$bWin   = Join-Path $backup 'StandaloneWindows64'
New-Item -ItemType Directory -Force -Path $bWin | Out-Null
Write-Step "Резервная копия оригиналов -> $backup"

foreach ($f in $bundles) {
    $dst = Join-Path $bWin $f
    if (-not (Test-Path $dst)) {
        Copy-Item (Join-Path $aaWin $f) $dst -Force
        Write-Ok "сохранён $f"
    } else { Write-Ok "уже сохранён $f" }
}
if (-not (Test-Path (Join-Path $backup 'catalog.json'))) {
    Copy-Item (Join-Path $aa 'catalog.json') (Join-Path $backup 'catalog.json') -Force
    Write-Ok "сохранён catalog.json"
} else { Write-Ok "уже сохранён catalog.json" }

foreach ($f in $assets) {
    $dst = Join-Path $backup $f
    if (-not (Test-Path $dst)) {
        Copy-Item (Join-Path $data $f) $dst -Force
        Write-Ok "сохранён $f"
    } else { Write-Ok "уже сохранён $f" }
}

# ---------------------------------------------------------------- установка
Write-Step "Установка таблиц строк"
foreach ($f in $bundles) {
    Copy-Item (Join-Path $src $f) (Join-Path $aaWin $f) -Force
    Write-Ok "заменён $f"
}
Copy-Item (Join-Path $PSScriptRoot 'catalog.json') (Join-Path $aa 'catalog.json') -Force
Write-Ok "обновлён catalog.json (CRC отключён для изменённых бандлов)"

Write-Step "Установка патча шрифтов"
foreach ($f in $assets) {
    Copy-Item (Join-Path $PSScriptRoot "Data\$f") (Join-Path $data $f) -Force
    Write-Ok "заменён $f"
}

# ---------------------------------------------------------------- язык в настройках
$opts = Join-Path $env:USERPROFILE 'AppData\LocalLow\Realm Archive\Death Must Die\Options\Default.json'
if (Test-Path $opts) {
    try {
        $json = Get-Content $opts -Raw -Encoding UTF8 | ConvertFrom-Json
        $idx = [Array]::IndexOf($json.OptionValues.keys, 'Locale')
        if ($idx -ge 0 -and $json.OptionValues.values[$idx] -ne 'en') {
            $json.OptionValues.values[$idx] = 'en'
            ($json | ConvertTo-Json -Depth 12 -Compress) | Set-Content $opts -Encoding UTF8
            Write-Ok "в настройках выбран язык en (русский подставлен вместо английского)"
        } else {
            Write-Ok "настройки уже указывают на en"
        }
    } catch { Write-Warn2 "не удалось обновить Options\Default.json: $_" }
} else {
    Write-Warn2 "файл настроек ещё не создан — игра сделает это при первом запуске"
}

# ---------------------------------------------------------------- проверка
Write-Step "Проверка"
$bad = 0
foreach ($f in $bundles) {
    $a = (Get-FileHash (Join-Path $src $f) -Algorithm SHA256).Hash
    $b = (Get-FileHash (Join-Path $aaWin $f) -Algorithm SHA256).Hash
    if ($a -ne $b) { Write-Err "  НЕ СОВПАДАЕТ: $f"; $bad++ } else { Write-Ok "$f — ok" }
}
foreach ($f in $assets) {
    $a = (Get-FileHash (Join-Path $PSScriptRoot "Data\$f") -Algorithm SHA256).Hash
    $b = (Get-FileHash (Join-Path $data $f) -Algorithm SHA256).Hash
    if ($a -ne $b) { Write-Err "  НЕ СОВПАДАЕТ: $f"; $bad++ } else { Write-Ok "$f — ok" }
}

Write-Host ""
if ($bad -eq 0) {
    Write-Host "Готово! Запускайте игру — интерфейс и тексты будут на русском." -ForegroundColor Green
} else {
    Write-Host "Установка завершилась с ошибками ($bad файл(ов))." -ForegroundColor Red
}
Write-Host "Удалить русификатор: Uninstall-Rus.ps1" -ForegroundColor DarkGray
