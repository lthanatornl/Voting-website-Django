from django.db import models
from django.contrib.auth.models import User,AbstractBaseUser,BaseUserManager,UserManager
from django.db import connection,transaction,models
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.http import HttpResponse, HttpResponseRedirect, Http404
from votewebG import settings
from datetime import datetime
from django.utils import timezone



#--------------------------------User --Zone -----------------------------------------------

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='all_user', max_length=255, null=True, blank=True)

    def __str__(self):
        return "{0} - {1}".format(self.user.username)



class UserManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(profile__designation="User")

class CustomUser(User):
    class Meta:
        ordering = ("username",)
        proxy = True

    objects = UserManager()
    
    def full_name(self):
        return self.first_name + " - " + self.last_name


@receiver(post_save, sender=User)
def user_is_created(sender, instance, created, **kwargs):
    print(created)
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()


from django.contrib.auth.models import User

@property
def full_name(self):
    return "{} {}".format(self.first_name, self.last_name)

User.add_to_class('full_name', full_name)

#-----------------------------END User -- Zone -----------------------------------------------
#-----------------------------Poll -- Zone----------------------------------------------------
class ObjectTracking(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
 

class Comment(models.Model):
    text = models.TextField(null=False, blank=False)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.text[:20]

class Tag(ObjectTracking):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        ordering = []

class QuestionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status="open")

    def all_objects(self):
        return super().get_queryset()

    def inactive(self):
        durate= self.vote_end <= datetime.now() <= self.vote_start
        return durate.all_objects().filter(status='Close')



class Poll(ObjectTracking):
    STATUS = (
        ("OPEN", "Open"),
        ("CLOSE", "Close"),
    )
    question = models.TextField()
    status = models.CharField(choices=STATUS,default='OPEN', max_length=10)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    poll_start = models.DateTimeField(null=True, blank=True,default=datetime.now())
    poll_end = models.DateTimeField(null=True, blank=True)
    tags = models.ManyToManyField(Tag)

    comments = GenericRelation(Comment, related_name="question")

    objects = QuestionManager()


    def __str__(self):
        return self.question
    
    @property
    def choices(self):
        return self.choice_set.all()
    


class Choice(models.Model):
    question = models.ForeignKey(Poll, on_delete=models.CASCADE)
    text = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text

    @property
    def votes(self):
        return self.answer_set.count()


class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    comments = GenericRelation(Comment, related_name="answer")

    def __str__(self):
        return self.user.first_name + ' --has ans-- ' + self.choice.text
#-------------------------END Poll--Zone--------------------------------------------------
#--------------------------- Election -- Zone --------------------------------------------

class Election(ObjectTracking):
    TYPES = (
        ("Pl", "Plurality"),
        ("Pr", "Preferential"),
    )
    STATUS = (
        ("OPEN", "Open"),
        ("CLOSE", "Close"),
    )
    name = models.CharField(max_length=120,null=False, blank=False)
    status = models.CharField(choices=STATUS,default='OPEN', max_length=10)
    created_by = models.ForeignKey(User, related_name="Creator",null=True, blank=True, on_delete=models.CASCADE)
    allowed_voters = models.ManyToManyField(settings.DJANGO_ELECT_USER_MODEL, related_name="Voter",blank=True)
    introduction=models.TextField(null=True, blank=True)
    picture=models.ImageField(upload_to="vote_pic",null=False, blank=False)
    vote_start = models.DateTimeField(null=False, blank=False,default=datetime.now())
    vote_end = models.DateTimeField(null=False, blank=False)
    type = models.CharField(max_length=2, blank=True, choices=TYPES,default="Pl")

    objects = QuestionManager()

    def __str__(self):
        return self.name

    def voting_allowed_for_user(self, user):
        """
        Returns True if not is between vote_start and vote_end, inclusive,
        and given user is in allowed_voters and user hasn't already voted.
        """
        return (self.voting_allowed() and not self.has_voted(user) and
            (self.allowed_voters.count() == 0 or
            self.allowed_voters.filter(id=user.id)))

    @property
    def candys(self):
        return self.candidate_set.all()


class Candidate(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=65)
    last_name = models.CharField(max_length=65)
    image=models.ImageField(upload_to='candy_pic')
    biography = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.election.name + ": " +self.first_name + " " + self.last_name

    @property
    def voted(self):
        return self.voted_set.count()


class Voted(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    candy = models.ForeignKey(Candidate, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.first_name + '-- has choose --' + self.candy.first_name
    
    
    
class VotePreferential(models.Model):
    """
    Vote for a candidate on a preferential ballot (i.e. Ballot.type="Pr")
    """
    vote = models.ForeignKey(Voted, related_name="preferentials", null=True, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    point = models.PositiveSmallIntegerField()

    def __unicode__(self):
        return "%s vote, %i points for %s" % (self.vote, self.point,
                                              self.candidate.get_name())


class VotePlurality(models.Model):
    """
    Vote for a candidate on a plurality ballot (i.e. Ballot.type="Pl")
    """
    vote = models.ForeignKey(Voted, related_name="pluralities", null=True, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)

    def __unicode__(self):
        return "%s vote for %s" % (self.vote, self.candidate.get_name())
