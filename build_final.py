"""
最终打包脚本
分别打包监控程序和报告查看器
"""
import os
import sys
import subprocess
import shutil


def check_pyinstaller():
    """检查PyInstaller是否安装"""
    try:
        import PyInstaller
        print("✓ PyInstaller 已安装")
        return True
    except ImportError:
        print("✗ PyInstaller 未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller 安装完成")
        return True


def clean_previous_builds():
    """清理之前的构建文件"""
    print("清理之前的构建文件...")

    folders_to_clean = ['build', 'dist']
    files_to_clean = []  # 不清理spec文件，因为我们需要它们

    for item in folders_to_clean + files_to_clean:
        if os.path.exists(item):
            if os.path.isfile(item):
                os.remove(item)
                print(f"✓ 清理文件: {item}")
            else:
                shutil.rmtree(item)
                print(f"✓ 清理文件夹: {item}")


def build_monitor():
    """构建监控程序"""
    print("构建监控程序...")

    cmd = [sys.executable, "-m", "PyInstaller", "monitor.spec", "--clean"]
    try:
        subprocess.run(cmd, check=True)
        print("✓ 监控程序构建完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 监控程序构建失败: {e}")
        return False


def build_report():
    """构建报告查看器"""
    print("构建报告查看器...")

    cmd = [sys.executable, "-m", "PyInstaller", "report.spec", "--clean"]
    try:
        subprocess.run(cmd, check=True)
        print("✓ 报告查看器构建完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 报告查看器构建失败: {e}")
        return False


def create_distribution():
    """创建最终的发布包"""
    print("创建发布包...")

    # 确保dist目录存在
    os.makedirs("dist", exist_ok=True)

    # 移动构建的程序到dist目录
    monitor_source = os.path.join("dist", "FocusInsight-Monitor")
    report_source = os.path.join("dist", "FocusInsight-Report")

    monitor_dest = os.path.join("dist", "FocusInsight-Monitor")
    report_dest = os.path.join("dist", "FocusInsight-Report")

    # 如果目标目录已存在，先删除
    if os.path.exists(monitor_dest):
        shutil.rmtree(monitor_dest)
    if os.path.exists(report_dest):
        shutil.rmtree(report_dest)

    # 移动构建结果
    if os.path.exists(monitor_source):
        shutil.move(monitor_source, monitor_dest)
        print(f"✓ 移动监控程序到: {monitor_dest}")
    if os.path.exists(report_source):
        shutil.move(report_source, report_dest)
        print(f"✓ 移动报告查看器到: {report_dest}")

    # 创建启动脚本
    batch_content = """@echo off
echo Starting Focus-Insight...
echo.
echo 1. Monitor - 启动监控程序 (记录应用使用情况)
echo 2. Report - 查看报告 (可视化分析)
echo.
set /p choice="请选择功能 (1/2): "

if "%choice%"=="1" (
    start "" "%~dp0FocusInsight-Monitor\\FocusInsight-Monitor.exe"
) else if "%choice%"=="2" (
    start "" "%~dp0FocusInsight-Report\\FocusInsight-Report.exe"
) else (
    echo 无效选择
    pause
)
"""

    batch_file = os.path.join("dist", "Start_FocusInsight.bat")
    with open(batch_file, 'w', encoding='gbk') as f:
        f.write(batch_content)
    print(f"✓ 创建启动脚本: {batch_file}")

    # 创建说明文件
    readme_content = """# Focus-Insight 个人效率分析工具 v1.0

## 简介
Focus-Insight 是一个精准、无感运行的私人效率助手，帮助您了解时间分配，提高工作效率。

## 系统要求
- Windows 7 或更高版本
- 至少 100MB 可用磁盘空间
- 屏幕分辨率 1024x768 或更高

## 安装说明
1. 将整个 `dist` 文件夹复制到您想要的位置
2. 运行 `Start_FocusInsight.bat` 启动程序

## 使用说明

### 监控程序 (FocusInsight-Monitor.exe)
- 功能：记录应用使用情况、浏览器页面变化、键盘鼠标活动
- 使用：双击运行，程序会在后台自动记录您的使用情况
- 特点：
  * 精确记录窗口切换时间
  * 监控浏览器标签页变化
  * 跟踪键盘鼠标输入频率
  * 检测空闲状态（5分钟无操作）
- 停止：按 Ctrl+C 或关闭控制台窗口

### 报告查看器 (FocusInsight-Report.exe)
- 功能：可视化查看使用数据，生成时间轴报告
- 使用：双击运行，选择要查看的数据
- 视图：
  * 时间轴视图：显示一天中应用使用的时间分布
  * 饼图视图：显示各应用使用时间占比
  * 条形图视图：显示应用使用时间排行
- 功能：
  * 鼠标悬停查看详细信息
  * 导出数据为JSON格式
  * 查看不同日期的数据

## 数据隐私
- ✅ 所有数据都存储在您的本地计算机上
- ✅ 不会上传到任何云端服务器
- ✅ 数据文件位于 `data/focus_insight.db`
- ✅ 您可以随时删除数据文件
- ✅ 程序不会收集任何个人信息

## 常见问题

### Q: 程序启动时显示安全警告怎么办？
A: 这是Windows的安全保护机制。点击"更多信息"，然后选择"仍要运行"即可。

### Q: 监控程序运行时会影响电脑性能吗？
A: 不会。程序经过优化，CPU和内存占用极低，确保无感运行。

### Q: 为什么有些浏览器页面没有记录？
A: 当前版本通过窗口标题识别浏览器页面，可能需要后续版本使用更精确的方法。

### Q: 如何备份数据？
A: 复制 `data/focus_insight.db` 文件即可备份所有数据。

### Q: 如何卸载？
A: 直接删除整个 `dist` 文件夹即可完全卸载。

## 技术支持
如有问题，请查看：
1. 控制台输出的错误信息
2. `data` 目录下的日志文件
3. 确保系统满足最低要求

## 版本信息
- 版本：1.0.0
- 开发语言：Python
- 界面框架：Tkinter + Matplotlib
- 数据存储：SQLite

© 2025 Focus-Insight Team
"""

    readme_file = os.path.join("dist", "README.txt")
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"✓ 创建说明文件: {readme_file}")

    return True


def show_final_info():
    """显示最终信息"""
    print("\n" + "="*50)
    print("🎉 Focus-Insight 打包完成！")
    print("="*50)
    print()
    print("📁 生成的文件:")
    print("  ├── dist/")
    print("  │   ├── FocusInsight-Monitor/     # 监控程序")
    print("  │   │   └── FocusInsight-Monitor.exe")
    print("  │   ├── FocusInsight-Report/      # 报告查看器")
    print("  │   │   └── FocusInsight-Report.exe")
    print("  │   ├── Start_FocusInsight.bat  # 启动脚本")
    print("  │   └── README.txt               # 说明文件")
    print()
    print("🚀 使用方法:")
    print("  1. 将整个 dist 文件夹复制到目标位置")
    print("  2. 运行 Start_FocusInsight.bat")
    print("  3. 选择要使用的功能")
    print()
    print("⚠️  注意:")
    print("  - 首次运行时Windows可能显示安全警告")
    print("  - 点击'更多信息'并选择'仍要运行'")
    print("  - 监控程序需要控制台窗口显示运行信息")
    print("  - 报告查看器为纯图形界面，无控制台")
    print("="*50)


def main():
    """主函数"""
    print("=== Focus-Insight 最终打包工具 ===")
    print()

    # 检查PyInstaller
    if not check_pyinstaller():
        print("✗ 无法安装PyInstaller")
        return False

    print()

    # 清理之前的构建
    clean_previous_builds()
    print()

    # 构建监控程序
    if not build_monitor():
        print("✗ 监控程序构建失败")
        return False

    print()

    # 构建报告查看器
    if not build_report():
        print("✗ 报告查看器构建失败")
        return False

    print()

    # 创建发布包
    if not create_distribution():
        print("✗ 发布包创建失败")
        return False

    print()

    # 显示最终信息
    show_final_info()

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)