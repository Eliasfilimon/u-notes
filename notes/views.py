from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Note, Course, Topic, Document
from .forms import NoteForm, CourseForm, TopicForm, UserUpdateForm, DocumentForm
from django.db import models
from taggit.models import Tag

def home(request):
    if request.user.is_authenticated:
        return redirect('note_list')
    return render(request, 'notes/landing.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('note_list')
    else:
        form = UserCreationForm()
    return render(request, 'notes/signup.html', {'form': form})

@login_required
def note_list(request, course_id=None, topic_id=None, tag_slug=None):
    notes = Note.objects.filter(owner=request.user).order_by('-updated_at')
    course = None
    topic = None
    tag = None

    if course_id:
        course = get_object_or_404(Course, pk=course_id, owner=request.user)
        notes = notes.filter(topic__course=course)
    
    if topic_id:
        topic = get_object_or_404(Topic, pk=topic_id, owner=request.user)
        notes = notes.filter(topic=topic)

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        notes = notes.filter(tags__in=[tag])

    return render(request, 'notes/note_list.html', {'notes': notes, 'course': course, 'topic': topic, 'tag': tag})

@login_required
def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    return render(request, 'notes/note_detail.html', {'note': note})

@login_required
def note_create(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        form.fields['topic'].queryset = Topic.objects.filter(owner=request.user)
        if form.is_valid():
            note = form.save(commit=False)
            note.owner = request.user
            note.save()
            form.save_m2m()
            return redirect('note_list')
    else:
        form = NoteForm()
        form.fields['topic'].queryset = Topic.objects.filter(owner=request.user)
    return render(request, 'notes/note_form.html', {'form': form})

@login_required
def note_update(request, pk):
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        form.fields['topic'].queryset = Topic.objects.filter(owner=request.user)
        if form.is_valid():
            form.save()
            return redirect('note_list')
    else:
        form = NoteForm(instance=note)
        form.fields['topic'].queryset = Topic.objects.filter(owner=request.user)
    return render(request, 'notes/note_form.html', {'form': form})

@login_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    if request.method == 'POST':
        note.delete()
        return redirect('note_list')
    return render(request, 'notes/note_confirm_delete.html', {'note': note})

@login_required
def course_list(request):
    courses = Course.objects.filter(owner=request.user)
    return render(request, 'notes/course_list.html', {'courses': courses})

@login_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.owner = request.user
            course.save()
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'notes/course_form.html', {'form': form})

@login_required
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'notes/course_form.html', {'form': form})

@login_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk, owner=request.user)
    if request.method == 'POST':
        course.delete()
        return redirect('course_list')
    return render(request, 'notes/course_confirm_delete.html', {'course': course})

@login_required
def topic_list(request):
    topics = Topic.objects.filter(owner=request.user)
    return render(request, 'notes/topic_list.html', {'topics': topics})

@login_required
def topic_create(request):
    if request.method == 'POST':
        form = TopicForm(request.POST)
        form.fields['course'].queryset = Course.objects.filter(owner=request.user)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.owner = request.user
            topic.save()
            return redirect('topic_list')
    else:
        form = TopicForm()
        form.fields['course'].queryset = Course.objects.filter(owner=request.user)
    return render(request, 'notes/topic_form.html', {'form': form})

@login_required
def topic_update(request, pk):
    topic = get_object_or_404(Topic, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = TopicForm(request.POST, instance=topic)
        form.fields['course'].queryset = Course.objects.filter(owner=request.user)
        if form.is_valid():
            form.save()
            return redirect('topic_list')
    else:
        form = TopicForm(instance=topic)
        form.fields['course'].queryset = Course.objects.filter(owner=request.user)
    return render(request, 'notes/topic_form.html', {'form': form})

@login_required
def topic_delete(request, pk):
    topic = get_object_or_404(Topic, pk=pk, owner=request.user)
    if request.method == 'POST':
        topic.delete()
        return redirect('topic_list')
    return render(request, 'notes/topic_confirm_delete.html', {'topic': topic})

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'notes/profile.html', {'form': form})

@login_required
def search_results(request):
    query = request.GET.get('q')
    if query:
        notes = Note.objects.filter(owner=request.user).filter(
            models.Q(title__icontains=query) | models.Q(content__icontains=query)
        )
    else:
        notes = Note.objects.none()
    return render(request, 'notes/search_results.html', {'notes': notes, 'query': query})

@login_required
def document_list(request):
    documents = Document.objects.filter(owner=request.user).order_by('-uploaded_at')
    return render(request, 'notes/document_list.html', {'documents': documents})

@login_required
def document_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        form.fields['topic'].queryset = Topic.objects.filter(owner=request.user)
        if form.is_valid():
            document = form.save(commit=False)
            document.owner = request.user
            document.save()
            return redirect('document_list')
    else:
        form = DocumentForm()
        form.fields['topic'].queryset = Topic.objects.filter(owner=request.user)
    return render(request, 'notes/document_form.html', {'form': form})

@login_required
def document_delete(request, pk):
    document = get_object_or_404(Document, pk=pk, owner=request.user)
    if request.method == 'POST':
        document.delete()
        return redirect('document_list')
    return render(request, 'notes/document_confirm_delete.html', {'document': document})

@login_required
def document_view(request, pk):
    document = get_object_or_404(Document, pk=pk, owner=request.user)
    file_extension = document.file.name.split('.')[-1].lower()
    
    # Categorize file types
    image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']
    pdf_extensions = ['pdf']
    text_extensions = ['txt', 'md', 'py', 'js', 'html', 'css', 'json', 'xml']
    
    file_type = 'other'
    if file_extension in image_extensions:
        file_type = 'image'
    elif file_extension in pdf_extensions:
        file_type = 'pdf'
    elif file_extension in text_extensions:
        file_type = 'text'
    
    return render(request, 'notes/document_view.html', {
        'document': document,
        'file_type': file_type,
        'file_extension': file_extension
    })
