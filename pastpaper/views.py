from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
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


staff_required = user_passes_test(lambda u: u.is_staff)


@login_required
@staff_required
def create_question_view(request):
    """教师端创建题目页面"""
    subjects = Subject.objects.all().order_by('id')
    current_subject = subjects.first() if subjects else None
    return render(
        request,
        'pastpaper/create_question.html',
        {
            'current_subject': current_subject,
            'all_subjects': subjects,
        },
    )


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
        past_papers = list(PastPaper.objects.filter(subject=subject).order_by('-year', 'session', 'paper_num'))
        paper_ids = [pp.id for pp in past_papers]
        tags = {}
        if paper_ids:
            tags = {
                tag.past_paper_id: tag
                for tag in PastPaperTag.objects.filter(user=request.user, past_paper_id__in=paper_ids)
            }
        
        result = []
        for pp in past_papers:
            tag = tags.get(pp.id)
            result.append({
                'code': pp.code,
                'year': pp.year,
                'session': pp.session,
                'paper_num': pp.paper_num,
                'checked': tag.kill if tag else False,
                'save': tag.saved if tag else False,
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
@staff_required
@require_POST
def list_papers_by_subject(request):
    """根据学科列出历年试卷（教师创建页使用）"""
    subject_code = request.POST.get('subject')
    if not subject_code:
        return JsonResponse({'error': 'Subject code is required'}, status=400)

    try:
        subject = Subject.objects.get(code=subject_code)
    except Subject.DoesNotExist:
        return JsonResponse({'error': 'Subject not found'}, status=404)

    papers = PastPaper.objects.filter(subject=subject).order_by('-year', 'session', 'paper_num')
    data = [
        {
            'code': pp.code,
            'year': pp.year,
            'session': pp.session,
            'paper_num': pp.paper_num,
            'year_session': f"{pp.session}{str(pp.year)[-2:]}",
        }
        for pp in papers
    ]
    return JsonResponse(data, safe=False)


@login_required
@staff_required
@require_POST
def get_questions_by_paper(request):
    """根据试卷编号获取题目列表（按编码前缀匹配）"""
    subject_code = request.POST.get('subject')
    year_session = request.POST.get('year_session')
    paper_num = request.POST.get('paper')

    if not subject_code or not year_session or not paper_num:
        return JsonResponse({'error': 'subject, year_session and paper are required'}, status=400)

    try:
        subject = Subject.objects.get(code=subject_code)
    except Subject.DoesNotExist:
        return JsonResponse({'error': 'Subject not found'}, status=404)

    prefix = f"{subject.exam_code}_{year_session}_{paper_num}"
    questions = (
        Question.objects.filter(subject=subject, code__startswith=f"{prefix}-")
        .select_related('unit')
        .order_by('code')
    )
    data = [
        {
            'id': q.id,
            'code': q.code,
            'unit_id': q.unit_id,
            'unit_label': f"Unit {q.unit.unit_num}: {q.unit.name}" if q.unit else '',
            'qpage': q.qpage,
            'apage': q.apage,
            'spage': q.spage,
        }
        for q in questions
    ]
    return JsonResponse({'questions': data, 'prefix': prefix})


@login_required
@staff_required
@require_POST
def save_question(request):
    """保存或更新题目信息（仅限教师）"""
    subject_code = request.POST.get('subject')
    code = request.POST.get('code')
    unit_id = request.POST.get('unit_id')
    qpage = request.POST.get('qpage')
    apage = request.POST.get('apage')
    spage = request.POST.get('spage')
    question_id = request.POST.get('id')

    if not subject_code or not code:
        return JsonResponse({'error': 'Subject and code are required'}, status=400)

    try:
        subject = Subject.objects.get(code=subject_code)
    except Subject.DoesNotExist:
        return JsonResponse({'error': 'Subject not found'}, status=404)

    if subject.exam_code and not code.startswith(str(subject.exam_code)):
        return JsonResponse({'error': f'题目代码必须以学科考试代码 {subject.exam_code} 开头'}, status=400)

    def parse_int(val, default):
        try:
            return int(val)
        except (TypeError, ValueError):
            return default

    qpage_val = parse_int(qpage, 1)
    apage_val = parse_int(apage, 1)
    spage_val = parse_int(spage, 1)

    unit = None
    if unit_id:
        try:
            unit = Unit.objects.get(id=unit_id, subject=subject)
        except Unit.DoesNotExist:
            return JsonResponse({'error': 'Unit not found for this subject'}, status=404)

    created = False
    try:
        if question_id:
            question = Question.objects.get(id=question_id)
            if question.subject_id != subject.id:
                return JsonResponse({'error': '不允许更改题目所属学科'}, status=400)
            question.code = code
            question.unit = unit
            question.qpage = qpage_val
            question.apage = apage_val
            question.spage = spage_val
            question.save()
        else:
            # 避免用相同code覆盖其他学科
            if Question.objects.filter(code=code).exclude(subject=subject).exists():
                return JsonResponse({'error': '存在同名题目且属于其他学科，无法覆盖'}, status=400)
            question, created = Question.objects.update_or_create(
                code=code,
                defaults={
                    'subject': subject,
                    'unit': unit,
                    'qpage': qpage_val,
                    'apage': apage_val,
                    'spage': spage_val,
                },
            )
    except Exception as exc:  # 防御性兜底，避免500
        return JsonResponse({'error': str(exc)}, status=500)

    return JsonResponse({
        'success': True,
        'id': question.id,
        'created': created,
        'code': question.code,
    })


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
    """更新用户题目或Past Paper标签"""
    item_type = request.POST.get('item_type', 'question')
    question_id = request.POST.get('id')
    paper_code = request.POST.get('code')
    kill_value = request.POST.get('kill', '0')
    save_value = request.POST.get('save', '0')

    def apply_tag_state(tag_obj):
        if kill_value == '1':
            tag_obj.kill = True
            tag_obj.saved = False
        elif save_value == '1':
            tag_obj.saved = True
            tag_obj.kill = False
        tag_obj.save()
        return {'kill': tag_obj.kill, 'saved': tag_obj.saved}

    if item_type == 'past_paper':
        if not paper_code:
            return JsonResponse({'success': False, 'error': 'Past paper code is required'}, status=400)
        try:
            past_paper = PastPaper.objects.get(code=paper_code)
            tag, _ = PastPaperTag.objects.get_or_create(
                user=request.user,
                past_paper=past_paper
            )
            state = apply_tag_state(tag)
            return JsonResponse({'success': True, 'item_type': 'past_paper', 'state': state})
        except PastPaper.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Past paper not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    if not question_id:
        return JsonResponse({'success': False, 'error': 'Question ID is required'}, status=400)

    try:
        question = Question.objects.get(id=question_id)
        tag, _ = UserTag.objects.get_or_create(
            user=request.user,
            question=question
        )
        state = apply_tag_state(tag)
        return JsonResponse({'success': True, 'item_type': 'question', 'state': state})
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

