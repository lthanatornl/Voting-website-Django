from django.forms.models import ModelForm,inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Div, HTML, ButtonHolder, Submit
from .custom_layout_object import *
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.http import urlquote
from django.utils.safestring import mark_safe
from django.conf import settings
from django import forms 
from polls.models import *
from django.forms import widgets
from django.db import models,connection,transaction
from string import Template

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','password1','password2']
        
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email']
        
class AuthenUserForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['id','password']
        
class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ['question']
        widgets={
            'question':forms.TextInput(attrs={'class':'w3-input w3-border'}),  
            
        }

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        exclude = ('question',) 
        fields = ['text']
        widgets={
            'text':forms.TextInput(attrs={'class':'w3-input w3-border'}),      
        }
        
class CreateVoteForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = ['name','picture','vote_start','vote_end','introduction']
        
        widgets={
            'name':forms.TextInput(attrs={'class':'w3-input w3-border'}),
            'picture':forms.FileInput(attrs={'class':'w3-input w3-border'}),
            'vote_start':forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S', attrs={'class':'datetimefield w3-input w3-border','id':'dateform1'}),
            'vote_end':forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S', attrs={'class':'datetimefield w3-input w3-border','id':'dateform2'}),
            'introduction':forms.Textarea(attrs={'class':'w3-input w3-border'}), 
         
        }
   

class CandidateForm(forms.ModelForm): 
    class Meta:
        model = Candidate
        exclude = ('name','picture','vote_start','vote_end','introduction','type') 
        fields = ['first_name','last_name','image','biography']
        widgets={
            'first_name':forms.TextInput(attrs={'class':'w3-input w3-border'}),
            'last_name':forms.TextInput(attrs={'class':'w3-input w3-border'}),
            'image':forms.FileInput(attrs={'class':'w3-input w3-border'}),
            'biography':forms.TextInput(attrs={'class':'w3-input w3-border'}), 
        }       
        
