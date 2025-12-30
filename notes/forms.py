from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.conf import settings
import os
from .models import Note, Course, Topic, Document


def validate_file_extension(value):
    """Validate file extension for security"""
    ext = os.path.splitext(value.name)[1].lower().replace('.', '')
    allowed_extensions = getattr(settings, 'ALLOWED_UPLOAD_EXTENSIONS', [
        'pdf', 'doc', 'docx', 'txt', 'md',
        'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp',
        'mp3', 'wav', 'ogg', 'm4a',
        'ppt', 'pptx', 'xls', 'xlsx',
        'zip', 'rar'
    ])
    
    if ext not in allowed_extensions:
        raise ValidationError(
            f'Unsupported file extension: .{ext}. Allowed types: {", ".join(allowed_extensions)}'
        )


def validate_file_size(value):
    """Validate file size for security"""
    max_size = getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 10485760)  # 10 MB default
    if value.size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        raise ValidationError(f'File size cannot exceed {max_size_mb} MB')


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'maxlength': '150'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'maxlength': '150'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'maxlength': '150'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
        }
    
    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        if email:
            # Check if email is already taken by another user
            existing_user = User.objects.filter(email=email).exclude(pk=self.instance.pk).first()
            if existing_user:
                raise ValidationError('This email address is already in use.')
        return email


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content', 'topic']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600',
                'maxlength': '200'
            }),
            'topic': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600'
            }),
        }
    
    def clean_title(self):
        """Sanitize title input"""
        title = self.cleaned_data.get('title')
        # Remove any potential XSS attempts
        dangerous_chars = ['<', '>', 'javascript:', 'onerror=', 'onload=']
        for char in dangerous_chars:
            if char.lower() in title.lower():
                raise ValidationError('Title contains invalid characters')
        return title

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file', 'topic']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600',
                'maxlength': '200'
            }),
            'file': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600',
                'accept': '.pdf,.doc,.docx,.txt,.md,.jpg,.jpeg,.png,.gif,.bmp,.webp,.mp3,.wav,.ogg,.m4a,.ppt,.pptx,.xls,.xlsx,.zip,.rar'
            }),
            'topic': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600'
            }),
        }
    
    def clean_file(self):
        """Validate uploaded file"""
        file = self.cleaned_data.get('file')
        if file:
            # Validate file extension
            validate_file_extension(file)
            # Validate file size
            validate_file_size(file)
        return file
    
    def clean_title(self):
        """Sanitize title input"""
        title = self.cleaned_data.get('title')
        dangerous_chars = ['<', '>', 'javascript:', 'onerror=', 'onload=']
        for char in dangerous_chars:
            if char.lower() in title.lower():
                raise ValidationError('Title contains invalid characters')
        return title


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'course_code', 'instructor']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'maxlength': '100'}),
            'course_code': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'maxlength': '20'}),
            'instructor': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'maxlength': '100'}),
        }
    
    def clean_course_code(self):
        """Validate and sanitize course code"""
        code = self.cleaned_data.get('course_code')
        if code:
            # Only allow alphanumeric and basic punctuation
            import re
            if not re.match(r'^[A-Za-z0-9\s\-_]+$', code):
                raise ValidationError('Course code can only contain letters, numbers, spaces, hyphens, and underscores')
        return code


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['name', 'course']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-lg', 'maxlength': '100'}),
            'course': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
        }
    
    def clean_name(self):
        """Sanitize topic name"""
        name = self.cleaned_data.get('name')
        dangerous_chars = ['<', '>', 'javascript:', 'onerror=', 'onload=']
        for char in dangerous_chars:
            if char.lower() in name.lower():
                raise ValidationError('Name contains invalid characters')
        return name
            'course': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg'}),
        }
