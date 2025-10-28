"""
数据库操作模块
负责创建和管理SQLite数据库
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional


class Database:
    def __init__(self, db_path: str = "focus_insight.db"):
        """
        初始化数据库
        :param db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.connection = None
        self.init_database()

    def init_database(self):
        """初始化数据库表结构"""
        # 确保数据目录存在
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else '.', exist_ok=True)

        # 连接数据库
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row  # 使结果可以按列名访问

        # 创建表
        self.create_tables()

    def create_tables(self):
        """创建所有必要的表"""
        cursor = self.connection.cursor()

        # 窗口活动记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS window_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                process_name TEXT NOT NULL,
                window_title TEXT NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP NOT NULL,
                duration REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 浏览器活动记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS browser_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                browser_name TEXT NOT NULL,
                page_title TEXT NOT NULL,
                page_url TEXT,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                duration REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 输入活动记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS input_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_type TEXT NOT NULL,  -- 'keyboard' 或 'mouse'
                event_count INTEGER NOT NULL,
                frequency_per_minute REAL NOT NULL,
                window_start TIMESTAMP NOT NULL,
                window_end TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 状态变化记录表（空闲/活跃切换）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS state_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state_type TEXT NOT NULL,  -- 'idle' 或 'active'
                timestamp TIMESTAMP NOT NULL,
                idle_duration REAL,  -- 如果是idle状态，记录空闲时长
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 应用统计表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                process_name TEXT NOT NULL,
                window_title TEXT,
                total_duration REAL NOT NULL,
                session_count INTEGER NOT NULL,
                last_used TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(process_name, window_title)
            )
        ''')

        # 提交更改
        self.connection.commit()

    def insert_window_activity(self, process_name: str, window_title: str,
                              start_time: datetime, end_time: datetime, duration: float):
        """插入窗口活动记录"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO window_activities
            (process_name, window_title, start_time, end_time, duration)
            VALUES (?, ?, ?, ?, ?)
        ''', (process_name, window_title, start_time, end_time, duration))
        self.connection.commit()

        # 更新应用统计
        self._update_app_statistics(process_name, window_title, duration, end_time)

    def insert_browser_activity(self, browser_name: str, page_title: str, page_url: str,
                               start_time: datetime, end_time: Optional[datetime] = None,
                               duration: Optional[float] = None):
        """插入浏览器活动记录"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO browser_activities
            (browser_name, page_title, page_url, start_time, end_time, duration)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (browser_name, page_title, page_url, start_time, end_time, duration))
        self.connection.commit()

    def insert_input_activity(self, activity_type: str, event_count: int, frequency: float,
                             window_start: datetime, window_end: datetime):
        """插入输入活动记录"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO input_activities
            (activity_type, event_count, frequency_per_minute, window_start, window_end)
            VALUES (?, ?, ?, ?, ?)
        ''', (activity_type, event_count, frequency, window_start, window_end))
        self.connection.commit()

    def insert_state_change(self, state_type: str, timestamp: datetime, idle_duration: Optional[float] = None):
        """插入状态变化记录"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO state_changes
            (state_type, timestamp, idle_duration)
            VALUES (?, ?, ?)
        ''', (state_type, timestamp, idle_duration))
        self.connection.commit()

    def _update_app_statistics(self, process_name: str, window_title: str, duration: float, last_used: datetime):
        """更新应用统计信息"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO app_statistics
            (process_name, window_title, total_duration, session_count, last_used, updated_at)
            VALUES (
                ?, ?,
                COALESCE((SELECT total_duration FROM app_statistics
                         WHERE process_name = ? AND window_title = ?), 0) + ?,
                COALESCE((SELECT session_count FROM app_statistics
                         WHERE process_name = ? AND window_title = ?), 0) + 1,
                ?, CURRENT_TIMESTAMP
            )
        ''', (process_name, window_title, process_name, window_title, duration,
              process_name, window_title, last_used))
        self.connection.commit()

    def get_window_activities(self, start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None) -> List[Dict]:
        """获取窗口活动记录"""
        cursor = self.connection.cursor()
        query = "SELECT * FROM window_activities WHERE 1=1"
        params = []

        if start_date:
            query += " AND start_time >= ?"
            params.append(start_date)

        if end_date:
            query += " AND start_time <= ?"
            params.append(end_date)

        query += " ORDER BY start_time DESC"

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_browser_activities(self, start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None) -> List[Dict]:
        """获取浏览器活动记录"""
        cursor = self.connection.cursor()
        query = "SELECT * FROM browser_activities WHERE 1=1"
        params = []

        if start_date:
            query += " AND start_time >= ?"
            params.append(start_date)

        if end_date:
            query += " AND start_time <= ?"
            params.append(end_date)

        query += " ORDER BY start_time DESC"

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_app_statistics(self, limit: int = 10) -> List[Dict]:
        """获取应用使用统计"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM app_statistics
            ORDER BY total_duration DESC
            LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def get_daily_summary(self, date: datetime) -> Dict:
        """获取某天的使用摘要"""
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day.replace(hour=23, minute=59, second=59, microsecond=999999)

        cursor = self.connection.cursor()

        # 总活跃时间
        cursor.execute('''
            SELECT SUM(duration) as total_time
            FROM window_activities
            WHERE start_time >= ? AND start_time <= ?
        ''', (start_of_day, end_of_day))
        total_time = cursor.fetchone()['total_time'] or 0

        # 应用数量
        cursor.execute('''
            SELECT COUNT(DISTINCT process_name) as app_count
            FROM window_activities
            WHERE start_time >= ? AND start_time <= ?
        ''', (start_of_day, end_of_day))
        app_count = cursor.fetchone()['app_count'] or 0

        # 空闲时间
        cursor.execute('''
            SELECT SUM(idle_duration) as idle_time
            FROM state_changes
            WHERE state_type = 'idle' AND timestamp >= ? AND timestamp <= ?
        ''', (start_of_day, end_of_day))
        idle_time = cursor.fetchone()['idle_time'] or 0

        return {
            'date': date.date(),
            'total_active_time': total_time,
            'total_idle_time': idle_time,
            'app_count': app_count,
            'focus_efficiency': (total_time / (total_time + idle_time) * 100) if (total_time + idle_time) > 0 else 0
        }

    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()

    def __del__(self):
        """析构函数，确保数据库连接被关闭"""
        self.close()


# 测试代码
if __name__ == "__main__":
    # 测试数据库功能
    db = Database("test_focus_insight.db")

    print("数据库初始化完成")

    # 测试插入数据
    start_time = datetime.now()
    end_time = datetime.now()
    duration = 10.5

    db.insert_window_activity("test.exe", "测试窗口", start_time, end_time, duration)
    print("插入窗口活动记录成功")

    # 测试查询
    activities = db.get_window_activities()
    print(f"查询到 {len(activities)} 条记录")

    # 测试统计
    stats = db.get_app_statistics()
    print(f"应用统计: {stats}")

    # 清理测试文件
    db.close()
    os.remove("test_focus_insight.db")
    print("测试完成，数据库文件已清理")