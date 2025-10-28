"""
主程序入口
集成所有监控功能并实现数据存储
"""
import sys
import os
import time

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from monitoring.window_monitor import WindowMonitor
from monitoring.browser_monitor import BrowserMonitor
from monitoring.input_monitor import InputMonitor
from data.storage import DataStorage


def main():
    """主函数 - 完整的监控和数据存储功能"""
    print("=== Focus-Insight 完整版监控 ===")
    print("监控已启动，所有数据将保存到本地数据库...")
    print("包括：窗口监控、浏览器标签页监控、键盘鼠标活动监控")
    print("按 Ctrl+C 停止监控\n")

    # 创建数据存储
    storage = DataStorage()

    # 创建监控器
    window_monitor = WindowMonitor()
    browser_monitor = BrowserMonitor()
    input_monitor = InputMonitor(idle_threshold=30)  # 测试用30秒空闲阈值

    # 添加窗口监控回调 - 同时显示和保存数据
    def handle_window_record(record):
        duration = record['duration']
        process = record['process_name']
        title = record['window_title'][:50] + "..." if len(record['window_title']) > 50 else record['window_title']
        print(f"📊 [{duration:6.1f}s] {process} - {title}")

        # 保存到数据库
        storage.db.insert_window_activity(
            process_name=process,
            window_title=record['window_title'],
            start_time=record['start_time'],
            end_time=record['end_time'],
            duration=duration
        )

    # 添加浏览器监控回调
    def handle_browser_record(record):
        browser = record['browser']
        title = record['title'][:40] + "..." if len(record['title']) > 40 else record['title']
        print(f"🌐 [浏览器] {browser} - {title}")

        # 保存到数据库
        storage.db.insert_browser_activity(
            browser_name=browser,
            page_title=record['title'],
            page_url=record['url'],
            start_time=record['timestamp']
        )

    # 添加输入监控回调
    def handle_input_record(record):
        if record['type'] == 'state_change':
            if record['state'] == 'idle':
                duration = record['idle_duration'].total_seconds() if record['idle_duration'] else 0
                print(f"😴 [空闲状态] 用户已空闲 {duration:.1f}秒")
                storage.save_state_change('idle', duration)
            else:
                print(f"👆 [活跃状态] 用户恢复活动")
                storage.save_state_change('active')

    window_monitor.add_callback(handle_window_record)
    browser_monitor.add_callback(handle_browser_record)
    input_monitor.add_callback(handle_input_record)

    try:
        # 开始输入监控
        input_monitor.start_monitoring()

        # 开始窗口和浏览器监控
        print("开始监控所有活动...")
        last_summary_time = time.time()
        last_data_save_time = time.time()

        while True:
            window_monitor.check_window_change()

            # 如果当前窗口是浏览器，检查标签页变化
            window_info = window_monitor.get_active_window_info()
            if window_info:
                process_name = window_info[0]
                browser_monitor.check_tab_change(process_name)

            # 检查空闲状态
            input_monitor.check_idle_status()

            # 每5秒显示一次活动摘要
            current_time = time.time()
            if current_time - last_summary_time >= 5:
                summary = input_monitor.get_activity_summary()
                print(f"⌨️  键盘: {summary['keyboard_frequency']:.1f}/分钟  "
                      f"🖱️  鼠标: {summary['mouse_frequency']:.1f}/分钟  "
                      f"💤 空闲: {'是' if summary['is_idle'] else '否'}")
                last_summary_time = current_time

            # 每30秒保存一次输入活动数据
            if current_time - last_data_save_time >= 30:
                storage.save_input_activity('keyboard', summary['total_keyboard_events'], summary['keyboard_frequency'])
                storage.save_input_activity('mouse', summary['total_mouse_events'], summary['mouse_frequency'])
                last_data_save_time = current_time

            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\n正在停止监控并保存数据...")
        window_monitor.stop_monitoring()
        browser_monitor.stop_monitoring()
        input_monitor.stop_monitoring()

        # 显示今日统计
        print("\n=== 今日使用统计 ===")
        summary = storage.get_today_summary()
        print(f"总活跃时间: {summary['total_active_time']:.1f} 秒 ({summary['total_active_time']/3600:.2f} 小时)")
        print(f"总空闲时间: {summary['total_idle_time']:.1f} 秒")
        print(f"使用应用数量: {summary['app_count']} 个")
        print(f"专注效率: {summary['focus_efficiency']:.1f}%")

        print("\n=== 使用时间最长的应用 ===")
        top_apps = storage.get_top_apps(5)
        for i, app in enumerate(top_apps, 1):
            hours = app['total_duration'] / 3600
            print(f"{i}. {app['process_name']} - {hours:.2f} 小时")

        # 关闭数据存储
        storage.close()
        print("\n监控已停止，数据已保存")


if __name__ == "__main__":
    main()