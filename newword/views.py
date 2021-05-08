from hashlib import new
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import Test, Lesson, NewWord, Quest
import random
from django.core import serializers
from django.http import JsonResponse
from .forms import CustomUserCreationForm
from django.urls import reverse

# Create your views here.

@login_required
def home(request):
  lessons = Lesson.objects.all()
  context = {
    "lessons": lessons,
  }
  return render(request, "home.html", context)

@login_required
def lesson_test(request, lesson_id):
  newWords = list(NewWord.objects.filter(lesson=lesson_id))
  
  test = Test()
  test.user = request.user
  test.lesson = Lesson.objects.get(pk=lesson_id)
  test.num_of_quest = len(newWords)
  test.save()
  
  random.shuffle(newWords)
  questions = []
  for newWord in newWords:
    quest = Quest()
    quest_str, result = "", ""
    r = random.randint(1,3)
    if r == 1:
      quest_str = f"{newWord.meaning}({newWord.get_wtype_display()}) in English is ..."
      result = newWord.word
    elif r == 2:
      quest_str = f"{newWord.word}({newWord.meaning}) word type is ..."
      result = str(newWord.wtype)
    elif r == 3:
      quest_str = f"{newWord.word}({newWord.get_wtype_display()}) meaning is ..."
      result = newWord.meaning
    quest.question = quest_str
    quest.qtype = r
    quest.test = test
    quest.result = result
    quest.save()
    questions.append(quest)
  request.session["questpks"] = [x.pk for x in questions]
  context = {
    "test": test,
    "questions": questions,
  }
  return render(request, "test.html", context)

@login_required
def grading(request):
  if request.is_ajax and request.method == "POST":
    answer = request.POST.getlist("ans[]")
    print(answer)
    questpks = request.session["questpks"]
    for ind, pk in enumerate(questpks):
      print(ind)
      quest = Quest.objects.get(pk=pk)
      quest.answer = answer[ind]
      quest.correct = 0
      if answer[ind].lower() == quest.result.lower():
        quest.correct = 1
      quest.save()
    test = quest.test
    test.score = Quest.objects.filter(test=test).filter(correct=1).count()
    test.save()
    ser_instance = serializers.serialize('json', [ test, ])
    # send to client side.
    return JsonResponse({"test": ser_instance}, status=200)
  return JsonResponse({"error": ""}, status=400)

@login_required
def review(request, test_id):
  test = Test.objects.get(pk=test_id)
  quests = Quest.objects.filter(test=test)
  print(quests)
  context = {
    "test": test,
    "quests": quests,
    "wtype": {
      "1": "Noun",
      "2": "Verb",
      "3": "Adjective",
      "4": "Adverb"
    }
  }
  return render(request, "review.html", context)

@login_required
def view_history(request):
  tests = Test.objects.filter(user=request.user)
  context = {
    "tests": tests,
  }
  return render(request, "history.html", context)

def register(request):
  if request.method == "GET":
    form = CustomUserCreationForm()
    context = {
      "form": form,
    }
    return render(request, "register.html", context)
  elif request.method == "POST":
    form = CustomUserCreationForm(request.POST)
    if form.is_valid:
      user = form.save()
      login(request, user)
      return redirect(reverse("home"))
    else:
      return redirect(reverse("register"))

@login_required
def random_test(request):
  test = Test()
  test.user = request.user
  test.num_of_quest = 6
  test.save()
  
  allWords = list(NewWord.objects.all())
  wordCount = len(allWords)
  print(wordCount)
  newWordInds, newWords, questions = [], [], []
  index = 0
  while index < test.num_of_quest:
    r = random.randint(1, wordCount-1)
    if r not in newWordInds:
      newWordInds.append(r)
      index += 1
  print(newWordInds)
  for pk in newWordInds:
    newWords.append(allWords[pk])
  for newWord in newWords:
    quest = Quest()
    quest_str, result = "", ""
    r = random.randint(1,3)
    if r == 1:
      quest_str = f"{newWord.meaning}({newWord.get_wtype_display()}) in English is ..."
      result = newWord.word
    elif r == 2:
      quest_str = f"{newWord.word}({newWord.meaning}) word type is ..."
      result = str(newWord.wtype)
    elif r == 3:
      quest_str = f"{newWord.word}({newWord.get_wtype_display()}) meaning is ..."
      result = newWord.meaning
    quest.question = quest_str
    quest.qtype = r
    quest.test = test
    quest.result = result
    quest.save()
    questions.append(quest)
  request.session["questpks"] = [x.pk for x in questions]
  context = {
    "test": test,
    "questions": questions,
  }
  return render(request, "test.html", context)