from django.contrib import admin
from django.urls import reverse
from dal import autocomplete
from polls.models import *
from votewebG import settings
from django import forms
from polls import views
from django.http import HttpResponseRedirect
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import User,AbstractBaseUser,BaseUserManager
from votewebG import settings


#Register Your models!!

class CandidateInline(admin.StackedInline):
    model = Candidate
    extra = 2
    max_num=4
    
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'vote_start', 'vote_end')
    filter_horizontal = ("allowed_voters",)
    inlines = [CandidateInline]

admin.site.register(Election, ElectionAdmin)
admin.site.register(Candidate)
admin.site.register(Voted)
admin.site.register(Poll)
admin.site.register(Choice)
admin.site.register(Answer)
admin.site.register(Tag)

