"""
时间轴组件
负责显示时间轴视图，类似RescueTime的风格
"""
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import matplotlib.patches as mpatches
from matplotlib.dates import DateFormatter, HourLocator, date2num
import matplotlib.font_manager as fm

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


class TimelineWidget:
    def __init__(self, parent, width=800, height=400):
        """
        初始化时间轴组件
        :param parent: 父容器
        :param width: 宽度
        :param height: 高度
        """
        self.parent = parent
        self.width = width
        self.height = height

        # 应用颜色映射
        self.app_colors = {
            'chrome.exe': '#4285F4',      # Google蓝
            'firefox.exe': '#FF6611',     # Firefox橙
            'msedge.exe': '#0078D4',      # Edge蓝
            'explorer.exe': '#00BCF2',    # Windows蓝
            'cmd.exe': '#000000',         # 黑色
            'python.exe': '#3776AB',      # Python蓝
            'zed.exe': '#FFA500',         # 橙色
            'code.exe': '#007ACC',        # VS Code蓝
            'default': '#888888'          # 默认灰色
        }

        # 创建主框架
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建控制面板
        self.create_control_panel()

        # 创建图表区域
        self.create_chart_area()

        # 创建详细信息区域
        self.create_detail_area()

    def create_control_panel(self):
        """创建控制面板"""
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # 日期选择
        ttk.Label(control_frame, text="选择日期:").pack(side=tk.LEFT, padx=(0, 5))

        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.date_entry = ttk.Entry(control_frame, textvariable=self.date_var, width=12)
        self.date_entry.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(control_frame, text="刷新", command=self.refresh_timeline).pack(side=tk.LEFT, padx=(0, 5))

        # 视图选择
        ttk.Label(control_frame, text="视图:").pack(side=tk.LEFT, padx=(10, 5))
        self.view_var = tk.StringVar(value="时间轴")
        view_combo = ttk.Combobox(control_frame, textvariable=self.view_var,
                                  values=["时间轴", "饼图", "条形图"], width=10, state="readonly")
        view_combo.pack(side=tk.LEFT)
        view_combo.bind("<<ComboboxSelected>>", self.on_view_changed)

    def create_chart_area(self):
        """创建图表区域"""
        # 创建matplotlib图形
        self.fig, self.ax = plt.subplots(figsize=(self.width/100, self.height/100), dpi=100)
        self.fig.patch.set_facecolor('white')

        # 创建canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 绑定鼠标事件
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_hover)

    def create_detail_area(self):
        """创建详细信息区域"""
        detail_frame = ttk.LabelFrame(self.main_frame, text="详细信息", padding=10)
        detail_frame.pack(fill=tk.X, pady=(10, 0))

        # 创建详细信息标签
        self.detail_text = tk.Text(detail_frame, height=4, wrap=tk.WORD)
        self.detail_text.pack(fill=tk.X)
        self.detail_text.insert('1.0', "将鼠标悬停在时间轴上查看详细信息...")
        self.detail_text.config(state=tk.DISABLED)

    def get_app_color(self, process_name: str) -> str:
        """获取应用颜色"""
        return self.app_colors.get(process_name.lower(), self.app_colors['default'])

    def draw_timeline(self, data: List[Dict[str, Any]]):
        """绘制时间轴"""
        self.ax.clear()

        print(f"开始绘制时间轴，数据条数: {len(data)}")

        if not data:
            self.ax.text(0.5, 0.5, '暂无数据\n请先运行监控程序收集数据', ha='center', va='center',
                        transform=self.ax.transAxes, fontsize=14)
            self.canvas.draw()
            return

        # 计算时间范围
        times = []
        colors = []
        labels = []
        durations = []

        for record in data:
            start_time = record['start_time']
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time)

            end_time = record['end_time']
            if isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time)

            times.append((start_time, end_time))
            colors.append(self.get_app_color(record['process_name']))
            labels.append(f"{record['process_name']}\n{record['window_title'][:30]}...")
            durations.append(record['duration'])

        print(f"处理了 {len(times)} 个时间块")

        # 绘制时间轴块
        y_pos = 0
        bar_height = 0.8

        for i, ((start_time, end_time), color, label) in enumerate(zip(times, colors, labels)):
            # 转换为matplotlib时间格式
            start_num = date2num(start_time)
            end_num = date2num(end_time)
            width = end_num - start_num

            # 绘制矩形块
            rect = Rectangle((start_num, y_pos), width, bar_height,
                           facecolor=color, edgecolor='white', linewidth=1,
                           picker=True)
            self.ax.add_patch(rect)

            # 存储矩形信息用于鼠标悬停
            rect.record = data[i]

        # 设置坐标轴
        if times:
            all_times = [t for time_pair in times for t in time_pair]
            min_time = min(all_times)
            max_time = max(all_times)

            # 扩展时间范围
            time_range = max_time - min_time
            if time_range.total_seconds() == 0:
                time_range = timedelta(hours=1)  # 至少显示1小时

            min_time = min_time - time_range * 0.05
            max_time = max_time + time_range * 0.05

            self.ax.set_xlim(min_time, max_time)
            self.ax.set_ylim(-0.5, 1.5)

            # 设置x轴格式
            self.ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
            self.ax.xaxis.set_major_locator(HourLocator(interval=2))

            # 旋转x轴标签
            plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right')

        # 隐藏y轴
        self.ax.set_yticks([])
        self.ax.set_ylabel('')

        # 设置标题
        self.ax.set_title('Timeline - Application Usage', fontsize=16, fontweight='bold', pad=20)

        # 添加网格
        self.ax.grid(True, axis='x', alpha=0.3)

        # 添加图例
        self.add_legend(data)

        # 调整布局
        self.fig.tight_layout()

        # 刷新画布
        self.canvas.draw()
        print("时间轴绘制完成")

    def add_legend(self, data: List[Dict[str, Any]]):
        """添加图例"""
        # 统计应用使用时间
        app_usage = {}
        for record in data:
            app = record['process_name']
            duration = record['duration']
            if app in app_usage:
                app_usage[app] += duration
            else:
                app_usage[app] = duration

        # 创建图例项
        legend_items = []
        for app, duration in sorted(app_usage.items(), key=lambda x: x[1], reverse=True)[:8]:
            color = self.get_app_color(app)
            label = f"{app} ({duration/60:.1f}分钟)"
            legend_items.append(mpatches.Patch(color=color, label=label))

        if legend_items:
            self.ax.legend(handles=legend_items, loc='upper right', fontsize=8)

    def draw_pie_chart(self, data: List[Dict[str, Any]]):
        """绘制饼图"""
        self.ax.clear()

        print(f"开始绘制饼图，数据条数: {len(data)}")

        if not data:
            self.ax.text(0.5, 0.5, '暂无数据\n请先运行监控程序收集数据', ha='center', va='center',
                        transform=self.ax.transAxes, fontsize=14)
            self.canvas.draw()
            return

        # 统计应用使用时间
        app_usage = {}
        for record in data:
            app = record['process_name']
            duration = record['duration']
            if app in app_usage:
                app_usage[app] += duration
            else:
                app_usage[app] = duration

        # 准备数据
        apps = list(app_usage.keys())
        durations = list(app_usage.values())
        colors = [self.get_app_color(app) for app in apps]

        print(f"饼图应用数: {len(apps)}")

        # 绘制饼图
        wedges, texts, autotexts = self.ax.pie(durations, labels=apps, colors=colors,
                                               autopct='%1.1f%%', startangle=90)

        # 设置标题
        self.ax.set_title('Application Usage Distribution', fontsize=16, fontweight='bold')

        # 调整布局
        self.fig.tight_layout()
        self.canvas.draw()
        print("饼图绘制完成")

    def draw_bar_chart(self, data: List[Dict[str, Any]]):
        """绘制条形图"""
        self.ax.clear()

        print(f"开始绘制条形图，数据条数: {len(data)}")

        if not data:
            self.ax.text(0.5, 0.5, '暂无数据\n请先运行监控程序收集数据', ha='center', va='center',
                        transform=self.ax.transAxes, fontsize=14)
            self.canvas.draw()
            return

        # 统计应用使用时间
        app_usage = {}
        for record in data:
            app = record['process_name']
            duration = record['duration']
            if app in app_usage:
                app_usage[app] += duration
            else:
                app_usage[app] = duration

        # 按使用时间排序
        sorted_apps = sorted(app_usage.items(), key=lambda x: x[1], reverse=True)[:10]

        if not sorted_apps:
            self.ax.text(0.5, 0.5, '暂无数据\n请先运行监控程序收集数据', ha='center', va='center',
                        transform=self.ax.transAxes, fontsize=14)
            self.canvas.draw()
            return

        apps = [item[0] for item in sorted_apps]
        durations = [item[1]/60 for item in sorted_apps]  # 转换为分钟
        colors = [self.get_app_color(app) for app in apps]

        print(f"条形图应用数: {len(apps)}")

        # 绘制条形图
        bars = self.ax.bar(range(len(apps)), durations, color=colors)

        # 设置标签
        self.ax.set_xticks(range(len(apps)))
        self.ax.set_xticklabels(apps, rotation=45, ha='right')
        self.ax.set_ylabel('Usage Time (minutes)')
        self.ax.set_title('Top Applications by Usage Time', fontsize=16, fontweight='bold')

        # 在条形图上显示数值
        for bar, duration in zip(bars, durations):
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{duration:.1f}', ha='center', va='bottom')

        # 调整布局
        self.fig.tight_layout()
        self.canvas.draw()
        print("条形图绘制完成")

    def on_mouse_hover(self, event):
        """处理鼠标悬停事件"""
        if event.inaxes != self.ax:
            return

        # 查找鼠标下的矩形
        for patch in self.ax.patches:
            if isinstance(patch, Rectangle) and hasattr(patch, 'record'):
                if patch.contains_point([event.x, event.y]):
                    self.show_detail_info(patch.record)
                    return

    def show_detail_info(self, record: Dict[str, Any]):
        """显示详细信息"""
        start_time = record['start_time']
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time)

        end_time = record['end_time']
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time)

        duration = record['duration']
        duration_str = f"{duration:.1f}秒 ({duration/60:.1f}分钟)"

        detail_text = f"""应用: {record['process_name']}
窗口标题: {record['window_title']}
开始时间: {start_time.strftime('%H:%M:%S')}
结束时间: {end_time.strftime('%H:%M:%S')}
持续时间: {duration_str}"""

        # 更新详细信息区域
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete('1.0', tk.END)
        self.detail_text.insert('1.0', detail_text)
        self.detail_text.config(state=tk.DISABLED)

    def on_view_changed(self, event):
        """处理视图切换"""
        view_type = self.view_var.get()
        # 这里会在主程序中处理
        if hasattr(self, 'on_view_change_callback'):
            self.on_view_change_callback(view_type)

    def refresh_timeline(self):
        """刷新时间轴"""
        if hasattr(self, 'refresh_callback'):
            self.refresh_callback()

    def set_data(self, data: List[Dict[str, Any]]):
        """设置数据并更新视图"""
        self.data = data
        view_type = self.view_var.get()

        if view_type == "时间轴":
            self.draw_timeline(data)
        elif view_type == "饼图":
            self.draw_pie_chart(data)
        elif view_type == "条形图":
            self.draw_bar_chart(data)

    def pack(self, **kwargs):
        """包装pack方法"""
        self.main_frame.pack(**kwargs)