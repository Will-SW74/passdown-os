param(
    [Parameter(Mandatory = $true)]
    [string]$ScriptRelativePath,

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ScriptArguments
)

# PDOS-D-20260722-1：Windows 常見只有 git.exe 在 PATH；從它反推同套 Git Bash，
# 讓 Codex commandWindows 執行既有 POSIX 腳本，不另外複製一份 PowerShell 業務邏輯。
$ErrorActionPreference = 'Stop'
$repoRoot = (& git.exe rev-parse --show-toplevel).Trim()
if (-not $repoRoot) {
    throw '無法解析 Git repository root，Passdown OS hook 無法安全定位。'
}

$gitExecutable = (Get-Command git.exe -ErrorAction Stop).Source
$gitRoot = Split-Path (Split-Path $gitExecutable -Parent) -Parent
$shellCandidates = @(
    (Join-Path $gitRoot 'bin\sh.exe'),
    (Join-Path $gitRoot 'usr\bin\sh.exe')
)
$shell = $shellCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $shell) {
    throw "已找到 git.exe，但找不到同一套 Git Bash 的 sh.exe：$gitRoot"
}

# Why：腳本路徑以 repo root 組合，避免從子目錄啟動 Codex 時相對路徑指錯位置。
$scriptPath = Join-Path $repoRoot ($ScriptRelativePath -replace '/', '\')
if (-not (Test-Path -LiteralPath $scriptPath)) {
    throw "找不到 Passdown OS hook 腳本：$scriptPath"
}

# Why：整個資料夾 copy 或切換 Codex sandbox session 時，舊 `.toolcount` 可能缺少本次
# restricted SID。Codex sandbox 禁止 Set-Acl，因此以一般檔案操作保留舊值並重建檔案；
# 計數邏輯仍由共同 POSIX 腳本唯一負責，PowerShell 只修復 Windows 檔案可寫性。
$sessionsRoot = if (Test-Path -LiteralPath (Join-Path $repoRoot 'passdown-os\sessions')) {
    Join-Path $repoRoot 'passdown-os\sessions'
}
elseif (Test-Path -LiteralPath (Join-Path $repoRoot 'sessions')) {
    Join-Path $repoRoot 'sessions'
}
if ($sessionsRoot) {
    $countFile = Join-Path $sessionsRoot '.toolcount'
    if (Test-Path -LiteralPath $countFile) {
        $countValue = Get-Content -Raw -LiteralPath $countFile
        $countReplacement = Join-Path $sessionsRoot ".toolcount.replace-$PID"
        try {
            Set-Content -LiteralPath $countReplacement -Value $countValue -NoNewline
            Remove-Item -LiteralPath $countFile -Force
            Move-Item -LiteralPath $countReplacement -Destination $countFile -Force
        }
        finally {
            Remove-Item -LiteralPath $countReplacement -Force -ErrorAction SilentlyContinue
        }
    }
}

# Why：Git Bash 不在系統 PATH 時，裸 sh 也找不到同套的 cat 等 POSIX 工具；在 sh 內
# 暫時補上 /usr/bin 與 /bin，既能完整執行共同腳本，也不污染使用者的永久環境變數。
# 先切到 repo root，避免從子目錄啟動時，外層沙箱把 hook 對上層計數檔的寫入判成越界。
$previousLocation = Get-Location
$posixScriptPath = $scriptPath -replace '\\', '/'
try {
    Set-Location -LiteralPath $repoRoot
    & $shell -c 'PATH="/usr/bin:/bin:$PATH"; export PATH; script="$1"; shift; exec sh "$script" "$@"' sh $posixScriptPath @ScriptArguments
    $hookExitCode = $LASTEXITCODE
}
finally {
    Set-Location -LiteralPath $previousLocation
}
exit $hookExitCode
