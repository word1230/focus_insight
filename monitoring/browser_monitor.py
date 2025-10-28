"""
浏览器页面监控模块
负责精确记录浏览器当前活动标签页的URL和标题
"""
import time
from typing import Optional, Dict, Any
from datetime import datetime


class BrowserMonitor:
    def __init__(self):
        self.browsers = {
            'chrome.exe': 'Chrome',
            'firefox.exe': 'Firefox',
            'msedge.exe': 'Edge',
            'iexplore.exe': 'Internet Explorer',
            'opera.exe': 'Opera'
        }
        self.current_tab_info = None
        self.callbacks = []

    def add_callback(self, callback):
        """添加数据回调函数"""
        self.callbacks.append(callback)

    def is_browser_process(self, process_name: str) -> bool:
        """检查是否为浏览器进程"""
        return process_name.lower() in self.browsers

    def get_browser_name(self, process_name: str) -> str:
        """获取浏览器名称"""
        return self.browsers.get(process_name.lower(), process_name)

    def get_chrome_tab_info(self) -> Optional[Dict[str, Any]]:
        """通过Chrome进程获取当前标签页信息（简化版本）"""
        try:
            # 这里使用简化的方法，实际项目中可以使用Chrome DevTools Protocol
            # 暂时返回模拟数据，后续可以扩展
            import win32gui
            import win32process

            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            # 获取窗口标题，Chrome的标题通常包含页面标题
            window_title = win32gui.GetWindowText(hwnd)

            if window_title:
                # Chrome标题格式通常是: "页面标题 - Google Chrome"
                if " - Google Chrome" in window_title:
                    page_title = window_title.replace(" - Google Chrome", "")
                    return {
                        'browser': 'Chrome',
                        'title': page_title,
                        'url': 'chrome://detecting',  # 暂时使用占位符
                        'timestamp': datetime.now()
                    }

            return None
        except Exception as e:
            print(f"获取Chrome标签页信息时出错: {e}")
            return None

    def get_edge_tab_info(self) -> Optional[Dict[str, Any]]:
        """通过Edge进程获取当前标签页信息"""
        try:
            import win32gui
            import win32process

            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            window_title = win32gui.GetWindowText(hwnd)

            if window_title and " - Microsoft Edge" in window_title:
                page_title = window_title.replace(" - Microsoft Edge", "")
                return {
                    'browser': 'Edge',
                    'title': page_title,
                    'url': 'edge://detecting',  # 暂时使用占位符
                    'timestamp': datetime.now()
                }

            return None
        except Exception as e:
            print(f"获取Edge标签页信息时出错: {e}")
            return None

    def get_firefox_tab_info(self) -> Optional[Dict[str, Any]]:
        """通过Firefox进程获取当前标签页信息"""
        try:
            import win32gui
            import win32process

            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            window_title = win32gui.GetWindowText(hwnd)

            if window_title and " - Mozilla Firefox" in window_title:
                page_title = window_title.replace(" - Mozilla Firefox", "")
                return {
                    'browser': 'Firefox',
                    'title': page_title,
                    'url': 'about:blank',  # 暂时使用占位符
                    'timestamp': datetime.now()
                }

            return None
        except Exception as e:
            print(f"获取Firefox标签页信息时出错: {e}")
            return None

    def get_current_tab_info(self, process_name: str) -> Optional[Dict[str, Any]]:
        """根据进程名获取当前标签页信息"""
        process_lower = process_name.lower()

        if 'chrome.exe' in process_lower:
            return self.get_chrome_tab_info()
        elif 'msedge.exe' in process_lower:
            return self.get_edge_tab_info()
        elif 'firefox.exe' in process_lower:
            return self.get_firefox_tab_info()
        else:
            return None

    def check_tab_change(self, process_name: str):
        """检查浏览器标签页是否发生变化"""
        if not self.is_browser_process(process_name):
            return

        tab_info = self.get_current_tab_info(process_name)

        if tab_info is None:
            if self.current_tab_info is not None:
                self._record_tab_end()
            return

        # 检查是否发生了变化
        if self.current_tab_info != tab_info:
            # 记录上一个标签页的结束
            if self.current_tab_info is not None:
                self._record_tab_end()

            # 开始记录新标签页
            self.current_tab_info = tab_info
            print(f"浏览器标签页切换: {tab_info['browser']} - {tab_info['title']}")

    def _record_tab_end(self):
        """记录标签页使用结束"""
        if self.current_tab_info is None:
            return

        # 构造记录数据
        record = {
            'browser': self.current_tab_info['browser'],
            'title': self.current_tab_info['title'],
            'url': self.current_tab_info['url'],
            'timestamp': self.current_tab_info['timestamp']
        }

        # 调用回调函数
        for i, callback in enumerate(self.callbacks):
            try:
                callback(record)
            except Exception as e:
                print(f"浏览器监控回调函数 {i} 执行出错: {e}")
                import traceback
                traceback.print_exc()

    def stop_monitoring(self):
        """停止监控并记录最后一个标签页"""
        if self.current_tab_info is not None:
            self._record_tab_end()
        print("浏览器监控已停止")


# 测试代码
if __name__ == "__main__":
    def test_callback(record):
        print(f"浏览器记录: {record['browser']} - {record['title']} - {record['url']}")

    monitor = BrowserMonitor()
    monitor.add_callback(test_callback)

    # 测试Chrome
    print("测试浏览器监控...")
    chrome_info = monitor.get_chrome_tab_info()
    if chrome_info:
        print(f"Chrome标签页: {chrome_info['title']}")