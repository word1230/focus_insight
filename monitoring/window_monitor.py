"""
窗口监控模块
负责记录当前聚焦的顶层应用名称及其窗口标题
"""
import win32gui
import win32process
import win32api
import win32con
import time
from typing import Optional, Tuple
from datetime import datetime


class WindowMonitor:
    def __init__(self):
        self.current_window = None
        self.current_title = ""
        self.current_process = ""
        self.start_time = None
        self.callbacks = []

    def add_callback(self, callback):
        """添加数据回调函数"""
        self.callbacks.append(callback)

    def get_active_window_info(self) -> Optional[Tuple[str, str, str]]:
        """
        获取当前活动窗口信息
        返回: (进程名, 窗口标题, 窗口句柄)
        """
        try:
            # 获取前台窗口句柄
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return None

            # 获取窗口标题
            window_title = win32gui.GetWindowText(hwnd)
            if not window_title:
                window_title = "无标题窗口"

            # 获取进程信息
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
            try:
                # 尝试获取进程名
                exe_path = win32process.GetModuleFileNameEx(process, 0)
                process_name = exe_path.split('\\')[-1]
            except:
                process_name = f"进程_{pid}"
            finally:
                win32api.CloseHandle(process)

            return process_name, window_title, hwnd

        except Exception as e:
            print(f"获取窗口信息时出错: {e}")
            return None

    def check_window_change(self):
        """检查窗口是否发生变化"""
        window_info = self.get_active_window_info()

        if window_info is None:
            # 没有活动窗口
            if self.current_window is not None:
                self._record_window_end()
            return

        process_name, window_title, hwnd = window_info
        current_key = (process_name, window_title)

        # 检查是否发生了变化
        if self.current_window != current_key:
            # 记录上一个窗口的结束
            if self.current_window is not None:
                self._record_window_end()

            # 开始记录新窗口
            self.current_window = current_key
            self.current_process = process_name
            self.current_title = window_title
            self.start_time = datetime.now()

            print(f"窗口切换: {process_name} - {window_title}")

    def _record_window_end(self):
        """记录窗口使用结束"""
        if self.start_time is None:
            return

        end_time = datetime.now()
        duration = end_time - self.start_time

        # 构造记录数据
        record = {
            'process_name': self.current_process,
            'window_title': self.current_title,
            'start_time': self.start_time,
            'end_time': end_time,
            'duration': duration.total_seconds()
        }

        # 调用回调函数
        for i, callback in enumerate(self.callbacks):
            try:
                callback(record)
            except Exception as e:
                print(f"窗口监控回调函数 {i} 执行出错: {e}")
                import traceback
                traceback.print_exc()

    def start_monitoring(self, interval=1.0):
        """开始监控"""
        print("开始窗口监控...")
        while True:
            try:
                self.check_window_change()
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n停止窗口监控")
                break
            except Exception as e:
                print(f"监控过程中出错: {e}")
                time.sleep(interval)

    def stop_monitoring(self):
        """停止监控并记录最后一个窗口"""
        if self.current_window is not None:
            self._record_window_end()
        print("窗口监控已停止")


# 测试代码
if __name__ == "__main__":
    def test_callback(record):
        print(f"记录: {record['process_name']} - {record['window_title']} - {record['duration']:.2f}秒")

    monitor = WindowMonitor()
    monitor.add_callback(test_callback)

    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        monitor.stop_monitoring()