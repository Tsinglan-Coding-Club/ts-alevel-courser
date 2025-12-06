from django import forms
from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Subject,
    Unit,
    Question,
    PastPaper,
    PastPaperTag,
    UserTag,
    HistoryRecord,
    Setting,
)


class SubjectAdminForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = '__all__'

    def clean_syllabus_url(self):
        value = (self.cleaned_data.get('syllabus_url') or '').strip()
        if not value:
            return ''
        normalized = value.replace('\\', '/')
        lower_value = normalized.lower()
        if lower_value.startswith('http://') or lower_value.startswith('https://'):
            raise forms.ValidationError('请只填写media目录下的文件名，不要包含http/https。')

        prefixes = {
            settings.MEDIA_URL or '',
            (settings.MEDIA_URL or '').lstrip('/'),
            'media/',
            '/media/',
        }
        for prefix in prefixes:
            if prefix and normalized.startswith(prefix):
                normalized = normalized[len(prefix):]
        return normalized.lstrip('/')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    form = SubjectAdminForm
    list_display = ['code', 'name', 'exam_code', 'get_syllabus_file', 'created_at']
    search_fields = ['code', 'name', 'exam_code']
    list_filter = ['created_at']

    @admin.display(description="大纲文件")
    def get_syllabus_file(self, obj):
        if not obj.syllabus_filename:
            return "-"
        return format_html('<a href="{}" target="_blank">{}</a>', obj.syllabus_media_url, obj.syllabus_filename)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['unit_num', 'name', 'subject', 'syllabus_page', 'created_at']
    list_filter = ['subject', 'created_at']
    search_fields = ['name']
    ordering = ['subject', 'unit_num']
    fields = ['subject', 'unit_num', 'name', 'syllabus_page']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['code', 'subject', 'unit', 'qpage', 'apage', 'created_at']
    list_filter = ['subject', 'unit', 'created_at']
    search_fields = ['code']
    ordering = ['-created_at']
    
    # 设置字段顺序，确保先选择学科再选择单元
    fields = ['code', 'subject', 'unit', 'qpage', 'apage']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """根据已选学科过滤单元选项"""
        if db_field.name == "unit":
            # 如果是编辑现有题目，根据题目的学科过滤单元
            if request.resolver_match.kwargs.get('object_id'):
                try:
                    question = Question.objects.get(pk=request.resolver_match.kwargs['object_id'])
                    kwargs["queryset"] = Unit.objects.filter(subject=question.subject)
                except Question.DoesNotExist:
                    kwargs["queryset"] = Unit.objects.all()
            # 如果是新增题目，显示所有单元（单元名称已包含学科代码）
            else:
                kwargs["queryset"] = Unit.objects.all().select_related('subject')
                kwargs["help_text"] = "请选择与所属学科匹配的单元（括号中为学科代码）"
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        """保存时验证单元是否属于所选学科"""
        if obj.unit and obj.subject and obj.unit.subject != obj.subject:
            from django.contrib import messages
            messages.error(request, f"错误：选择的单元不属于所选学科！请选择 {obj.subject.code} 学科的单元。")
            return
        super().save_model(request, obj, form, change)


@admin.register(PastPaper)
class PastPaperAdmin(admin.ModelAdmin):
    list_display = ['code', 'year', 'session', 'paper_num', 'subject', 'created_at']
    list_filter = ['subject', 'year', 'session', 'created_at']
    search_fields = ['code']
    ordering = ['-year', 'session', 'paper_num']
    
    # 设置字段顺序，确保学科字段在前
    fields = ['code', 'subject', 'year', 'session', 'paper_num']


@admin.register(UserTag)
class UserTagAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'kill', 'saved', 'created_at']
    list_filter = ['kill', 'saved', 'created_at']
    search_fields = ['user__username', 'question__code']


@admin.register(PastPaperTag)
class PastPaperTagAdmin(admin.ModelAdmin):
    list_display = ['user', 'past_paper', 'kill', 'saved', 'created_at']
    list_filter = ['kill', 'saved', 'created_at']
    search_fields = ['user__username', 'past_paper__code']


@admin.register(HistoryRecord)
class HistoryRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'visited_at']
    list_filter = ['visited_at']
    search_fields = ['user__username', 'question__code']
    ordering = ['-visited_at']


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'description', 'updated_at']
    search_fields = ['key', 'description']
