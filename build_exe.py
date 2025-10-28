"""
自动化打包脚本
用于生成exe安装包
"""
import os
import sys
import subprocess
import shutil


def check_dependencies():
    """检查依赖是否安装"""
    print("检查打包依赖...")

    try:
        import PyInstaller
        print("✓ PyInstaller 已安装")
    except ImportError:
        print("✗ PyInstaller 未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller 安装完成")

    try:
        import matplotlib
        print("✓ matplotlib 已安装")
    except ImportError:
        print("✗ matplotlib 未安装")
        return False

    try:
        import tkinter
        print("✓ tkinter 已安装")
    except ImportError:
        print("✗ tkinter 未安装")
        return False

    return True


def clean_build_files():
    """清理之前的构建文件"""
    print("清理之前的构建文件...")

    folders_to_clean = ['build', 'dist']
    for folder in folders_to_clean:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"✓ 清理 {folder}")

    files_to_clean = ['Focus-Insight.spec', '*.pyc', '__pycache__']
    for pattern in files_to_clean:
        if os.path.exists(pattern):
            if os.path.isfile(pattern):
                os.remove(pattern)
                print(f"✓ 清理 {pattern}")
            else:
                shutil.rmtree(pattern)
                print(f"✓ 清理 {pattern}")


def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")

    # 使用PyInstaller进行打包
    cmd = [sys.executable, "-m", "PyInstaller", "build_spec.py", "--clean"]

    try:
        subprocess.run(cmd, check=True)
        print("✓ 构建完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 构建失败: {e}")
        return False


def create_installer():
    """创建安装程序"""
    print("创建安装程序...")

    dist_dir = os.path.join(os.getcwd(), 'dist')
    if not os.path.exists(dist_dir):
        print("✗ dist 目录不存在")
        return False

    # 创建简单的批处理文件来启动程序
    batch_content = """@echo off
echo Starting Focus-Insight...
echo.
echo 1. Monitor - 启动监控程序
echo 2. Report - 查看报告
echo.
set /p choice="请选择功能 (1/2): "

if "%choice%"=="1" (
    start "" "%~dp0FocusInsight-Monitor\FocusInsight-Monitor.exe"
) else if "%choice%"=="2" (
    start "" "%~dp0FocusInsight-Report\FocusInsight-Report.exe"
) else (
    echo 无效选择
    pause
)
"""

    batch_file = os.path.join(dist_dir, "Start_FocusInsight.bat")
    with open(batch_file, 'w', encoding='gbk') as f:
        f.write(batch_content)
    print(f"✓ 创建启动脚本: {batch_file}")

    # 创建README文件
    readme_content = """# Focus-Insight 个人效率分析工具

## 安装说明
1. 将整个 dist 文件夹复制到您想要的位置
2. 运行 Start_FocusInsight.bat 启动程序

## 使用说明
### 监控程序 (FocusInsight-Monitor.exe)
- 记录您的应用使用情况
- 监控浏览器页面变化
- 跟踪键盘鼠标活动
- 所有数据保存在本地

### 报告查看器 (FocusInsight-Report.exe)
- 查看时间轴报告
- 分析应用使用时间
- 导出数据
- 可视化统计信息

## 系统要求
- Windows 7 或更高版本
- 至少 100MB 可用磁盘空间
- 屏幕分辨率 1024x768 或更高

## 数据隐私
- 所有数据都存储在您的本地计算机上
- 不会上传到任何云端服务器
- 您可以随时删除数据文件

## 技术支持
如有问题，请查看 data 目录下的日志文件。
"""

    readme_file = os.path.join(dist_dir, "README.txt")
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"✓ 创建说明文件: {readme_file}")

    return True


def main():
    """主函数"""
    print("=== Focus-Insight 打包工具 ===")
    print()

    # 检查依赖
    if not check_dependencies():
        print("✗ 依赖检查失败，请安装必要的依赖")
        return False

    print()

    # 清理文件
    clean_build_files()
    print()

    # 构建可执行文件
    if not build_executable():
        print("✗ 构建失败")
        return False

    print()

    # 创建安装程序
    if not create_installer():
        print("✗ 创建安装程序失败")
        return False

    print()
    print("=== 打包完成 ===")
    print()
    print("生成的文件:")
    print("- dist/FocusInsight-Monitor/ - 监控程序")
    print("- dist/FocusInsight-Report/ - 报告查看器")
    print("- dist/Start_FocusInsight.bat - 启动脚本")
    print("- dist/README.txt - 说明文件")
    print()
    print("使用方法:")
    print("1. 将整个 dist 文件夹复制到目标位置")
    print("2. 运行 Start_FocusInsight.bat 启动程序")
    print()
    print("注意: 首次运行时，Windows 可能会显示安全警告，请点击'更多信息'并选择'仍要运行'")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)