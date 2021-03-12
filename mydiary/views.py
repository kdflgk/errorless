from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect,reverse


from common.forms import UserForm
from .models import Diary
from .forms import DiaryForm
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib import messages

# 프로필 ##############################################
from django.contrib.auth.models import User
from django.views.generic.detail import DetailView
from django.views import View
from common.forms import UserForm, ProfileForm
######################################################
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
import itertools
import matplotlib.pyplot as plt
import io
import urllib, base64
######################################################


class ProfileView(DetailView):
    context_object_name = 'profile_user' # model로 지정해준 User모델에 대한 객체와 로그인한 사용자랑 명칭이 겹쳐버리기 때문에 이를 지정해줌.
    model = User
    template_name = 'mydiary/testmypage.html'


class ProfileUpdateView(View): # 간단한 View클래스를 상속 받았으므로 get함수와 post함수를 각각 만들어줘야한다.
    # 프로필 편집에서 보여주기위한 get 메소드
    def get(self, request):
        user = get_object_or_404(User, pk=request.user.pk)  # 로그인중인 사용자 객체를 얻어옴
        user_form = UserForm(initial={
            'username': user.username,
            'email': user.email,
        })
        if hasattr(user, 'profile'):  # user가 profile을 가지고 있으면 True, 없으면 False (회원가입을 한다고 profile을 가지고 있진 않으므로)
            profile = user.profile
            profile_form = ProfileForm(initial={
                'nickname': profile.nickname,
                'profile_photo': profile.profile_photo,
            })
        else:
            profile_form = ProfileForm()

        return render(request, 'mydiary/updateprofile.html', {"user_form": user_form, "profile_form": profile_form})
        # return render(request, 'mydiary/testmypage.html', {"user_form": user_form, "profile_form": profile_form})

    # 프로필 편집에서 실제 수정(저장) 버튼을 눌렀을 때 넘겨받은 데이터를 저장하는 post 메소드
    def post(self, request):
        u = User.objects.get(id=request.user.pk)  # 로그인중인 사용자 객체를 얻어옴
        user_form = UserForm(request.POST, instance=u)  # 기존의 것의 업데이트하는 것 이므로 기존의 인스턴스를 넘겨줘야한다. 기존의 것을 가져와 수정하는 것

        # User 폼
        if user_form.is_valid():
            user_form.save()

        if hasattr(u, 'profile'):
            profile = u.profile
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile)  # 기존의 것 가져와 수정하는 것
        else:
            profile_form = ProfileForm(request.POST, request.FILES)  # 새로 만드는 것

        # Profile 폼
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)  # 기존의 것을 가져와 수정하는 경우가 아닌 새로 만든 경우 user를 지정해줘야 하므로
            profile.user = u
            profile.save()

        return redirect('mydiary:profile', pk=request.user.pk)  # 수정된 화면 보여주기

# 딥러닝 ##############################################
okt = Okt()
stopwords = []
f = open('stopwords.csv')
lines = f.readlines()
for line in lines:
    line = line.strip()
    stopwords.append(line)
f.close()


def sentence_preprocessing(sentence):
    new_sentence = spacing(sentence)
    new_sentence = spell_checker.check(new_sentence).checked
    new_sentence = emoticon_normalize(new_sentence, num_repeats=2)
    new_sentence = okt.morphs(new_sentence, norm=True, stem=True)
    new_sentence = [w for w in new_sentence if not w in stopwords]
    return new_sentence


def mood(sentence):
    max_len = 30
    model = load_model('best_model.h5')

    tokenizer = Tokenizer()

    with open('wordIndex.json') as json_file:
        word_index = json.load(json_file)
        tokenizer.word_index = word_index

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
    if score.argmax() == 4:
        result = '{:.2f}% 확률로 {} 감정입니다.\n'.format(np.max(score) * 100, '놀라움, 충격')
        print(result)
    if score.argmax() == 5:
        result = '{:.2f}% 확률로 {} 감정입니다.\n'.format(np.max(score) * 100, '지루, 따분')
        print(result)

    data = score.tolist()
    data = list(itertools.chain.from_iterable(data))

    labels = ['happy', 'angry', 'sad', 'fear', 'surprise', 'boring']
    colors = ['#ff9999', '#ffc000', '#8fd9b6', '#d395d0', '#00ccff', '#00ff22']
    wedgeprops = {'width': 0.7, 'edgecolor': 'w', 'linewidth': 5}
    explode = [0.05, 0.05, 0.05, 0.05, 0.05, 0.05]

    plt.pie(data, labels=labels, autopct='%.1f%%', startangle=260, counterclock=False, colors=colors,
            wedgeprops=wedgeprops, explode=explode)
    # plt.show()
    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    plt.close(fig)
    return result, uri
######################################################


def startup(request):
    return render(request, 'mydiary/testmain.html')


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
    # return render(request, 'mydiary/mainscreen.html', context)
    return render(request, 'mydiary/testdiarylist.html', context)


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
    # return render(request, 'mydiary/writediary.html', context)
    return render(request, 'mydiary/testwrite.html', context)


@login_required(login_url='common:login')
def detail(request, question_id):
    """
    내용 출력
    """
    question = Diary.objects.get(id=question_id)
    question.author = request.user
    ###################
    # sentiment_predict_pie_graph(question.content)
    question.moodres, uri = mood(question.content)
    ###################
    print()
    context = {'question': question, 'data': uri}
    # return render(request, 'mydiary/detail.html', context)
    return render(request, 'mydiary/testdetail.html', context)


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
