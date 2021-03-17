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

# 딥러닝 ##############################################
import numpy as np
import pandas as pd
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
from pyecharts import Pie
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
######################################################


class ProfileView(DetailView):
    context_object_name = 'profile_user' # model로 지정해준 User모델에 대한 객체와 로그인한 사용자랑 명칭이 겹쳐버리기 때문에 이를 지정해줌.
    model = User
    # template_name = 'mydiary/testmypage.html'
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

lyric = pd.read_csv('lyric_label_final.csv')

lines = f.readlines()
for line in lines:
    line = line.strip()
    stopwords.append(line)
f.close()
max_len = 30
model = load_model('best_model.h5')
tokenizer = Tokenizer()

with open('wordIndex.json') as json_file:
    word_index = json.load(json_file)
    tokenizer.word_index = word_index

REMOTE_HOST = "https://pyecharts.github.io/assets/js"

def sentence_preprocessing(sentence):
    new_sentence = spacing(sentence)
    new_sentence = spell_checker.check(new_sentence).checked
    new_sentence = emoticon_normalize(new_sentence, num_repeats=2)
    new_sentence = okt.morphs(new_sentence, norm=True, stem=True)
    new_sentence = [w for w in new_sentence if not w in stopwords]
    return new_sentence


def prepro(sentence):
    new_sentence = sentence_preprocessing(sentence)
    print(new_sentence)
    encoded = tokenizer.texts_to_sequences([new_sentence])  # 정수 인코딩
    print(encoded)
    pad_new = pad_sequences(encoded, maxlen=max_len)  # 패딩
    print(pad_new)
    score = model.predict(pad_new)
    print(score)
    return score


def mood(sentence):
    score = prepro(sentence)
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
    v2 = list(itertools.chain.from_iterable(data))
    attr = ['happy', 'angry', 'sad', 'fear', 'surprise', 'boring']
    pie = Pie("", title_pos="center", width=600)
    # pie.add("A", attr, v1, center=[25, 50], is_random=True, radius=[30, 75], rosetype='radius')
    pie.add("", attr, v2, center=[45, 50], radius=[30, 75], is_label_show=True, label_text_size=20,
            legend_orient='vertical', legend_pos='right', legend_text_size=14)
    ########################################################################
    # data = score.tolist()
    # data = list(itertools.chain.from_iterable(data))
    #
    # labels = ['happy', 'angry', 'sad', 'fear', 'surprise', 'boring']
    # colors = ['#ff9999', '#ffc000', '#8fd9b6', '#d395d0', '#00ccff', '#00ff22']
    # wedgeprops = {'width': 0.7, 'edgecolor': 'w', 'linewidth': 5}
    # explode = [0.05, 0.05, 0.05, 0.05, 0.05, 0.05]
    #
    # plt.pie(data, labels=labels, autopct='%.1f%%', startangle=260, counterclock=False, colors=colors,
    #         wedgeprops=wedgeprops, explode=explode)
    #
    # fig = pie.gcf()
    # buf = io.BytesIO()
    # fig.savefig(buf, format='png')
    # buf.seek(0)
    # string = base64.b64encode(buf.read())
    # uri = urllib.parse.quote(string)
    # plt.close(fig)

    return result, pie


def okt_tokenize(sent):
    words = okt.pos(sent)
    words = [w for w in words if ('Adjective' in w or 'Verb' in w or 'Noun' in w)]
#     words = [w for w in words if ('Adjective' in w or 'Verb' in w )]
    return words


def func(sentence):
    result = okt_tokenize(sentence)
    t = []
    for j in range(len(result)):
        t.append(str(result[j][0]))
    return t


def recommend(sentence):
    score = prepro(sentence)
    if score.argmax() == 0:
        df_rec = lyric[lyric['label'] == 1]
        df_rec = df_rec.reset_index(drop=True)
    if score.argmax() == 1:
        df_rec = lyric[lyric['label'] == 0]
        df_rec = df_rec.reset_index(drop=True)
    if score.argmax() == 2:
        df_rec = lyric[lyric['label'] == 0]
        df_rec = df_rec.reset_index(drop=True)
    if score.argmax() == 3:
        df_rec = lyric[lyric['label'] == 0]
        df_rec = df_rec.reset_index(drop=True)
    if score.argmax() == 4:
        df_rec = lyric[lyric['label'] == 0]
        df_rec = df_rec.reset_index(drop=True)
    if score.argmax() == 5:
        df_rec = lyric[lyric['label'] == 0]
        df_rec = df_rec.reset_index(drop=True)

    df_rec.loc[len(df_rec)] = ['', '', '', sentence, '', '']
    c = func(df_rec['lyric'][len(df_rec) - 1])
    df_rec['lyric_clean'][len(df_rec) - 1] = ' '.join(c)

    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(df_rec['lyric_clean'])

    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    indices = pd.Series(df_rec.index, index=df_rec['title']).drop_duplicates()

    idx = indices['']

    sim_scores = list(enumerate(cosine_sim[idx]))

    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    sim_scores = sim_scores[1:6]

    song_indices = [i[0] for i in sim_scores]

    return df_rec.iloc[song_indices, 1:3]
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
            question.author = request.user

            question.save()
            question.moodres, uri = mood(question.content)
            uri2 = uri.render_embed()
            script_list = uri.get_js_dependencies()
            recom = recommend(question.content)
            tre = recom['title']
            sre = recom['singer']
            singlist = tre + " - " + sre
            print(singlist)
            # return redirect('mydiary:main')
            context = {'form': form, 'data': uri2, "script_list": script_list,
                       "host": REMOTE_HOST,'singlist': singlist}
    else:
        form = DiaryForm()
        context = {'form': form}
        print(4)

    # context={'form': form}
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
    uri2 = uri.render_embed()
    script_list = uri.get_js_dependencies()
    ###################
    recom = recommend(question.content)
    tre = recom['title']
    sre = recom['singer']
    singlist = tre + " - " + sre
    ###################
    context = {'question': question, 'data': uri2, "script_list": script_list, "host": REMOTE_HOST, 'singlist': singlist}
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
