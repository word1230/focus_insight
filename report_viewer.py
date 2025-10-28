"""
报告查看器
独立的时间轴报告查看程序
"""
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow


def main():
    """主函数 - 启动报告查看器"""
    print("=== Focus-Insight 报告查看器 ===")
    print("正在启动图形界面...")

    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"启动报告查看器时出错: {e}")
        input("按回车键退出...")


if __name__ == "__main__":
    main()