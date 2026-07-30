"""
学生信息数据库初始化脚本
创建 SQLite3 数据库 students.db 并写入示例学生信息
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "students.db")


def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            major TEXT,
            grade TEXT,
            class_name TEXT,
            gpa REAL,
            email TEXT,
            phone TEXT,
            enrollment_date TEXT
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        sample_students = [
            ("2024001", "张三", 20, "男", "计算机科学与技术", "2024级", "计科1班", 3.85, "zhangsan@school.edu", "13800000001", "2024-09-01"),
            ("2024002", "李四", 19, "女", "软件工程", "2024级", "软工2班", 3.72, "lisi@school.edu", "13800000002", "2024-09-01"),
            ("2024003", "王五", 21, "男", "人工智能", "2023级", "AI1班", 3.95, "wangwu@school.edu", "13800000003", "2023-09-01"),
            ("2024004", "赵六", 20, "女", "数据科学", "2023级", "数据1班", 3.60, "zhaoliu@school.edu", "13800000004", "2023-09-01"),
            ("2024005", "钱七", 22, "男", "计算机科学与技术", "2022级", "计科2班", 3.45, "qianqi@school.edu", "13800000005", "2022-09-01"),
            ("2024006", "孙八", 19, "女", "软件工程", "2024级", "软工1班", 3.88, "sunba@school.edu", "13800000006", "2024-09-01"),
            ("2024007", "周九", 20, "男", "网络工程", "2023级", "网工1班", 3.20, "zhoujiu@school.edu", "13800000007", "2023-09-01"),
            ("2024008", "吴十", 21, "女", "人工智能", "2022级", "AI2班", 3.91, "wushi@school.edu", "13800000008", "2022-09-01"),
            ("2024009", "郑十一", 19, "男", "数据科学", "2024级", "数据2班", 3.55, "zhengshiyi@school.edu", "13800000009", "2024-09-01"),
            ("2024010", "王十二", 22, "女", "计算机科学与技术", "2022级", "计科3班", 3.78, "wangshier@school.edu", "13800000010", "2022-09-01"),
        ]
        cursor.executemany("""
            INSERT INTO students (
                student_id, name, age, gender, major, grade, class_name,
                gpa, email, phone, enrollment_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_students)
        conn.commit()
        print(f"已写入 {len(sample_students)} 条学生记录")
    else:
        print("学生表已存在,跳过写入")

    cursor.execute("SELECT COUNT(*) FROM students")
    total = cursor.fetchone()[0]
    print(f"数据库路径: {DB_PATH}")
    print(f"当前学生总数: {total}")

    conn.close()


if __name__ == "__main__":
    init_database()
