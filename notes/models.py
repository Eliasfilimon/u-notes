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

class Flashcard(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='flashcards')
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Flashcard for {self.note.title}"

class StudySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='study_sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.note.title}"

class SharedNote(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='shares')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_notes')
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notes')
    can_edit = models.BooleanField(default=False)
    shared_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('note', 'shared_with')
    
    def __str__(self):
        return f"{self.note.title} shared with {self.shared_with.username}"

class Comment(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.note.title}"

class VoiceNote(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='voice_notes')
    audio_file = models.FileField(upload_to='voice_notes/')
    transcription = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Voice note for {self.note.title}"

class UserActivity(models.Model):
    ACTIVITY_TYPES = [
        ('create', 'Created'),
        ('edit', 'Edited'),
        ('view', 'Viewed'),
        ('share', 'Shared'),
        ('comment', 'Commented'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=10, choices=ACTIVITY_TYPES)
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'User Activities'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} {self.get_activity_type_display()} at {self.timestamp}"
