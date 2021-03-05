from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect,reverse


from common.forms import UserForm
from .models import Diary
from .forms import DiaryForm
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib import messages

# # 달력테스트
# import datetime
# from .models import Event
# import calendar
# from .calendar import Calendar
# from django.utils.safestring import mark_safe
# from .forms import EventForm

# 딥러닝 ##############################################
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from hanspell import spell_checker
from konlpy.tag import Okt
from pykospacing import spacing
from soynlp.normalizer import *
import json
######################################################


# @login_required(login_url='common:login')
# def startup(request):
#     return render(request, 'mydiary/startupscreen.html')


# 딥러닝 ##############################################
okt = Okt()
stopwords = []


def sentence_preprocessing(sentence):
    new_sentence = spacing(sentence)
    new_sentence = spell_checker.check(new_sentence).checked
    new_sentence = emoticon_normalize(new_sentence, num_repeats=2)
    new_sentence = okt.morphs(new_sentence, norm=True, stem=True)
    new_sentence = [w for w in new_sentence if not w in stopwords]
    return new_sentence


def mood(sentence):
    max_len = 30
    model = load_model('best_model11.h5')
    tokenizer = Tokenizer()

    with open('wordIndex.json') as json_file:
        word_index = json.load(json_file)
        tokenizer.word_index = word_index

    # sentence = '기분이 너무 좋다'
    # print(sentence)
    new_sentence = sentence_preprocessing(sentence)
    print(new_sentence)
    encoded = tokenizer.texts_to_sequences([new_sentence])  # 정수 인코딩
    print(encoded)
    pad_new = pad_sequences(encoded, maxlen=max_len)  # 패딩
    print(pad_new)
    score = model.predict(pad_new)
    print(score)
    if score.argmax() == 0:
        result = '{:.2f}% 확률로 {} 감정입니다.\n'.format(np.max(score) * 100, '행복, 즐거움')
        print(result)
    if score.argmax() == 1:
        result = '{:.2f}% 확률로 {} 감정입니다.\n'.format(np.max(score) * 100, '분노, 짜증')
        print(result)
    if score.argmax() == 2:
        result = '{:.2f}% 확률로 {} 감정입니다.\n'.format(np.max(score) * 100, '슬픔, 우울')
        print(result)
    if score.argmax() == 3:
        result = '{:.2f}% 확률로 {} 감정입니다.\n'.format(np.max(score) * 100, '두려움, 불안')
        print(result)
    return result
######################################################

@login_required(login_url='common:login')
def main(request):
    """
    목록 출력
    """
    page = request.GET.get('page', '1')  # 페이지

    # question_list = Diary.objects.order_by('-create_date')
    # 현재 로그인한 사용자의 글만 출력하고 날짜순으로 정렬
    question_list = Diary.objects.order_by('-create_date').filter(author=request.user)

    paginator = Paginator(question_list, 10)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    context = {'question_list': page_obj}
    return render(request, 'mydiary/mainscreen.html', context)
    # return render(request, 'mydiary/testmain.html', context)

@login_required(login_url='common:login')
def write(request):
    """
    일기작성
    """
    if request.method == 'POST':
        form = DiaryForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.create_date = timezone.now()
            question.author=request.user
            question.save()
            return redirect('mydiary:main')
    else:
        form = DiaryForm()
    context = {'form': form}
    return render(request, 'mydiary/writediary.html', context)


@login_required(login_url='common:login')
def detail(request, question_id):
    """
    내용 출력
    """
    question = Diary.objects.get(id=question_id)
    question.author = request.user
    ###################
    question.moodres = mood(question.content)
    ###################
    # context = {'question': question}
    context = {'question': question}
    return render(request, 'mydiary/detail.html', context)


@login_required(login_url='common:login')
def diary_delete(request, question_id):
    """
    삭제
    """
    question = get_object_or_404(Diary, pk=question_id)
    if request.user != question.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('mydiary:detail', question_id=question.id)
    question.delete()
    return redirect('mydiary:main')


# 달력테스트 ################################################################################################################################
# def calendar_view(request):
#     today = get_date(request.GET.get('month'))
#
#     prev_month_var = prev_month(today)
#     next_month_var = next_month(today)
#
#     cal = Calendar(today.year, today.month)
#     html_cal = cal.formatmonth(withyear=True)
#     result_cal = mark_safe(html_cal)
#
#     context = {'calendar': result_cal, 'prev_month': prev_month_var, 'next_month': next_month_var}
#
#     return render(request, 'mydiary/events.html', context)


# # 현재 달력을 보고 있는 시점의 시간을 반환
# def get_date(req_day):
#     if req_day:
#         year, month = (int(x) for x in req_day.split('-'))
#         return datetime.date(year, month, day=1)
#     return datetime.datetime.today()
#
#
# # 현재 달력의 이전 달 URL 반환
# def prev_month(day):
#     first = day.replace(day=1)
#     prev_month = first - datetime.timedelta(days=1)
#     month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
#     return month
#
#
# # 현재 달력의 다음 달 URL 반환
# def next_month(day):
#     days_in_month = calendar.monthrange(day.year, day.month)[1]
#     last = day.replace(day=days_in_month)
#     next_month = last + datetime.timedelta(days=1)
#     month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
#     return month
#
#
# # 새로운 Event의 등록 혹은 수정
# def event(request, event_id=None):
#     if event_id:
#         instance = get_object_or_404(Event, pk=event_id)
#     else:
#         instance = Event()
#
#     form = EventForm(request.POST or None, instance=instance)
#     if request.POST and form.is_valid():
#         form.save()
#         return redirect('calendar')
#     return render(request, 'mydiary/imput.html', {'form': form})
