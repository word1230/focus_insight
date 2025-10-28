"""
主窗口模块
负责创建应用程序的主界面
"""
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import List, Dict, Any

from gui.timeline_widget import TimelineWidget
from data.storage import DataStorage



class MainWindow:
    def __init__(self):
        """初始化主窗口"""
        self.root = tk.Tk()
        self.root.title("Focus-Insight - 个人效率分析工具")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

        # 设置窗口图标（如果有的话）
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass

        # 初始化数据存储
        self.storage = DataStorage()

        # 创建界面
        self.create_menu()
        self.create_main_layout()
        self.create_status_bar()

        # 加载今日数据
        self.load_today_data()

        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="刷新数据", command=self.refresh_data)
        file_menu.add_separator()
        file_menu.add_command(label="导出数据", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_closing)

        # 视图菜单
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="视图", menu=view_menu)
        view_menu.add_command(label="今日视图", command=lambda: self.change_date("today"))
        view_menu.add_command(label="昨日视图", command=lambda: self.change_date("yesterday"))
        view_menu.add_command(label="选择日期", command=self.select_date)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)

    def create_main_layout(self):
        """创建主布局"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建顶部信息面板
        self.create_info_panel(main_frame)

        # 创建时间轴组件
        self.timeline = TimelineWidget(main_frame, width=900, height=400)
        self.timeline.pack(fill=tk.BOTH, expand=True)

        # 绑定回调函数
        self.timeline.refresh_callback = self.refresh_data
        self.timeline.on_view_change_callback = self.on_view_change

    def create_info_panel(self, parent):
        """创建信息面板"""
        info_frame = ttk.LabelFrame(parent, text="今日统计", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        # 创建统计标签
        stats_frame = ttk.Frame(info_frame)
        stats_frame.pack(fill=tk.X)

        # 总活跃时间
        self.active_time_label = ttk.Label(stats_frame, text="活跃时间: 0小时", font=("Arial", 10, "bold"))
        self.active_time_label.pack(side=tk.LEFT, padx=(0, 20))

        # 应用数量
        self.app_count_label = ttk.Label(stats_frame, text="应用数量: 0", font=("Arial", 10))
        self.app_count_label.pack(side=tk.LEFT, padx=(0, 20))

        # 专注效率
        self.efficiency_label = ttk.Label(stats_frame, text="专注效率: 0%", font=("Arial", 10))
        self.efficiency_label.pack(side=tk.LEFT, padx=(0, 20))

        # 最后更新时间
        self.update_time_label = ttk.Label(stats_frame, text="最后更新: --", font=("Arial", 9))
        self.update_time_label.pack(side=tk.RIGHT)

    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_today_data(self):
        """加载今日数据"""
        try:
            print("开始加载今日数据...")
            # 获取今日数据
            today = datetime.now().date()
            start_time = datetime.combine(today, datetime.min.time())
            end_time = datetime.combine(today, datetime.max.time())

            print(f"查询时间范围: {start_time} 到 {end_time}")

            # 从数据库获取数据
            window_data = self.storage.db.get_window_activities(start_time, end_time)

            print(f"从数据库获取到 {len(window_data)} 条记录")

            # 更新时间轴
            self.timeline.set_data(window_data)

            # 更新统计信息
            self.update_statistics()

            # 更新状态
            self.update_status("数据加载完成")
            self.update_last_update_time()

        except Exception as e:
            print(f"加载数据时出错: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("错误", f"加载数据时出错: {e}")
            self.update_status(f"错误: {e}")

    def update_statistics(self):
        """更新统计信息"""
        try:
            # 获取今日摘要
            summary = self.storage.get_today_summary()

            # 更新标签
            active_hours = summary['total_active_time'] / 3600
            self.active_time_label.config(text=f"活跃时间: {active_hours:.2f}小时")
            self.app_count_label.config(text=f"应用数量: {summary['app_count']}")
            self.efficiency_label.config(text=f"专注效率: {summary['focus_efficiency']:.1f}%")

        except Exception as e:
            print(f"更新统计信息时出错: {e}")

    def refresh_data(self):
        """刷新数据"""
        self.update_status("正在刷新数据...")
        self.root.after(100, self.load_today_data)

    def on_view_change(self, view_type):
        """处理视图变化"""
        self.update_status(f"切换到{view_type}视图")
        # 重新加载数据以更新视图
        self.load_today_data()

    def change_date(self, date_type):
        """改变日期"""
        if date_type == "today":
            target_date = datetime.now().date()
        elif date_type == "yesterday":
            target_date = datetime.now().date() - timedelta(days=1)
        else:
            return

        self.load_date_data(target_date)

    def select_date(self):
        """选择日期"""
        from tkinter import simpledialog
        # 这里可以实现日期选择对话框
        # 暂时使用简单输入
        date_str = tk.simpledialog.askstring("选择日期", "请输入日期 (YYYY-MM-DD):")
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                self.load_date_data(target_date)
            except ValueError:
                messagebox.showerror("错误", "日期格式不正确，请使用 YYYY-MM-DD 格式")

    def load_date_data(self, target_date):
        """加载指定日期的数据"""
        try:
            start_time = datetime.combine(target_date, datetime.min.time())
            end_time = datetime.combine(target_date, datetime.max.time())

            # 获取数据
            window_data = self.storage.db.get_window_activities(start_time, end_time)

            # 更新时间轴
            self.timeline.set_data(window_data)

            # 更新日期输入框
            self.timeline.date_var.set(target_date.strftime("%Y-%m-%d"))

            # 更新状态
            self.update_status(f"已加载 {target_date} 的数据")
            self.update_last_update_time()

        except Exception as e:
            messagebox.showerror("错误", f"加载指定日期数据时出错: {e}")

    def export_data(self):
        """导出数据"""
        try:
            from tkinter import filedialog
            import json

            # 选择保存位置
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )

            if file_path:
                # 导出数据
                data = self.storage.export_data()
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2, default=str)

                messagebox.showinfo("成功", f"数据已导出到:\n{file_path}")
                self.update_status("数据导出成功")

        except Exception as e:
            messagebox.showerror("错误", f"导出数据时出错: {e}")

    def show_help(self):
        """显示帮助信息"""
        help_text = """Focus-Insight 使用说明

基本功能：
1. 时间轴视图：显示一天中应用使用的时间分布
2. 饼图视图：显示各应用使用时间占比
3. 条形图视图：显示应用使用时间排行

操作说明：
• 将鼠标悬停在时间轴上查看详细信息
• 使用日期选择器查看不同日期的数据
• 可以导出数据为JSON格式

快捷键：
• Ctrl+R：刷新数据
• Ctrl+E：导出数据
• F1：显示帮助

提示：
• 程序会在后台自动记录您的应用使用情况
• 所有数据都存储在本地，保护您的隐私
• 长时间无操作会自动记录为空闲状态"""

        messagebox.showinfo("使用说明", help_text)

    def show_about(self):
        """显示关于信息"""
        about_text = """Focus-Insight v1.0

个人效率分析工具

一个精准、无感运行的私人效率助手，
帮助您了解时间分配，提高工作效率。

特性：
• 精确记录应用使用时间
• 浏览器页面监控
• 键盘鼠标活动分析
• 空闲状态检测
• 本地数据存储
• 可视化时间轴报告

开发语言：Python
界面框架：Tkinter
数据存储：SQLite

© 2025 Focus-Insight Team"""

        messagebox.showinfo("关于", about_text)

    def update_status(self, message):
        """更新状态栏"""
        self.status_bar.config(text=message)

    def update_last_update_time(self):
        """更新最后更新时间"""
        now = datetime.now().strftime("%H:%M:%S")
        self.update_time_label.config(text=f"最后更新: {now}")

    def on_closing(self):
        """窗口关闭事件"""
        if messagebox.askokcancel("退出", "确定要退出 Focus-Insight 吗？"):
            self.storage.close()
            self.root.destroy()

    def run(self):
        """运行应用程序"""
        self.root.mainloop()


# 测试代码
if __name__ == "__main__":
    app = MainWindow()
    app.run()