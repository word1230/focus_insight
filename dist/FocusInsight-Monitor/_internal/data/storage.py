"""
数据存储模块
负责管理所有监控数据的存储
"""
import os
from datetime import datetime
from typing import Dict, Any, Optional
from .database import Database


class DataStorage:
    def __init__(self, data_dir: str = "data"):
        """
        初始化数据存储
        :param data_dir: 数据目录
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        # 初始化数据库
        db_path = os.path.join(data_dir, "focus_insight.db")
        self.db = Database(db_path)

        # 当前会话的临时数据
        self.current_window_session = None
        self.current_browser_session = None

    def start_window_session(self, process_name: str, window_title: str):
        """开始窗口会话"""
        self.current_window_session = {
            'process_name': process_name,
            'window_title': window_title,
            'start_time': datetime.now()
        }

    def end_window_session(self):
        """结束窗口会话并保存到数据库"""
        if self.current_window_session is None:
            return

        end_time = datetime.now()
        start_time = self.current_window_session['start_time']
        duration = (end_time - start_time).total_seconds()

        # 保存到数据库
        self.db.insert_window_activity(
            process_name=self.current_window_session['process_name'],
            window_title=self.current_window_session['window_title'],
            start_time=start_time,
            end_time=end_time,
            duration=duration
        )

        print(f"保存窗口记录: {self.current_window_session['process_name']} - {duration:.1f}秒")
        self.current_window_session = None

    def start_browser_session(self, browser_name: str, page_title: str, page_url: str):
        """开始浏览器会话"""
        self.current_browser_session = {
            'browser_name': browser_name,
            'page_title': page_title,
            'page_url': page_url,
            'start_time': datetime.now()
        }

    def end_browser_session(self):
        """结束浏览器会话并保存到数据库"""
        if self.current_browser_session is None:
            return

        end_time = datetime.now()
        start_time = self.current_browser_session['start_time']
        duration = (end_time - start_time).total_seconds()

        # 保存到数据库
        self.db.insert_browser_activity(
            browser_name=self.current_browser_session['browser_name'],
            page_title=self.current_browser_session['page_title'],
            page_url=self.current_browser_session['page_url'],
            start_time=start_time,
            end_time=end_time,
            duration=duration
        )

        print(f"保存浏览器记录: {self.current_browser_session['browser_name']} - {duration:.1f}秒")
        self.current_browser_session = None

    def save_input_activity(self, activity_type: str, event_count: int, frequency: float):
        """保存输入活动记录"""
        window_start = datetime.now().replace(second=0, microsecond=0)
        window_end = window_start.replace(second=59, microsecond=999999)

        self.db.insert_input_activity(
            activity_type=activity_type,
            event_count=event_count,
            frequency=frequency,
            window_start=window_start,
            window_end=window_end
        )

    def save_state_change(self, state_type: str, idle_duration: Optional[float] = None):
        """保存状态变化记录"""
        self.db.insert_state_change(
            state_type=state_type,
            timestamp=datetime.now(),
            idle_duration=idle_duration
        )

    def get_today_summary(self) -> Dict[str, Any]:
        """获取今日使用摘要"""
        return self.db.get_daily_summary(datetime.now())

    def get_top_apps(self, limit: int = 10) -> list:
        """获取使用时间最长的应用"""
        return self.db.get_app_statistics(limit)

    def export_data(self, start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """导出数据"""
        return {
            'window_activities': self.db.get_window_activities(start_date, end_date),
            'browser_activities': self.db.get_browser_activities(start_date, end_date),
            'app_statistics': self.db.get_app_statistics(),
            'daily_summary': self.get_today_summary()
        }

    def cleanup_old_data(self, days_to_keep: int = 30):
        """清理旧数据"""
        cutoff_date = datetime.now() - datetime.timedelta(days=days_to_keep)
        # 这里可以添加清理逻辑，暂时保留所有数据
        print(f"清理 {cutoff_date} 之前的数据（功能待实现）")

    def close(self):
        """关闭数据存储"""
        # 结束当前会话
        self.end_window_session()
        self.end_browser_session()

        # 关闭数据库
        self.db.close()


# 测试代码
if __name__ == "__main__":
    # 创建测试数据目录
    test_data_dir = "test_data"
    storage = DataStorage(test_data_dir)

    print("数据存储初始化完成")

    # 测试窗口会话
    storage.start_window_session("test.exe", "测试窗口")
    import time
    time.sleep(1)
    storage.end_window_session()

    # 测试浏览器会话
    storage.start_browser_session("Chrome", "测试页面", "https://example.com")
    time.sleep(1)
    storage.end_browser_session()

    # 测试输入活动
    storage.save_input_activity("keyboard", 50, 25.5)

    # 测试状态变化
    storage.save_state_change("active")
    storage.save_state_change("idle", 120.5)

    # 测试数据查询
    summary = storage.get_today_summary()
    print(f"今日摘要: {summary}")

    top_apps = storage.get_top_apps(5)
    print(f"热门应用: {top_apps}")

    # 清理测试数据
    storage.close()
    import shutil
    shutil.rmtree(test_data_dir)
    print("测试完成，测试数据已清理")