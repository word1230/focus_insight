"""
输入监控模块
负责记录键盘和鼠标活动频率，以及检测空闲状态
"""
import time
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional
from collections import deque
from pynput import mouse, keyboard


class InputMonitor:
    def __init__(self, idle_threshold=300):  # 5分钟 = 300秒
        """
        初始化输入监控器
        :param idle_threshold: 空闲阈值（秒），默认5分钟
        """
        self.idle_threshold = idle_threshold
        self.callbacks = []

        # 记录输入事件的队列（用于计算频率）
        self.keyboard_events = deque(maxlen=60)  # 保存最近60个键盘事件
        self.mouse_events = deque(maxlen=60)     # 保存最近60个鼠标事件

        # 最后活动时间
        self.last_activity_time = datetime.now()

        # 监听器
        self.keyboard_listener = None
        self.mouse_listener = None

        # 统计数据
        self.keyboard_count = 0
        self.mouse_count = 0
        self.is_idle = False

        # 监控状态
        self.is_monitoring = False

    def add_callback(self, callback: Callable):
        """添加状态变化回调函数"""
        self.callbacks.append(callback)

    def on_key_press(self, key):
        """键盘按键事件处理"""
        current_time = datetime.now()
        self.last_activity_time = current_time
        self.keyboard_count += 1

        # 记录事件时间
        self.keyboard_events.append(current_time)

        # 如果之前是空闲状态，现在变为活跃状态
        if self.is_idle:
            self.is_idle = False
            self._notify_state_change('active')

    def on_mouse_click(self, x, y, button, pressed):
        """鼠标点击事件处理"""
        if not pressed:  # 只处理释放事件，避免重复计数
            return

        current_time = datetime.now()
        self.last_activity_time = current_time
        self.mouse_count += 1

        # 记录事件时间
        self.mouse_events.append(current_time)

        # 如果之前是空闲状态，现在变为活跃状态
        if self.is_idle:
            self.is_idle = False
            self._notify_state_change('active')

    def _notify_state_change(self, state: str):
        """通知状态变化"""
        record = {
            'type': 'state_change',
            'state': state,
            'timestamp': datetime.now(),
            'idle_duration': None
        }

        if state == 'idle':
            record['idle_duration'] = datetime.now() - self.last_activity_time

        for callback in self.callbacks:
            try:
                callback(record)
            except Exception as e:
                print(f"输入监控回调函数执行出错: {e}")

    def get_keyboard_frequency(self, window_seconds=60) -> float:
        """
        获取键盘输入频率（次/分钟）
        :param window_seconds: 统计时间窗口（秒）
        :return: 键盘输入频率
        """
        if not self.keyboard_events:
            return 0.0

        current_time = datetime.now()
        cutoff_time = current_time - timedelta(seconds=window_seconds)

        # 统计时间窗口内的事件数
        recent_events = [event for event in self.keyboard_events if event > cutoff_time]

        # 转换为每分钟频率
        frequency = len(recent_events) * (60.0 / window_seconds)
        return frequency

    def get_mouse_frequency(self, window_seconds=60) -> float:
        """
        获取鼠标点击频率（次/分钟）
        :param window_seconds: 统计时间窗口（秒）
        :return: 鼠标点击频率
        """
        if not self.mouse_events:
            return 0.0

        current_time = datetime.now()
        cutoff_time = current_time - timedelta(seconds=window_seconds)

        # 统计时间窗口内的事件数
        recent_events = [event for event in self.mouse_events if event > cutoff_time]

        # 转换为每分钟频率
        frequency = len(recent_events) * (60.0 / window_seconds)
        return frequency

    def check_idle_status(self):
        """检查空闲状态"""
        current_time = datetime.now()
        idle_duration = (current_time - self.last_activity_time).total_seconds()

        # 如果超过空闲阈值且当前不是空闲状态
        if idle_duration >= self.idle_threshold and not self.is_idle:
            self.is_idle = True
            self._notify_state_change('idle')
            print(f"用户进入空闲状态，空闲时长: {idle_duration:.1f}秒")

    def get_activity_summary(self) -> Dict:
        """获取活动摘要"""
        return {
            'keyboard_frequency': self.get_keyboard_frequency(),
            'mouse_frequency': self.get_mouse_frequency(),
            'total_keyboard_events': self.keyboard_count,
            'total_mouse_events': self.mouse_count,
            'is_idle': self.is_idle,
            'last_activity': self.last_activity_time,
            'idle_duration': (datetime.now() - self.last_activity_time).total_seconds()
        }

    def start_monitoring(self):
        """开始监控"""
        if self.is_monitoring:
            print("输入监控已在运行中")
            return

        print("开始输入监控...")
        self.is_monitoring = True

        # 启动键盘监听器
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()

        # 启动鼠标监听器
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        self.mouse_listener.start()

        print("键盘和鼠标监控已启动")

    def stop_monitoring(self):
        """停止监控"""
        if not self.is_monitoring:
            return

        print("停止输入监控...")
        self.is_monitoring = False

        # 停止监听器
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()

        print("输入监控已停止")

    def __del__(self):
        """析构函数，确保监听器被正确停止"""
        self.stop_monitoring()


# 测试代码
if __name__ == "__main__":
    def test_callback(record):
        if record['type'] == 'state_change':
            print(f"状态变化: {record['state']} at {record['timestamp']}")

    monitor = InputMonitor(idle_threshold=10)  # 测试用10秒空闲阈值

    monitor.add_callback(test_callback)
    monitor.start_monitoring()

    try:
        print("输入监控测试运行中，请尝试键盘输入和鼠标点击...")
        print("10秒无操作将进入空闲状态")
        while True:
            monitor.check_idle_status()
            summary = monitor.get_activity_summary()
            print(f"\r键盘频率: {summary['keyboard_frequency']:.1f}/分钟, "
                  f"鼠标频率: {summary['mouse_frequency']:.1f}/分钟, "
                  f"空闲: {'是' if summary['is_idle'] else '否'}", end="")
            time.sleep(2)
    except KeyboardInterrupt:
        monitor.stop_monitoring()
        print("\n测试结束")