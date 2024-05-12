from django.db import models
# Create your models here.
from base.models import User,Material   


class Post(Material):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    content = models.TextField(default="")
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    @property
    def num_likes(self):
        return self.likes.all().count()
    class Meta:
        verbose_name = 'Bài đăng'
        verbose_name_plural = 'Bài đăng'

LIKE_CHOICE = (
    ('Like', 'Like'),
    ('Unlike', 'Unlike')
)

class Reply(Material):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    content = models.TextField(default="")
    like = models.IntegerField(default=0)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    class Meta:
        verbose_name = 'Phản hồi'
        verbose_name_plural = 'Phản hồi'
class Like(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    value = models.CharField(choices=LIKE_CHOICE,default='Like', max_length=10)
    def __str__(self):
        return str(self.post)