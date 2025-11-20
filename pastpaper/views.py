from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import Subject, Unit, Question, PastPaper, UserTag, HistoryRecord, Setting


@login_required
def home_view(request, subject_code='cs'):
    """主页视图"""
    # 获取学科信息
    try:
        subject = Subject.objects.get(code=subject_code)
    except Subject.DoesNotExist:
        subject = Subject.objects.get(code='cs')  # 默认使用cs
    
    # 获取所有学科列表
    all_subjects = Subject.objects.all().order_by('id')
    
    return render(request, 'pastpaper/home.html', {
        'current_subject': subject,
        'all_subjects': all_subjects
    })


@login_required
def theme_settings_view(request):
    """主题设置页面"""
    # 获取默认学科
    try:
        subject = Subject.objects.first()
    except Subject.DoesNotExist:
        subject = None

    all_subjects = Subject.objects.all().order_by('id')

    return render(request, 'pastpaper/theme_settings.html', {
        'current_subject': subject,
        'all_subjects': all_subjects
    })


@login_required
def feedback_view(request):
    """反馈页面视图"""
    # 获取默认学科
    try:
        subject = Subject.objects.get(code='cs')
    except Subject.DoesNotExist:
        subject = None
    
    # 获取所有学科列表
    all_subjects = Subject.objects.all().order_by('id')
    
    return render(request, 'pastpaper/feedback.html', {
        'current_subject': subject,
        'all_subjects': all_subjects
    })


@login_required
def mydetails_view(request):
    """个人详情页面视图"""
    # 获取默认学科
    try:
        subject = Subject.objects.get(code='cs')
    except Subject.DoesNotExist:
        subject = None
    
    # 获取所有学科列表
    all_subjects = Subject.objects.all().order_by('id')
    
    return render(request, 'pastpaper/mydetails.html', {
        'user': request.user,
        'current_subject': subject,
        'all_subjects': all_subjects
    })


# API Endpoints

@login_required
@require_POST
def get_units(request):
    """获取指定学科的所有单元列表"""
    subject_code = request.POST.get('subject', 'cs')
    
    try:
        subject = Subject.objects.get(code=subject_code)
        units = Unit.objects.filter(subject=subject).values('id', 'unit_num', 'name')
        return JsonResponse(list(units), safe=False)
    except Subject.DoesNotExist:
        return JsonResponse([], safe=False)


@login_required
@require_POST
def get_list(request):
    """获取指定单元的题目列表"""
    unit_num = request.POST.get('unit')
    subject_code = request.POST.get('subject', 'cs')
    
    if not unit_num:
        return JsonResponse({'error': 'Unit number is required'}, status=400)
    
    try:
        subject = Subject.objects.get(code=subject_code)
        unit = Unit.objects.get(unit_num=unit_num, subject=subject)
        questions = Question.objects.filter(unit=unit).order_by('-created_at')
        
        result = []
        for q in questions:
            # 获取用户标签
            try:
                tag = UserTag.objects.get(user=request.user, question=q)
                checked = tag.kill
                save = tag.saved
            except UserTag.DoesNotExist:
                checked = False
                save = False
            
            result.append({
                'id': q.id,
                'code': q.code,
                'qpage': q.qpage,
                'apage': q.apage,
                'spage': q.spage,
                'checked': checked,
                'save': save
            })
        
        return JsonResponse(result, safe=False)
    except (Subject.DoesNotExist, Unit.DoesNotExist):
        return JsonResponse([], safe=False)


@login_required
@require_POST
def get_past_papers(request):
    """获取指定学科的所有历年试卷"""
    subject_code = request.POST.get('subject', 'cs')
    
    try:
        subject = Subject.objects.get(code=subject_code)
        past_papers = PastPaper.objects.filter(subject=subject).order_by('-year', 'session', 'paper_num')
        
        result = []
        for pp in past_papers:
            result.append({
                'code': pp.code,
                'year': pp.year,
                'session': pp.session,
                'paper_num': pp.paper_num
            })
        
        return JsonResponse(result, safe=False)
    except Subject.DoesNotExist:
        return JsonResponse([], safe=False)


@login_required
@require_POST
def get_question_info(request):
    """获取题目详细信息（包括页码）"""
    code = request.POST.get('code')
    
    if not code:
        return JsonResponse({'error': 'Code is required'}, status=400)
    
    try:
        question = Question.objects.get(code=code)
        return JsonResponse({
            'id': question.id,
            'code': question.code,
            'qpage': question.qpage,
            'apage': question.apage,
            'spage': question.spage
        })
    except Question.DoesNotExist:
        return JsonResponse({'error': 'Question not found'}, status=404)


@login_required
@require_POST
def get_history(request):
    """获取用户浏览历史"""
    history = HistoryRecord.objects.filter(user=request.user).order_by('-visited_at')[:20]
    
    result = []
    for h in history:
        result.append({
            'code': h.question.code,
            'visited_at': h.visited_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return JsonResponse(result, safe=False)


@login_required
@require_POST
def update_user_tags(request):
    """更新用户题目标签"""
    question_id = request.POST.get('id')
    kill_value = request.POST.get('kill', '0')
    save_value = request.POST.get('save', '0')
    
    if not question_id:
        return JsonResponse({'success': False, 'error': 'Question ID is required'}, status=400)
    
    try:
        question = Question.objects.get(id=question_id)
        tag, created = UserTag.objects.get_or_create(
            user=request.user,
            question=question
        )
        
        # 根据传入的值更新标签
        if kill_value == '1':
            tag.kill = True
            tag.saved = False
        elif save_value == '1':
            tag.saved = True
            tag.kill = False
        
        tag.save()
        
        return JsonResponse({'success': True})
    except Question.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Question not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def update_history(request):
    """更新用户浏览历史"""
    code = request.POST.get('code')
    
    if not code:
        return JsonResponse({'success': False, 'error': 'Code is required'}, status=400)
    
    try:
        question = Question.objects.get(code=code)
        
        # 检查是否已存在最近的历史记录（避免重复）
        recent_history = HistoryRecord.objects.filter(
            user=request.user,
            question=question
        ).order_by('-visited_at').first()
        
        # 如果不存在或者超过1分钟，则创建新记录
        if not recent_history or (recent_history.visited_at - recent_history.visited_at).seconds > 60:
            HistoryRecord.objects.create(
                user=request.user,
                question=question
            )
        
        return JsonResponse({'success': True})
    except Question.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Question not found'}, status=404)

