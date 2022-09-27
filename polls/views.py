from django.forms import Form,inlineformset_factory,widgets,modelform_factory
from votewebG.settings import DATABASES
from django.shortcuts import redirect, render,render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.db import connection,transaction
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from polls.models import *
from polls.froms import *
from django.forms import modelformset_factory
from django.contrib.admin.widgets import AdminDateWidget,AdminTimeWidget,AdminSplitDateTime
from django.contrib.auth.models import User,Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages, auth
from .decorators import allowed_user, unauthenticated_user, only_admin
from django.views.generic import View
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage
from votewebG import settings
import pyodbc
# Create your views here.

@only_admin
def index(request):
    vote=Election.objects.all()
    user=User.objects.all()
    poll=Poll.objects.all()
   
    
    pollcount=poll.count()
    usercount=user.count()
    votecount=vote.count()
    eventcount=poll.count() + vote.count()
    context={ }
    return render(request, 'polls/index.html', {'votecount':votecount,'usercount':usercount,'pollcount':pollcount,'eventcount':eventcount})

def deletevote(request, election_id):
    vote=Election.objects.get(pk=election_id)
    vote.delete()
    return redirect('managevote')

@only_admin
def editvote(request, election_id):  
    data=Election.objects.all()
    upvote=Election.objects.get(pk=election_id)
    form=CreateVoteForm(request.POST, request.FILES,instance=upvote)
    if form.is_valid():
       form.save()
       return redirect('managevote')
    return render(request, 'polls/editvote.html', {'form':form, 'upvote':upvote, 'election':data})

def votedelete(request, election_id):
    vote=Election.objects.get(pk=election)
    vote.delete()
    return redirect('managevote')

@only_admin
def managevote(request):
    data=Election.objects.all()
    p = Paginator(Election.objects.all(), 4)
    page=request.GET.get('page')
    votev=p.get_page(page)
    return render(request, 'polls/managevote.html', {'election':data, 'electionv':votev})

@only_admin
def polledit(request, poll_id):  
    context = {}
    question = Poll.objects.get(pk=poll_id)
    poll_form = PollForm(request.POST or None, instance=question)
    choice_forms = [ChoiceForm(request.POST or None, prefix=str(
        choice.id), instance=choice) for choice in question.choice_set.all()]
    if poll_form.is_valid() and all([cf.is_valid() for cf in choice_forms]):
        new_poll = poll_form.save(commit=False)
        new_poll.created_by = request.user
        new_poll.save()
        for cf in choice_forms:
            new_choice = cf.save(commit=False)
            new_choice.question = new_poll
            new_choice.save()
        return redirect('managepoll')
    context = {'poll_form': poll_form, 'choice_forms': choice_forms}
    return render(request, 'polls/polledit.html', context)

def polldelete(request, poll_id):
    poll=Poll.objects.get(pk=poll_id)
    poll.delete()
    return redirect('managepoll')

@only_admin
def managepoll(request):
    data=Poll.objects.all()
    
    p = Paginator(Poll.objects.all(), 5)
    page=request.GET.get('page')
    pollv=p.get_page(page)
    
    return render(request, 'polls/managepoll.html', {'poll':data, 'pollv':pollv}) 

@only_admin   
def manageadmin(request):
    data=User.objects.all()
    p = Paginator(User.objects.all(), 6)
    page=request.GET.get('page')
    userv=p.get_page(page)
    
    return render(request, 'polls/manageadmin.html',{'user':data,'userv':userv})

@only_admin  
def edituser(request,user_id):
    alluser=User.objects.all()
    upuser=User.objects.get(pk=user_id)
    form=UserForm(request.POST or None, request.FILES or None,instance=upuser)
    if form.is_valid():
       form.save()
       return redirect('manageadmin')
    return render(request, 'polls/edituser.html', {'form':form, 'upuser':upuser, 'alluser':alluser})

@only_admin
def report(request):
    data=Election.objects.all()
    p = Paginator(Election.objects.all(), 3)
    page=request.GET.get('page')
    votere=p.get_page(page)
    return render(request, 'polls/report.html',{'vvote':data, 'votere':votere})


def register(request): 
    form=CreateUserForm()
    if request.method== 'POST':
        form=CreateUserForm(request.POST)
        if form.is_valid():
            user=form.save()
            username=form.cleaned_data.get('username')
            
            group=Group.objects.get(name='commonuser')
            user.groups.add(group)
            messages.success(request, 'ลงทะเบียนสำเร็จ' )
            return redirect('loginform')
    context={'form':form}        
    return render(request, 'polls/register.html', context)


def loginform(request):
    form=AuthenUserForm()  
    if request.method== 'POST':
        username=request.POST['username']
        pwd=request.POST['password']
        admin=authenticate(username=username,password=pwd)
        
        if admin is not None:
            login(request,admin)
            messages.success(request,'Login Successfully')
            return redirect('index')
        else:
            messages.info(request, 'Buasri ID OR Password is incorrect')
            return redirect('loginform')
    return render(request, 'polls/loginform.html', {'form':form})
    

def logoutUser(request):
    auth.logout(request)
    return redirect('loginform')


def frontdex(request):
    data=Election.objects.all()
    return render(request, 'polls/frontdex.html',{'vvote':data})

class PollView(View):
    
    def get(self, request, id=None):
        if id:
            question = get_object_or_404(Poll, id=id)
            poll_form = PollForm(instance=question)
            choices = question.choice_set.all()
            choice_forms = [ChoiceForm(prefix=str(
                choice.id), instance=choice) for choice in choices]
            template = 'polls/editpoll.html'
        else:
            poll_form = PollForm(instance=Poll())
            choice_forms = [ChoiceForm(prefix=str(
                x), instance=Choice()) for x in range(4)]
            template = 'polls/createpoll.html'
        context = {'poll_form': poll_form, 'choice_forms': choice_forms}
        return render(request, template, context)


    def post(self, request, id=None):
        context = {}
        if id:
            return self.put(request, id)
        poll_form = PollForm(request.POST, instance=Poll())
        choice_forms = [ChoiceForm(request.POST, prefix=str(
            x), instance=Choice()) for x in range(0, 4)]
        if poll_form.is_valid() and all([cf.is_valid() for cf in choice_forms]):
            new_poll = poll_form.save(commit=False)
            new_poll.created_by = request.user
            new_poll.save()
            for cf in choice_forms:
                new_choice = cf.save(commit=False)
                new_choice.question = new_poll
                new_choice.save()
            return redirect('vote')
        context = {'poll_form': poll_form, 'choice_forms': choice_forms}
        return render(request, 'polls/createpoll.html', context)


    def put(self, request, id=None):
        context = {}
        question = get_object_or_404(Poll, id=id)
        poll_form = PollForm(request.POST, instance=question)
        choice_forms = [ChoiceForm(request.POST, prefix=str(
            choice.id), instance=choice) for choice in question.choice_set.all()]
        if poll_form.is_valid() and all([cf.is_valid() for cf in choice_forms]):
            new_poll = poll_form.save(commit=False)
            new_poll.created_by = request.user
            new_poll.save()
            for cf in choice_forms:
                new_choice = cf.save(commit=False)
                new_choice.question = new_poll
                new_choice.save()
            return redirect('vote')
        context = {'poll_form': poll_form, 'choice_forms': choice_forms}
        return render(request, 'polls/editpoll.html', context)

    def delete(self, request, id=None):
        question = get_object_or_404(Poll)
        question.delete()
        return redirect('vote')

def deletepoll(request, id=None):
        question = get_object_or_404(Poll,id=id)
        question.delete()
        return redirect('vote') 
    

@login_required(login_url="/login/")
def letpoll(request, poll_id):
    context = {}
    try:
        question = Poll.objects.get(pk=poll_id)
    except:
        raise Http404
    context["question"] = question

    if request.method == "POST":
        user_id = request.user.id
        print(request.POST)
        data = request.POST

        ret = Answer.objects.create(user_id=user_id, choice_id=data['choice'])
        if ret:
            return HttpResponseRedirect(reverse('vote', args=[]))
        else:
            context["error"] = "Your vote is not done successfully"
            return render(request, 'polls/poll.html', context)
    else:
        return render(request, 'polls/letpoll.html', context)

def pollresult(request, poll_id):
    context = {}
    try:
        question = Poll.objects.get(pk=poll_id)
    except:
        raise Http404
    context['question'] = question
    return render(request, 'polls/pollresult.html', context) 

class ElectView(View):
    
    def get(self, request, id=None):
        if id:
            name = get_object_or_404(Election, id=id)
            elect_form = CreateVoteForm(instance=name)
            candys = name.candidate_set.all()
            candy_forms = [CandidateForm(prefix=str(
                candy.id), instance=candy) for candy in candys]
            template = 'polls/editelect.html'
        else:
            elect_form = CreateVoteForm(instance=Election())
            candy_forms = [CandidateForm(prefix=str(
                x), instance=Candidate()) for x in range(4)]
            template = 'polls/createelect.html'
        context = {'elect_form': elect_form, 'candy_forms': candy_forms}
        return render(request, template, context)


    def post(self, request, id=None):
        context = {}
        if id:
            return self.put(request, id)
        
        elect_form = CreateVoteForm(data=request.POST, files=request.FILES, instance=Election())
        candy_forms = [CandidateForm(request.POST, request.FILES, prefix=str(
            x), instance=Candidate()) for x in range(0, 4)]
        if elect_form.is_valid() and all([cf.is_valid() for cf in candy_forms]):
            new_elect = elect_form.save(commit=False)
            new_elect.created_by = request.user
            new_elect.save()
            for cf in candy_forms:
                new_candy = cf.save(commit=False)
                new_candy.election = new_elect
                new_candy.save()
            return redirect('vote')
        context = {'elect_form': elect_form, 'candy_forms': candy_forms}
        return render(request, 'polls/createelect.html', context)


    def put(self, request, id=None):
        context = {}
        name = get_object_or_404(Election, id=id)
        elect_form = CreateVoteForm(data=request.POST, files=request.FILES, instance=name)
        candy_forms = [CandidateForm(request.POST or None, request.FILES or None, prefix=str(
            candy.id), instance=candy) for candy in name.candidate_set.all()]
        if elect_form.is_valid() and all([cf.is_valid() for cf in candy_forms]):
            new_elect = elect_form.save(commit=False)
            new_elect.created_by = request.user
            new_elect.save()
            for cf in candy_forms:
                new_candy = cf.save(commit=False)
                new_candy.question = new_elect
                new_candy.save()
            return redirect('vote')
        context = {'elect_form': elect_form, 'candy_forms': candy_forms}
        return render(request, 'polls/editelect.html', context)


    def delete(self, request, id=None):
        name = get_object_or_404(Election)
        name.delete()
        return redirect('vote') 
    
def deleteelect(request, id=None):
        election = get_object_or_404(Election,id=id)
        election.delete()
        return redirect('vote') 


@login_required(login_url="/login/")
def letelect(request, election_id):
    context = {}
    try:
        election = Election.objects.get(pk=election_id)
    except:
        raise Http404
    context["election"] = election

    if request.method == "POST":
        user_id = request.user.id
        print(request.POST)
        data = request.POST
        ret = Voted.objects.create(user_id=user_id, candy_id=data['candidate'])
        if ret:
            return HttpResponseRedirect(reverse('vote', args=[]))
        else:
            context["error"] = "Your vote is not done successfully"
            return render(request, 'polls/vote.html', context)
    else:
        return render(request, 'polls/letelect.html', context)
    
def electresult(request, election_id):
    context = {}
    try:
        election = Election.objects.get(pk=election_id)
    except:
        raise Http404
    context['election'] = election
    return render(request, 'polls/electresult.html', context) 


def createvote(request):
    candyFormset=modelformset_factory(Candidate, form=CandidateForm,extra=2,max_num=4)
    formp=PollForm()
    formv=CreateVoteForm(request.POST, request.FILES)
    formset=candyFormset(request.POST or None, request.FILES or None, queryset=Candidate.objects.none(), prefix='candidate')
    if request.method == 'POST':
        formp=PollForm(request.POST)
        formv=CreateVoteForm(data=request.POST, files=request.FILES)
        if formp.is_valid():
            formp.save()
            messages.success(request, 'สร้างโหวตสำเร็จ' )
            return redirect('vote')
        if formv.is_valid() and formset.is_valid():
            with transaction.atomic():
                election=formv.save(commit=False)
                election.save()
                for candy in formset:
                    data=candy.save(commit=False)
                    data.election=election
                    data.save()
                messages.success(request, 'สร้างโหวตสำเร็จ' )
            return redirect('vote')
        else:
            messages.success(request, 'สร้างโหวตไม่สำเร็จ กรุณาตรวจสอบข้อมูล' )
    return render(request, 'polls/createvote.html',  {
        'formp':formp,
        'formv':formv,
        'formset':formset,
    } )
    

def vote(request):
    context = {}
    pol = Poll.objects.all()
    context['question'] = 'โพลคำถาม'
    context['pol'] = pol
    ele = Election.objects.all()
    context['election'] = 'โหวตเลือกตั้ง'
    context['ele'] = ele
    return render(request, 'polls/vote.html', context)   

def letvote(request, election_id):
    election=Election.objects.filter(pk=election_id)
   
    return render(request, 'polls/letvote.html', {'election':election,})
