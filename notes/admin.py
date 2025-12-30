from django.contrib import admin
from .models import Course, Topic, Note, Document, Flashcard, StudySession, SharedNote, Comment, VoiceNote, UserActivity

# Register your models here.
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['course_code', 'name', 'university', 'owner', 'instructor']
    search_fields = ['name', 'course_code']
    list_filter = ['university']

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'owner']
    search_fields = ['name']
    list_filter = ['course']

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'topic', 'created_at', 'updated_at']
    search_fields = ['title', 'content']
    list_filter = ['topic', 'created_at']
    date_hierarchy = 'created_at'

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'topic', 'uploaded_at']
    search_fields = ['title']
    list_filter = ['topic', 'uploaded_at']

@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ['note', 'question', 'created_at']
    search_fields = ['question', 'answer']
    list_filter = ['created_at']

@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'note', 'started_at', 'duration_minutes']
    list_filter = ['started_at']

@admin.register(SharedNote)
class SharedNoteAdmin(admin.ModelAdmin):
    list_display = ['note', 'shared_by', 'shared_with', 'can_edit', 'shared_at']
    list_filter = ['can_edit', 'shared_at']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['note', 'user', 'created_at']
    list_filter = ['created_at']

@admin.register(VoiceNote)
class VoiceNoteAdmin(admin.ModelAdmin):
    list_display = ['note', 'created_at']
    list_filter = ['created_at']

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'note', 'timestamp']
    list_filter = ['activity_type', 'timestamp']
    date_hierarchy = 'timestamp'
