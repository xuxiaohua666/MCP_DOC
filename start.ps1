# MCP文档服务器启动脚本 (PowerShell版本)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    MCP文档服务器启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 环境变量设置
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

# 检查Python命令
$pythonCandidates = @("python", "python3", "py -3", "py")
$pythonCmd = $null
foreach ($candidate in $pythonCandidates) {
    try {
        $cmdParts = $candidate.Split(" ", 2)
        if ($cmdParts.Length -eq 2) {
            Get-Command $cmdParts[0] -ErrorAction Stop | Out-Null
            $pythonCmd = $candidate
            break
        } else {
            Get-Command $candidate -ErrorAction Stop | Out-Null
            $pythonCmd = $candidate
            break
        }
    } catch {
        continue
    }
}

if (-not $pythonCmd) {
    Write-Host "❌ 错误：未找到Python环境，请先安装Python" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# 检查Python环境
Write-Host "正在检查Python环境..." -ForegroundColor Yellow
try {
    $pythonVersion = Invoke-Expression "$pythonCmd --version 2>&1"
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "✅ Python环境检查通过: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ 错误：未找到Python环境，请先安装Python" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

Write-Host ""

# 检查依赖包
Write-Host "正在检查依赖包..." -ForegroundColor Yellow
try {
    Invoke-Expression "$pythonCmd -c `"import mcp`"" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Dependencies not found"
    }
    Write-Host "✅ 依赖包检查通过" -ForegroundColor Green
} catch {
    Write-Host "⚠️  正在安装依赖包..." -ForegroundColor Yellow
    Invoke-Expression "$pythonCmd -m pip install mcp"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 依赖包安装失败" -ForegroundColor Red
        Read-Host "按回车键退出"
        exit 1
    }
    Write-Host "✅ 依赖包安装完成" -ForegroundColor Green
}

Write-Host ""

$runStdIo = $args.Length -ge 1 -and $args[0].ToLower() -eq "stdio"

if (-not $runStdIo) {
    $hostValue = if ($args.Length -ge 1) { $args[0] } else { "0.0.0.0" }
    $portValue = if ($args.Length -ge 2) { $args[1] } else { 7778 }

    Write-Host "正在启动HTTP MCP网关服务器..." -ForegroundColor Yellow
    Write-Host "" 
    try {
        Invoke-Expression "$pythonCmd start.py --mode http --host $hostValue --port $portValue --skip-checks"
    } catch {
        Write-Host "❌ 服务器启动失败" -ForegroundColor Red
    } finally {
        Write-Host ""
        Write-Host "服务器已停止" -ForegroundColor Yellow
        Read-Host "按回车键退出"
    }
    exit
}

Write-Host "正在启动MCP协议服务器 (STDIO 模式)..." -ForegroundColor Yellow
Write-Host "🤖 客户端配置示例：" -ForegroundColor Cyan
Write-Host "    Command : $pythonCmd" -ForegroundColor Cyan
Write-Host "    Args    : start.py --mode mcp --skip-checks" -ForegroundColor Cyan
Write-Host "    Workdir : $PWD" -ForegroundColor Cyan
Write-Host "⚠️  配置完成后，此窗口可关闭；客户端会自行管理进程。" -ForegroundColor Magenta
Write-Host "💡 若需共享给其他设备，请改用 http 模式：.\start.ps1 [host] [port]" -ForegroundColor Magenta
Write-Host "" 

try {
    Invoke-Expression "$pythonCmd start.py --mode mcp --skip-checks"
} catch {
    Write-Host "❌ 服务器启动失败" -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "服务器已停止" -ForegroundColor Yellow
    Read-Host "按回车键退出"
}
