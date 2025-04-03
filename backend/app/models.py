"""
模型定义文件

"""

from datetime import datetime, timezone
from app import db


class SystemLog(db.Model):
    """
    系统日志模型
    用于记录系统中的操作日志，包括用户操作、项目管理和任务管理等。
    包含日志级别(level)、操作类型(action_type)、用户ID(user_id)、时间戳(timestamp)和详细信息(details)等字段

    """

    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(20), nullable=False)  # 日志级别: info, warning, error
    action_type = db.Column(db.String(50), nullable=False)  # 操作类型
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=True
    )  # 用户ID，可以为空值，用来记录错误的用户登录日志
    timestamp = db.Column(
        db.DateTime, nullable=False, default=datetime.now(timezone.utc)
    )
    details = db.Column(db.Text, nullable=False)  # 详细信息
    user = db.relationship("User", back_populates="logs")  # 关联到 User 模型

    def __repr__(self):
        return f"<SystemLog {self.id} {self.level}>"

    def to_dict(self):
        return {
            "id": self.id,
            "level": self.level,
            "action_type": self.action_type,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
        }


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    projects = db.relationship("Project", backref="owner", lazy=True)
    assigned_tasks = db.relationship("Task", backref="assignee", lazy=True)
    logs = db.relationship("SystemLog", back_populates="user", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

    def to_dict(self):
        return {"id": self.id, "username": self.username, "is_admin": self.is_admin}


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="pending")
    tasks = db.relationship("Task", backref="project_tasks", lazy=True)

    def __repr__(self):
        return f"<Project {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "status": self.status,
        }


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    assignee_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    status = db.Column(db.String(20), default="pending")  # doing, done, pending
    priority = db.Column(db.String(10), default="medium")
    due_date = db.Column(db.DateTime)
    estimated_hours = db.Column(db.Float)  # 预估工时
    actual_hours = db.Column(db.Float)  # 实际工时
    dependencies = db.Column(db.String(255))  # 依赖任务ID列表，逗号分隔
    comments = db.relationship("TaskComment", backref="task", lazy=True)  # 任务评论

    def __repr__(self):
        return f"<Task {self.title}>"

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "assignee_id": self.assignee_id,
            "status": self.status,
            "priority": self.priority,
            "due_date": self.due_date.isoformat() if self.due_date else None,
        }


class TaskComment(db.Model):
    """任务评论模型"""

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)  # 评论内容(支持富文本)
    mentioned_users = db.Column(db.String(255))  # 被@的用户ID列表，逗号分隔
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<TaskComment {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "user_id": self.user_id,
            "content": self.content,
            "mentioned_users": (
                self.mentioned_users.split(",") if self.mentioned_users else []
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Dictionary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    items = db.relationship("DictionaryItem", backref="dictionary", lazy=True)

    def __repr__(self):
        return f"<Dictionary {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
        }


class DictionaryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dictionary_id = db.Column(
        db.Integer, db.ForeignKey("dictionary.id"), nullable=False
    )
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return f"<DictionaryItem {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "dictionary_id": self.dictionary_id,
            "name": self.name,
            "value": self.value,
            "description": self.description,
        }


class ProjectPerformance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    kpi = db.Column(db.String(100), nullable=False)
    budget = db.Column(db.Float, nullable=False)
    actual_cost = db.Column(db.Float)
    completion_rate = db.Column(db.Float, default=0)
    remark = db.Column(db.Text, default="")
    # Bug修复：将弃用的 datetime.utcnow 替换为 datetime.now(timezone.utc)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<ProjectPerformance {self.kpi}>"

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "kpi": self.kpi,
            "budget": self.budget,
            "actual_cost": self.actual_cost,
            "completion_rate": self.completion_rate,
            "remark": self.remark,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ProjectArchive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    archived_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    reason = db.Column(db.Text, default="")
    status = db.Column(db.String(20), default="archived")
    archived_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f"<ProjectArchive {self.project_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "archived_by": self.archived_by,
            "reason": self.reason,
            "status": self.status,
            "archived_at": self.archived_at.isoformat() if self.archived_at else None,
        }


class ProjectProgress(db.Model):
    """项目进度模型，用于记录项目各阶段的进度情况"""

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    milestone = db.Column(db.String(100), nullable=False)  # 里程碑名称
    planned_start = db.Column(db.DateTime, nullable=False)  # 计划开始时间
    planned_end = db.Column(db.DateTime, nullable=False)  # 计划结束时间
    actual_start = db.Column(db.DateTime)  # 实际开始时间
    actual_end = db.Column(db.DateTime)  # 实际结束时间
    completion_rate = db.Column(db.Float, default=0)  # 完成百分比(0-100)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<ProjectProgress {self.milestone}>"

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "milestone": self.milestone,
            "planned_start": (
                self.planned_start.isoformat() if self.planned_start else None
            ),
            "planned_end": self.planned_end.isoformat() if self.planned_end else None,
            "actual_start": (
                self.actual_start.isoformat() if self.actual_start else None
            ),
            "actual_end": self.actual_end.isoformat() if self.actual_end else None,
            "completion_rate": self.completion_rate,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ProjectRisk(db.Model):
    """项目风险模型，用于记录项目执行过程中的风险项"""

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    title = db.Column(db.String(100), nullable=False)  # 风险标题
    description = db.Column(db.Text)  # 风险详细描述
    probability = db.Column(db.String(20))  # 发生概率(高/中/低)
    impact = db.Column(db.String(20))  # 影响程度(高/中/低)
    status = db.Column(
        db.String(20), default="open"
    )  # 状态(open/in_progress/resolved/closed)
    solution = db.Column(db.Text)  # 解决方案
    created_by = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )  # 创建人
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # 创建时间
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )  # 更新时间


class ChangeRecord(db.Model):
    """项目变更记录模型"""

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    change_type = db.Column(db.String(50), nullable=False)  # 变更类型
    description = db.Column(db.Text, nullable=False)  # 变更描述
    before_data = db.Column(db.JSON)  # 变更前数据
    after_data = db.Column(db.JSON)  # 变更后数据
    created_by = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )  # 创建人
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # 创建时间

    def __repr__(self):
        return f"<ChangeRecord {self.change_type}>"

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "change_type": self.change_type,
            "description": self.description,
            "before_data": self.before_data,
            "after_data": self.after_data,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AuditLog(db.Model):
    """系统审计日志模型"""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )  # 操作用户
    project_id = db.Column(
        db.Integer, db.ForeignKey("project.id"), nullable=True
    )  # 关联项目ID
    action_type = db.Column(db.String(50), nullable=False)  # 操作类型
    resource_type = db.Column(db.String(50))  # 资源类型
    resource_id = db.Column(db.Integer)  # 资源ID
    details = db.Column(db.JSON)  # 操作详情
    ip_address = db.Column(db.String(50))  # IP地址
    user_agent = db.Column(db.String(200))  # 用户代理
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # 创建时间

    def __repr__(self):
        return f"<AuditLog {self.action_type}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action_type": self.action_type,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ProjectMilestone(db.Model):
    """项目里程碑模型，用于跟踪项目关键里程碑"""

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # 里程碑名称
    description = db.Column(db.Text)  # 里程碑描述
    planned_date = db.Column(db.DateTime, nullable=False)  # 计划完成日期
    actual_date = db.Column(db.DateTime)  # 实际完成日期
    status = db.Column(
        db.String(20), default="pending"
    )  # 状态(pending/completed/delayed)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # 创建时间
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )  # 更新时间

    def __repr__(self):
        return f"<ProjectMilestone {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "description": self.description,
            "planned_date": (
                self.planned_date.isoformat() if self.planned_date else None
            ),
            "actual_date": self.actual_date.isoformat() if self.actual_date else None,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class SystemConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.JSON, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<SystemConfig {self.key}>"

    def to_dict(self):
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ProjectMember(db.Model):
    """项目成员模型，用于管理项目成员关系"""

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.Integer, db.ForeignKey("project.id"), nullable=False
    )  # 关联项目ID
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )  # 关联用户ID
    role = db.Column(db.String(20), nullable=False)  # 成员角色(admin/member/guest)
    joined_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # 加入时间
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )  # 更新时间

    def __repr__(self):
        return f"<ProjectMember {self.user_id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "user_id": self.user_id,
            "role": self.role,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ProjectDocument(db.Model):
    """项目文档模型，用于管理项目相关文档"""

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.Integer, db.ForeignKey("project.id"), nullable=False
    )  # 关联项目ID
    name = db.Column(db.String(100), nullable=False)  # 文档名称
    file_path = db.Column(db.String(255), nullable=False)  # 文件存储路径
    file_size = db.Column(db.Integer)  # 文件大小(字节)
    file_type = db.Column(db.String(50))  # 文件类型
    description = db.Column(db.Text)  # 文档描述
    uploaded_by = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )  # 上传人
    uploaded_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # 上传时间
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )  # 更新时间

    def __repr__(self):
        return f"<ProjectDocument {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "description": self.description,
            "uploaded_by": self.uploaded_by,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
