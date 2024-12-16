# @Time  :2024/12/15 14:52
# @Author: yutian.li
# @Email : lyutian2020@qq.com
from sqlmodel import SQLModel, Field, ForeignKey,create_engine,Session
from typing import Optional
from datetime import datetime


class History(SQLModel, table=True):
    __tablename__ = "history"  # type:ignore
    hid: int = Field(default=None, primary_key=True)
    user_id: str = Field(sa_column_kwargs={"nullable": False})
    history_name: str = Field(default=None, max_length=64, sa_column_kwargs={"nullable": False})
    # 直接设置为 str，SQLModel 将其视为 TEXT 类型
    history_content: str = Field(default=None, sa_column_kwargs={"nullable": True})  # 使用 TEXT 类型
    created_time: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})
    updated_time: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})
    remark: str = Field(default=None, max_length=2048, sa_column_kwargs={"nullable": True})
    is_del: int = Field(default=0, sa_column_kwargs={"nullable": False})  # 0 表示未删除，1 表示已删除

class User(SQLModel, table=True):
    __tablename__ = "user"  # type:ignore
    uid: int = Field(default=None, primary_key=True)
    user_id: str = Field(sa_column_kwargs={"nullable": False})
    user_name: str = Field(default=None, max_length=64, sa_column_kwargs={"nullable": False})
    password: str = Field(default=None, max_length=64, sa_column_kwargs={"nullable": False})
    created_time: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})
    updated_time: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})
    remark: str = Field(default=None, max_length=2048, sa_column_kwargs={"nullable": True})
    is_del: int = Field(default=0, sa_column_kwargs={"nullable": False})  # 0 表示未删除，1 表示已删除

class Knowledge(SQLModel, table=True):
    __tablename__ = "knowledge"  # type:ignore
    klid: int = Field(default=None, primary_key=True)
    user_id: str = Field(sa_column_kwargs={"nullable": False})
    knowledge_vector_name: str = Field(default=None, max_length=64, sa_column_kwargs={"nullable": False})
    knowledge_vector_path: str = Field(default=None, max_length=256, sa_column_kwargs={"nullable": False})

    # 外键引用 FileToDir 表的 file_dir_id
    file_dir_id: int = Field(default=None, sa_column_kwargs={"nullable": False}, foreign_key="file_dir.file_dir_id")

    embedding_model_name: str = Field(default=None, max_length=64, sa_column_kwargs={"nullable": False})
    created_time: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})
    updated_time: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})
    remark: str = Field(default=None, max_length=2048, sa_column_kwargs={"nullable": True})
    is_del: int = Field(default=0, sa_column_kwargs={"nullable": False})  # 0 表示未删除，1 表示已删除


class File(SQLModel, table=True):
    __tablename__ = "file"  # type:ignore
    fid: int = Field(default=None, primary_key=True)
    file_name: str = Field(default=None, max_length=256, sa_column_kwargs={"nullable": False})  # 文件名，不能为空
    file_path: str = Field(default=None, max_length=512, sa_column_kwargs={"nullable": False})  # 文件路径，不能为空

    # 外键引用 FileToDir 表的 file_dir_id
    file_dir_id: int = Field(default=None, sa_column_kwargs={"nullable": False}, foreign_key="file_dir.file_dir_id")

    created_time: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})  # 创建时间，不能为空
    updated_time: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})  # 更新时间，不能为空
    remark: str = Field(default=None, max_length=2048, sa_column_kwargs={"nullable": True})  # 备注信息，最大长度为2048，可以为空
    is_del: int = Field(default=0, sa_column_kwargs={"nullable": False})  # 删除标识，0 表示未删除，1 表示已删除


class FileToDir(SQLModel, table=True):
    __tablename__ = "file_dir"  # type:ignore
    file_dir_id: int = Field(default=None, primary_key=True)
    file_dir_path: str = Field(default=None, max_length=256, sa_column_kwargs={"nullable": False})  # 文件夹路径，不能为空

    created_time: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})  # 创建时间，不能为空
    updated_time: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"nullable": False})  # 更新时间，不能为空
    remark: str = Field(default=None, max_length=2048, sa_column_kwargs={"nullable": True})  # 备注信息，最大长度为2048，可以为空
    is_del: int = Field(default=0, sa_column_kwargs={"nullable": False})  # 删除标识，0 表示未删除，1 表示已删除
    # 新增字段
    user_id: str = Field(default=None, max_length=100, sa_column_kwargs={"nullable": False})  # 用户ID，不能为空
    file_dir_name: str = Field(default=None, max_length=256, sa_column_kwargs={"nullable": False})  # 文件目录名称，不能为空



