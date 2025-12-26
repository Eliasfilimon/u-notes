from django import forms
from django.contrib.auth.models import User
from .models import Note, Course, Topic, Document

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
        }

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content', 'topic', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600'}),
            'topic': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600'}),
            'tags': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600', 'placeholder': 'Enter comma-separated tags'}),
        }

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file', 'topic']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600'}),
            'file': forms.FileInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600'}),
            'topic': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600'}),
        }

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'course_code', 'instructor']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'course_code': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'instructor': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
        }

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['name', 'course']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
            'course': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
        }
