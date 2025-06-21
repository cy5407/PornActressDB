#!/bin/bash
# 🚀 WSL GPU 一鍵設定腳本
# 自動配置 GPU 加速環境

set -e  # 遇到錯誤立即停止

echo "🚀 WSL GPU 加速環境自動設定開始"
echo "=========================================="

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 進度顯示函數
show_progress() {
    echo -e "${BLUE}[進行中]${NC} $1"
}

show_success() {
    echo -e "${GREEN}[完成]${NC} $1"
}

show_warning() {
    echo -e "${YELLOW}[警告]${NC} $1"
}

show_error() {
    echo -e "${RED}[錯誤]${NC} $1"
}

# 檢查系統需求
check_requirements() {
    show_progress "檢查系統需求..."
    
    # 檢查 WSL 版本
    if command -v wsl.exe &> /dev/null; then
        WSL_VERSION=$(wsl.exe --version 2>/dev/null | head -1 || echo "WSL 1")
        echo "   WSL 版本: $WSL_VERSION"
    else
        show_warning "無法檢測 WSL 版本"
    fi
    
    # 檢查 Python 版本
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        echo "   Python 版本: $PYTHON_VERSION"
    else
        show_error "Python3 未安裝"
        exit 1
    fi
    
    # 檢查 pip
    if command -v pip3 &> /dev/null; then
        show_success "pip3 已安裝"
    else
        show_error "pip3 未安裝"
        exit 1
    fi
    
    show_success "系統需求檢查完成"
}

# 更新系統套件
update_system() {
    show_progress "更新系統套件..."
    
    sudo apt update -qq
    sudo apt upgrade -y -qq
    
    # 安裝必要工具
    sudo apt install -y -qq \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        cmake \
        git \
        curl \
        wget \
        htop \
        tree
    
    show_success "系統套件更新完成"
}

# 檢查 GPU 可用性
check_gpu() {
    show_progress "檢查 GPU 可用性..."
    
    # 檢查 NVIDIA GPU
    if command -v nvidia-smi &> /dev/null; then
        echo "   NVIDIA GPU 資訊:"
        nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader | head -1
        GPU_TYPE="nvidia"
        show_success "偵測到 NVIDIA GPU"
    else
        show_warning "未偵測到 NVIDIA GPU 或驅動程式"
        GPU_TYPE="cpu"
    fi
    
    # 檢查其他 GPU (AMD, Intel)
    if lspci | grep -i amd &> /dev/null; then
        echo "   偵測到 AMD GPU"
        GPU_TYPE="amd"
    fi
    
    if lspci | grep -i intel.*graphics &> /dev/null; then
        echo "   偵測到 Intel GPU"
        if [ "$GPU_TYPE" == "cpu" ]; then
            GPU_TYPE="intel"
        fi
    fi
}

# 建立 GPU 虛擬環境
create_gpu_environment() {
    show_progress "建立 GPU 虛擬環境..."
    
    # 移到專案目錄
    PROJECT_DIR="/mnt/c/Users/$USER/OneDrive/桌面/Python/女優分類_重構20250617"
    if [ -d "$PROJECT_DIR" ]; then
        cd "$PROJECT_DIR"
    else
        show_warning "專案目錄不存在，在當前目錄建立環境"
    fi
    
    # 建立虛擬環境
    if [ -d "gpu_env" ]; then
        show_warning "GPU 環境已存在，將重新建立"
        rm -rf gpu_env
    fi
    
    python3 -m venv gpu_env
    source gpu_env/bin/activate
    
    # 升級 pip
    pip install --upgrade pip -q
    
    show_success "GPU 虛擬環境建立完成"
}

# 安裝 GPU 套件
install_gpu_packages() {
    show_progress "安裝 GPU 加速套件..."
    
    # 確保在虛擬環境中
    source gpu_env/bin/activate
    
    # 基礎套件
    pip install -q numpy scipy matplotlib pandas scikit-learn
    
    # 根據 GPU 類型安裝對應套件
    case $GPU_TYPE in
        "nvidia")
            show_progress "安裝 NVIDIA CUDA 套件..."
            pip install -q torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
            pip install -q tensorflow[and-cuda]
            pip install -q cupy-cuda12x
            show_success "NVIDIA 套件安裝完成"
            ;;
        "amd")
            show_progress "安裝 AMD ROCm 套件..."
            pip install -q torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7
            pip install -q tensorflow-rocm
            show_success "AMD 套件安裝完成"
            ;;
        "intel")
            show_progress "安裝 Intel GPU 套件..."
            pip install -q intel-extension-for-pytorch
            pip install -q intel-tensorflow
            show_success "Intel 套件安裝完成"
            ;;
        *)
            show_warning "未偵測到 GPU，安裝 CPU 版本套件"
            pip install -q torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
            pip install -q tensorflow
            ;;
    esac
    
    # 安裝其他必要套件
    pip install -q opencv-python Pillow requests beautifulsoup4 lxml
    
    show_success "GPU 套件安裝完成"
}

# 建立測試腳本
create_test_scripts() {
    show_progress "建立 GPU 測試腳本..."
    
    # 建立快速測試腳本
    cat > quick_gpu_test.py << 'EOF'
#!/usr/bin/env python3
"""快速 GPU 測試腳本"""
import sys

def test_pytorch():
    try:
        import torch
        print(f"✅ PyTorch 版本: {torch.__version__}")
        if torch.cuda.is_available():
            print(f"✅ CUDA 可用，版本: {torch.version.cuda}")
            print(f"✅ GPU 數量: {torch.cuda.device_count()}")
            print(f"✅ GPU 名稱: {torch.cuda.get_device_name(0)}")
        else:
            print("⚠️  CUDA 不可用")
        return True
    except ImportError:
        print("❌ PyTorch 未安裝")
        return False

def test_tensorflow():
    try:
        import tensorflow as tf
        print(f"✅ TensorFlow 版本: {tf.__version__}")
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            print(f"✅ TensorFlow GPU 數量: {len(gpus)}")
        else:
            print("⚠️  TensorFlow GPU 不可用")
        return True
    except ImportError:
        print("❌ TensorFlow 未安裝")
        return False

def quick_performance_test():
    try:
        import torch
        import time
        
        if not torch.cuda.is_available():
            print("⚠️  CUDA 不可用，跳過效能測試")
            return
        
        print("🚀 執行快速效能測試...")
        
        # 建立測試張量
        size = 2048
        a = torch.randn(size, size, device='cpu')
        b = torch.randn(size, size, device='cpu')
        
        # CPU 測試
        start = time.time()
        c_cpu = torch.matmul(a, b)
        cpu_time = time.time() - start
        
        # GPU 測試
        a_gpu = a.cuda()
        b_gpu = b.cuda()
        torch.cuda.synchronize()
        
        start = time.time()
        c_gpu = torch.matmul(a_gpu, b_gpu)
        torch.cuda.synchronize()
        gpu_time = time.time() - start
        
        speedup = cpu_time / gpu_time
        print(f"🎯 CPU 時間: {cpu_time:.4f}s")
        print(f"🎯 GPU 時間: {gpu_time:.4f}s")
        print(f"🎯 加速倍數: {speedup:.2f}x")
        
    except Exception as e:
        print(f"❌ 效能測試失敗: {e}")

if __name__ == "__main__":
    print("🔍 GPU 環境快速測試")
    print("=" * 40)
    
    pytorch_ok = test_pytorch()
    tensorflow_ok = test_tensorflow()
    
    if pytorch_ok:
        quick_performance_test()
    
    print("\n✅ 測試完成！")
EOF
    
    chmod +x quick_gpu_test.py
    show_success "測試腳本建立完成"
}

# 建立啟動腳本
create_launch_scripts() {
    show_progress "建立啟動腳本..."
    
    # GPU 環境啟動腳本
    cat > start_gpu_env.sh << 'EOF'
#!/bin/bash
# GPU 環境啟動腳本

echo "🔥 啟動 GPU 加速環境"
echo "====================="

# 啟用虛擬環境
if [ -f "gpu_env/bin/activate" ]; then
    source gpu_env/bin/activate
    echo "✅ GPU 虛擬環境已啟用"
else
    echo "❌ GPU 環境不存在，請先執行設定腳本"
    exit 1
fi

# 顯示 GPU 資訊
python quick_gpu_test.py

echo ""
echo "🎯 環境已就緒！可以開始使用 GPU 加速功能"
echo "執行 'python your_script.py' 開始開發"
EOF
    
    chmod +x start_gpu_env.sh
    
    # 專案啟動腳本 (如果存在)
    if [ -f "run.py" ]; then
        cat > run_gpu.sh << 'EOF'
#!/bin/bash
# 女優分類系統 GPU 版本啟動腳本

echo "🎬 女優分類系統 - GPU 加速版"
echo "============================="

# 啟用 GPU 環境
source gpu_env/bin/activate

# 執行系統
python run.py --use-gpu "$@"
EOF
        chmod +x run_gpu.sh
        show_success "專案 GPU 啟動腳本建立完成"
    fi
    
    show_success "啟動腳本建立完成"
}

# 執行最終測試
run_final_test() {
    show_progress "執行最終 GPU 測試..."
    
    source gpu_env/bin/activate
    python quick_gpu_test.py
    
    show_success "GPU 環境設定完成！"
}

# 顯示使用說明
show_usage_instructions() {
    echo ""
    echo "🎉 GPU 加速環境設定完成！"
    echo "=========================================="
    echo ""
    echo "📋 使用說明:"
    echo "   1. 啟動 GPU 環境: ./start_gpu_env.sh"
    echo "   2. 執行測試: python quick_gpu_test.py"
    if [ -f "run_gpu.sh" ]; then
        echo "   3. 啟動專案: ./run_gpu.sh"
    fi
    echo ""
    echo "🔧 手動啟動:"
    echo "   source gpu_env/bin/activate"
    echo "   python your_script.py"
    echo ""
    echo "📊 效能預期:"
    echo "   - 矩陣運算: 10-50x 加速"
    echo "   - 圖像處理: 5-20x 加速"
    echo "   - 深度學習: 20-100x 加速"
    echo ""
    echo "🚀 開始使用 GPU 加速進行開發吧！"
}

# 主程式執行流程
main() {
    echo "開始自動設定 GPU 加速環境..."
    echo ""
    
    check_requirements
    echo ""
    
    update_system
    echo ""
    
    check_gpu
    echo ""
    
    create_gpu_environment
    echo ""
    
    install_gpu_packages
    echo ""
    
    create_test_scripts
    echo ""
    
    create_launch_scripts
    echo ""
    
    run_final_test
    echo ""
    
    show_usage_instructions
}

# 錯誤處理
trap 'show_error "設定過程中發生錯誤！"; exit 1' ERR

# 執行主程式
main

exit 0
