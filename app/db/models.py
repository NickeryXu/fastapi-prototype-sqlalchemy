from sqlalchemy import Boolean, Column, Integer, Text, REAL, VARCHAR

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(VARCHAR(50), unique=True, index=True)
    hashed_password = Column(VARCHAR(100))
    salt = Column(VARCHAR(100))
    is_admin = Column(Boolean, default=False)


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(VARCHAR(50))
    status = Column(Integer)
    create_time = Column(Text)
    update_time = Column(Text)


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    case_name = Column(VARCHAR(50))
    sample_id = Column(Integer)
    status = Column(Integer)
    score = Column(REAL)
    create_time = Column(Text)


class Setting(Base):
    __tablename__ = "setting"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    debug = Column(Boolean, nullable=True)  # 运行模式, 测试运行，正式运行
    src_path = Column(VARCHAR(200), nullable=True)  # 原始文件监控目录
    export_path = Column(VARCHAR(200), nullable=True)  # 导出文件监控目录
    dest_path = Column(VARCHAR(200), nullable=True)  # 导出文件存储目录
    tmp_path = Column(VARCHAR(200), nullable=True)  # 排序暂存目录
    src_ext = Column(VARCHAR(200), nullable=True)  # 原文件扩展名
    export_ext = Column(VARCHAR(200), nullable=True)  # 导出文件扩展名
    sort_simulation = Column(Boolean, nullable=True) # 模拟排序
    worker_check_interval = Column(Integer, nullable=True)  # 文件监控间隔（秒）
