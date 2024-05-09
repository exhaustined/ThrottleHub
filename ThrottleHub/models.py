from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
# Create your models here.
class Posts(models.Model):
    spotter=models.ForeignKey(User,on_delete=models.CASCADE, related_name="spotter")
    licenseplate=models.CharField(max_length=10)
    brand=models.CharField(max_length=10)
    model=models.CharField(max_length=10)
    description=models.TextField()
    date=models.DateField(auto_now_add=True)
    city=models.CharField(max_length=100)
    images1 = models.ImageField(upload_to="images/")
    images2 = models.ImageField(upload_to="images/")
    images3 = models.ImageField(upload_to="images/")
    images4 = models.ImageField(upload_to="images/")
    images5 = models.ImageField(upload_to="images/")
    description = models.CharField(max_length=1000)
    owner_id = models.IntegerField(default=0)

class Garage(models.Model):
    owner=models.ForeignKey(User,on_delete=models.CASCADE)
    licenseplate= models.CharField(max_length=10)
    brand = models.CharField(max_length=10)
    model = models.CharField(max_length=10)
    power = models.FloatField(null=True, blank=True)
    torque = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    topspeed = models.FloatField(null=True, blank=True)
    acceleration = models.FloatField(null=True, blank=True)
    image = models.ImageField(upload_to="images/")

class Follows(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="user")
    followed_by = models.ForeignKey(User,on_delete=models.CASCADE, related_name="followed_by")

    def follower_count(self):
        return Follows.objects.filter(user_id=self.user_id).count()
    def following_count(self):
        return Follows.objects.filter(followed_by=self.followed_by).count()

class ProfilePics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images/profiles/")

class ThreadManager(models.Manager):
    def by_user(self, **kwargs):
        user = kwargs.get('user')
        lookup = Q(first_person=user) | Q(second_person=user)
        qs = self.get_queryset().filter(lookup).distinct()
        return qs


class Thread(models.Model):
    first_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='thread_first_person')
    second_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                     related_name='thread_second_person')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()
    class Meta:
        unique_together = ['first_person', 'second_person']


class ChatMessage(models.Model):
    thread = models.ForeignKey(Thread, null=True, blank=True, on_delete=models.CASCADE, related_name='chatmessage_thread')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)


class Comment(models.Model):
    content = models.CharField(max_length=200, blank=True)
    post = models.ForeignKey(Posts ,on_delete=models.CASCADE, related_name='post')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    @property
    def time_diff(self):
        diff = datetime.now() - self.created
        seconds = diff.seconds
        h = seconds//(60*60)
        m = (seconds-h*60*60)//60
        s = seconds-(h*60*60)-(m*60)
        if(diff.days):
            return f"{diff.days} days ago"
        if(h != 0):
            if(h == 1):
                return f"{m} hour ago"
            return f"{h} hours ago"
        elif(m != 0):
            if(m == 1):
                return f"{m} minute ago"
            return f"{m} minutes ago"
        else:
            return f"{s} seconds ago"

class Likes(models.Model):
    post = models.ForeignKey(Posts,on_delete=models.CASCADE, related_name="liked_post")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="liker")