from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):  
    coins = models.IntegerField(default=0)
    def __str__(self):
        return self.username

class Contest(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image  = models.ImageField(upload_to='images/', blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
   # created_at = models.DateTimeField(auto_now_add=True)
    entry_fee = models.IntegerField(default=0)
    limit = models.IntegerField(default = 5)
    def __str__(self):
        return self.title
    


class Submission(models.Model):
   # participation = models.ForeignKey(Participation, on_delete=models.CASCADE)
    html_code = models.TextField() 
    css_code = models.TextField() 
    contest_id = models.ForeignKey(Contest, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    votes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.participation.user.username}'s submission for {self.participation.contest.title}"


class Participation(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    contest_id = models.ForeignKey(Contest, on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)
    submission_id = models.ForeignKey(Submission, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} in {self.contest.title}"

