from django.db import models
from django.contrib.auth.models import User


class Subject(models.Model):
    """学科模型"""
    code = models.CharField(max_length=50, unique=True, verbose_name="学科代码")
    name = models.CharField(max_length=255, verbose_name="学科名称")
    exam_code = models.CharField(max_length=10, verbose_name="考试代码")  # 如9618, 0984
    syllabus_url = models.URLField(blank=True, verbose_name="大纲URL")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']
        verbose_name = "学科"
        verbose_name_plural = "学科"

    def __str__(self):
        return f"{self.name} ({self.exam_code})"


class Unit(models.Model):
    """课程单元模型"""
    unit_num = models.IntegerField(verbose_name="单元编号")
    name = models.CharField(max_length=255, verbose_name="单元名称")
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='units',
        verbose_name="所属学科"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['subject', 'unit_num']
        unique_together = ['subject', 'unit_num']
        verbose_name = "单元"
        verbose_name_plural = "单元"

    def __str__(self):
        return f"Unit {self.unit_num}: {self.name} ({self.subject.code})"


class PastPaper(models.Model):
    """历年试卷模型（用于Past Papers功能）"""
    code = models.CharField(max_length=50, unique=True, verbose_name="试卷代码")  # 如9618_s23_11
    year = models.IntegerField(verbose_name="年份")
    session = models.CharField(max_length=10, verbose_name="考试季")  # s=summer, w=winter
    paper_num = models.CharField(max_length=10, verbose_name="试卷编号")  # 11, 12, 21等
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='past_papers',
        verbose_name="所属学科"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', 'session', 'paper_num']
        verbose_name = "历年试卷"
        verbose_name_plural = "历年试卷"

    def __str__(self):
        return self.code

    @property
    def qp_filename(self):
        """生成Question Paper文件名"""
        return f"{self.code}qp_{self.paper_num}.pdf"

    @property
    def ms_filename(self):
        """生成Mark Scheme文件名"""
        return f"{self.code}ms_{self.paper_num}.pdf"


class PastPaperTag(models.Model):
    """用户对历年试卷的标签"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pastpaper_tags',
        verbose_name="用户"
    )
    past_paper = models.ForeignKey(
        PastPaper,
        on_delete=models.CASCADE,
        related_name='user_tags',
        verbose_name="历年试卷"
    )
    kill = models.BooleanField(default=False, verbose_name="已完成")
    saved = models.BooleanField(default=False, verbose_name="已保存", db_column='pp_save')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'past_paper']
        verbose_name = "历年试卷标签"
        verbose_name_plural = "历年试卷标签"

    def __str__(self):
        return f"{self.user.username} - {self.past_paper.code}"


class Question(models.Model):
    """题目模型"""
    code = models.CharField(max_length=50, unique=True, verbose_name="题目代码")
    unit = models.ForeignKey(
        Unit, 
        on_delete=models.CASCADE, 
        related_name='questions',
        verbose_name="所属单元",
        null=True,
        blank=True
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="所属学科"
    )
    qpage = models.IntegerField(default=1, verbose_name="试卷页码")
    apage = models.IntegerField(default=1, verbose_name="答案页码")
    spage = models.IntegerField(default=1, verbose_name="大纲页码")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "题目"
        verbose_name_plural = "题目"

    def __str__(self):
        return self.code

    @property
    def qp_filename(self):
        """生成Question Paper文件名"""
        parts = self.code.split('-')[0]
        base = parts[:9]
        paper = parts[9:11]
        return f"{base}qp_{paper}.pdf"

    @property
    def ms_filename(self):
        """生成Mark Scheme文件名"""
        parts = self.code.split('-')[0]
        base = parts[:9]
        paper = parts[9:11]
        return f"{base}ms_{paper}.pdf"


class UserTag(models.Model):
    """用户题目标签模型"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='user_tags',
        verbose_name="用户"
    )
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE, 
        related_name='user_tags',
        verbose_name="题目"
    )
    kill = models.BooleanField(default=False, verbose_name="已完成")
    saved = models.BooleanField(default=False, verbose_name="已保存", db_column='save')  # db_column保持数据库字段名不变
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'question']
        verbose_name = "用户标签"
        verbose_name_plural = "用户标签"

    def __str__(self):
        return f"{self.user.username} - {self.question.code}"


class HistoryRecord(models.Model):
    """用户浏览历史模型"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='history_records',
        verbose_name="用户"
    )
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE, 
        related_name='history_records',
        verbose_name="题目"
    )
    visited_at = models.DateTimeField(auto_now_add=True, verbose_name="访问时间")

    class Meta:
        ordering = ['-visited_at']
        verbose_name = "浏览历史"
        verbose_name_plural = "浏览历史"

    def __str__(self):
        return f"{self.user.username} - {self.question.code}"


class Setting(models.Model):
    """系统设置模型"""
    key = models.CharField(max_length=255, unique=True, verbose_name="键")
    value = models.TextField(verbose_name="值")
    description = models.CharField(max_length=500, blank=True, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "系统设置"
        verbose_name_plural = "系统设置"

    def __str__(self):
        return self.key
