"""
PyInstaller打包配置文件
用于生成exe安装包
"""
import os
import sys

# PyInstaller配置
block_cipher = None

# 获取项目根目录
project_root = os.path.abspath(os.path.dirname(__file__))

# 数据文件配置
data_files = [
    # 数据目录（如果有的话）
    ('data', 'data'),
    # 图标文件（如果有的话）
    ('icon.ico', '.') if os.path.exists('icon.ico') else None,
    # README文件（如果有的话）
    ('README.md', '.') if os.path.exists('README.md') else None,
]

# 过滤掉None值
data_files = [item for item in data_files if item[1] is not None]

# 分析配置
analysis_args = {
    'pathex': [project_root],
    'hiddenimports': [
        'matplotlib.backends.backend_tkagg',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'matplotlib.patches',
        'matplotlib.dates',
        'matplotlib.font_manager',
        'pynput',
        'win32gui',
        'win32process',
        'win32api',
        'win32con',
    ],
    'hookspath': [],
    'runtime_hooks': [],
    'excludes': [],
    'win_no_prefer_redirects': False,
    'win_private_assemblies': False,
    'cipher': block_cipher,
    'noarchive': False,
}

# 打包配置
pyinstaller_config = {
    'name': 'Focus-Insight',
    'console': False,  # 不显示控制台窗口
    'debug': False,
    'bootloader_ignore_signals': False,
    'strip': False,
    'upx': True,
    'upx_exclude': [],
    'runtime_tmpdir': None,
    'version': '1.0.0',
    'copyright': 'Copyright © 2025 Focus-Insight Team',
    'company_name': 'Focus-Insight',
    'product_name': 'Focus-Insight',
    'file_description': '个人效率分析工具',
    'comments': '精准、无感运行的私人效率助手',
    'product_version': '1.0.0',
    'icon': 'icon.ico' if os.path.exists('icon.ico') else None,
    'uac_admin': False,
    'uac_uiaccess': False,
    'onefile': False,  # 使用目录模式而不是单文件模式
    'datas': data_files,
    'clean': True,
    'distpath': os.path.join(project_root, 'dist'),
    'workpath': os.path.join(project_root, 'build'),
}

# 可执行文件配置
exe_configs = [
    {
        'script': 'main.py',
        'name': 'FocusInsight-Monitor',
        'icon': 'icon.ico' if os.path.exists('icon.ico') else None,
        'console': True,  # 监控程序需要控制台输出
        'debug': False,
        'strip': False,
        'upx': True,
        'dest_base': 'FocusInsight-Monitor',
    },
    {
        'script': 'report_viewer.py',
        'name': 'FocusInsight-Report',
        'icon': 'icon.ico' if os.path.exists('icon.ico') else None,
        'console': False,  # 报告查看器不需要控制台
        'debug': False,
        'strip': False,
        'upx': True,
        'dest_base': 'FocusInsight-Report',
    },
]

if __name__ == '__main__':
    # 打印配置信息
    print("=== Focus-Insight 打包配置 ===")
    print(f"项目根目录: {project_root}")
    print(f"数据文件: {data_files}")
    print(f"可执行文件数量: {len(exe_configs)}")

    print("\n配置完成！")
    print("运行以下命令进行打包:")
    print("pyinstaller build_spec.py")

    print("\n打包后将生成以下文件:")
    print("- dist/FocusInsight-Monitor/: 监控程序")
    print("- dist/FocusInsight-Report/: 报告查看器")