from django.db import models
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager

# Create your models here.
class Course(models.Model):
    name = models.CharField(max_length=100)
    course_code = models.CharField(max_length=20, unique=True)
    university = models.CharField(max_length=100, default='University of Dodoma')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses', null=True, blank=True)
    instructor = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.course_code} - {self.name}"

class Topic(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='topics')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topics', null=True, blank=True)

    def __str__(self):
        return self.name

class Note(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextUploadingField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = TaggableManager()

    def __str__(self):
        return self.title

class Document(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='documents')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
