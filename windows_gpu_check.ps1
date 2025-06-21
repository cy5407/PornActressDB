# 🚀 Windows GPU 驅動程式檢查與設定腳本
# PowerShell 版本 - 在 Windows 中執行

Write-Host "🚀 Windows GPU 驅動程式檢查與 WSL 設定" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green

# 顏色定義
function Write-Progress { param($Message) Write-Host "[進行中] $Message" -ForegroundColor Blue }
function Write-Success { param($Message) Write-Host "[完成] $Message" -ForegroundColor Green }
function Write-Warning { param($Message) Write-Host "[警告] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[錯誤] $Message" -ForegroundColor Red }

# 檢查管理員權限
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# 檢查 Windows 版本
function Check-WindowsVersion {
    Write-Progress "檢查 Windows 版本..."
    
    $version = Get-WmiObject -Class Win32_OperatingSystem
    $buildNumber = [int]$version.BuildNumber
    
    Write-Host "   Windows 版本: $($version.Caption)"
    Write-Host "   組建編號: $buildNumber"
    
    if ($buildNumber -ge 19041) {
        Write-Success "Windows 版本支援 WSL 2 GPU"
        return $true
    } else {
        Write-Error "Windows 版本過舊，需要 Windows 10 2004 (組建 19041) 或更新版本"
        return $false
    }
}

# 檢查 WSL 版本
function Check-WSLVersion {
    Write-Progress "檢查 WSL 版本..."
    
    try {
        $wslOutput = wsl --version 2>$null
        if ($wslOutput) {
            Write-Host "   WSL 版本資訊:"
            $wslOutput | ForEach-Object { Write-Host "   $_" }
            Write-Success "WSL 2 已安裝"
            return $true
        }
    } catch {
        Write-Warning "WSL 未安裝或版本過舊"
        return $false
    }
}

# 檢查 GPU 資訊
function Check-GPUInfo {
    Write-Progress "檢查 GPU 資訊..."
    
    $gpus = Get-WmiObject Win32_VideoController | Where-Object { $_.Name -notlike "*Basic*" }
    
    foreach ($gpu in $gpus) {
        Write-Host "   GPU: $($gpu.Name)"
        Write-Host "   驅動程式版本: $($gpu.DriverVersion)"
        Write-Host "   驅動程式日期: $($gpu.DriverDate)"
        
        # 檢查是否為支援的 GPU
        if ($gpu.Name -match "NVIDIA") {
            Write-Success "偵測到 NVIDIA GPU"
            Check-NVIDIADriver
        } elseif ($gpu.Name -match "AMD|Radeon") {
            Write-Success "偵測到 AMD GPU"
            Check-AMDDriver
        } elseif ($gpu.Name -match "Intel") {
            Write-Success "偵測到 Intel GPU"
            Check-IntelDriver
        }
        Write-Host ""
    }
}

# 檢查 NVIDIA 驅動程式
function Check-NVIDIADriver {
    try {
        $nvidiaOutput = nvidia-smi 2>$null
        if ($nvidiaOutput) {
            Write-Host "   NVIDIA-SMI 輸出:"
            $nvidiaOutput | Select-Object -First 5 | ForEach-Object { Write-Host "   $_" }
            Write-Success "NVIDIA 驅動程式正常運作"
        }
    } catch {
        Write-Warning "NVIDIA 驅動程式可能需要更新"
        Write-Host "   建議下載最新驅動程式: https://www.nvidia.com/drivers/"
    }
}

# 檢查 AMD 驅動程式
function Check-AMDDriver {
    Write-Host "   AMD GPU 偵測成功"
    Write-Host "   建議確保已安裝最新 AMD Software: https://www.amd.com/support"
}

# 檢查 Intel 驅動程式
function Check-IntelDriver {
    Write-Host "   Intel GPU 偵測成功"
    Write-Host "   建議確保已安裝最新 Intel Graphics Driver"
}

# 檢查 WSL 功能
function Check-WSLFeatures {
    Write-Progress "檢查 WSL 功能狀態..."
    
    $wslFeature = Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
    $vmFeature = Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform
    
    Write-Host "   WSL 功能狀態: $($wslFeature.State)"
    Write-Host "   虛擬機器平台狀態: $($vmFeature.State)"
    
    if ($wslFeature.State -eq "Enabled" -and $vmFeature.State -eq "Enabled") {
        Write-Success "WSL 功能已正確啟用"
        return $true
    } else {
        Write-Warning "WSL 功能未完全啟用"
        return $false
    }
}

# 自動安裝/啟用 WSL
function Install-WSL {
    Write-Progress "自動設定 WSL..."
    
    if (-not (Test-Administrator)) {
        Write-Error "需要管理員權限來安裝 WSL"
        Write-Host "請以管理員身分執行 PowerShell 並重新運行此腳本"
        return $false
    }
    
    try {
        # 啟用 WSL 功能
        Write-Progress "啟用 WSL 功能..."
        Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart
        
        # 啟用虛擬機器平台
        Write-Progress "啟用虛擬機器平台..."
        Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -NoRestart
        
        # 設定 WSL 2 為預設
        Write-Progress "設定 WSL 2 為預設版本..."
        wsl --set-default-version 2
        
        # 更新 WSL 核心
        Write-Progress "更新 WSL 核心..."
        wsl --update
        
        Write-Success "WSL 設定完成"
        Write-Warning "請重新啟動電腦以完成設定"
        
        return $true
    } catch {
        Write-Error "WSL 安裝失敗: $($_.Exception.Message)"
        return $false
    }
}

# 建立 WSL 設定檔
function Create-WSLConfig {
    Write-Progress "建立 WSL 設定檔..."
    
    $configPath = "$env:USERPROFILE\.wslconfig"
    
    $configContent = @"
[wsl2]
memory=8GB
processors=4
swap=2GB
localhostForwarding=true

[experimental]
autoMemoryReclaim=gradual
networkingMode=mirrored
dnsTunneling=true
firewall=true
autoProxy=true
"@
    
    try {
        Set-Content -Path $configPath -Value $configContent -Encoding UTF8
        Write-Success "WSL 設定檔已建立: $configPath"
        Write-Host "   記憶體分配: 8GB (可根據需要調整)"
        Write-Host "   CPU 核心: 4 (可根據需要調整)"
    } catch {
        Write-Error "無法建立 WSL 設定檔: $($_.Exception.Message)"
    }
}

# 檢查 Ubuntu 發行版
function Check-UbuntuDistro {
    Write-Progress "檢查 Ubuntu 發行版..."
    
    $distros = wsl --list --verbose 2>$null
    if ($distros) {
        Write-Host "   已安裝的 WSL 發行版:"
        $distros | ForEach-Object { Write-Host "   $_" }
        
        if ($distros -match "Ubuntu") {
            Write-Success "Ubuntu 發行版已安裝"
            return $true
        }
    }
    
    Write-Warning "未找到 Ubuntu 發行版"
    Write-Host "   建議安裝 Ubuntu 22.04 LTS"
    Write-Host "   可從 Microsoft Store 安裝，或執行: wsl --install -d Ubuntu-22.04"
    
    return $false
}

# 產生使用說明
function Show-NextSteps {
    Write-Host ""
    Write-Host "🎯 下一步操作指南" -ForegroundColor Green
    Write-Host "==================" -ForegroundColor Green
    Write-Host ""
    Write-Host "1. 📋 確認 WSL 設定完成後，在 WSL Ubuntu 中執行:"
    Write-Host "   cd /mnt/c/Users/$env:USERNAME/OneDrive/桌面/Python/女優分類_重構20250617"
    Write-Host "   chmod +x gpu_setup.sh"
    Write-Host "   ./gpu_setup.sh"
    Write-Host ""
    Write-Host "2. 🔧 如果需要手動設定:"
    Write-Host "   - NVIDIA: 下載最新 Game Ready 驅動程式"
    Write-Host "   - AMD: 安裝 AMD Software Adrenalin Edition"
    Write-Host "   - Intel: 更新 Intel Graphics Driver"
    Write-Host ""
    Write-Host "3. 🚀 GPU 環境設定完成後:"
    Write-Host "   - 在 WSL 中執行: source gpu_env/bin/activate"
    Write-Host "   - 測試 GPU: python quick_gpu_test.py"
    Write-Host ""
    Write-Host "4. 📊 預期效能提升:"
    Write-Host "   - 矩陣運算: 10-50x"
    Write-Host "   - 圖像處理: 5-20x"
    Write-Host "   - 深度學習: 20-100x"
}

# 主要執行流程
function Main {
    Write-Host "開始 Windows GPU 環境檢查..." -ForegroundColor Cyan
    Write-Host ""
    
    # 檢查 Windows 版本
    if (-not (Check-WindowsVersion)) {
        Write-Error "系統不符合需求，無法繼續"
        return
    }
    Write-Host ""
    
    # 檢查 GPU 資訊
    Check-GPUInfo
    
    # 檢查 WSL 版本
    $wslInstalled = Check-WSLVersion
    Write-Host ""
    
    # 檢查 WSL 功能
    $wslFeaturesEnabled = Check-WSLFeatures
    Write-Host ""
    
    # 如果 WSL 未正確設定，提供安裝選項
    if (-not $wslInstalled -or -not $wslFeaturesEnabled) {
        $response = Read-Host "是否要自動設定 WSL? (y/n)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            if (Install-WSL) {
                Create-WSLConfig
            }
        }
    } else {
        # 建立或更新 WSL 設定檔
        Create-WSLConfig
    }
    
    Write-Host ""
    
    # 檢查 Ubuntu 發行版
    Check-UbuntuDistro
    
    Write-Host ""
    Show-NextSteps
    
    Write-Host ""
    Write-Success "Windows 端檢查完成！"
}

# 執行主程式
Main

# 等待使用者按鍵
Write-Host ""
Write-Host "按任意鍵結束..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
