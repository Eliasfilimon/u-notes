from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
import json
from .models import Note, Course, Topic, Document, Flashcard, Comment, SharedNote, UserActivity, VoiceNote, StudySession
from .forms import NoteForm, CourseForm, TopicForm, UserUpdateForm, DocumentForm
from django.db import models
from django.conf import settings
from django.contrib import messages
from google import genai
import re
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import markdown

class CustomPasswordResetView(PasswordResetView):
    template_name = 'notes/password_reset.html'
    email_template_name = 'notes/password_reset_email.html'
    success_url = '/password_reset/done/'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'notes/password_reset_confirm.html'
    success_url = '/password_reset/complete/'

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
def note_list(request, course_id=None, topic_id=None):
    notes = Note.objects.filter(owner=request.user).order_by('-updated_at')
    course = None
    topic = None

    if course_id:
        course = get_object_or_404(Course, pk=course_id, owner=request.user)
        notes = notes.filter(topic__course=course)
    
    if topic_id:
        topic = get_object_or_404(Topic, pk=topic_id, owner=request.user)
        notes = notes.filter(topic=topic)

    return render(request, 'notes/note_list.html', {'notes': notes, 'course': course, 'topic': topic})

@login_required
def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    root_comments = note.comments.filter(parent__isnull=True)
    return render(request, 'notes/note_detail.html', {'note': note, 'root_comments': root_comments})

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

# AI-powered features
def strip_html(html_content):
    """Remove HTML tags from content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()

def use_gemini_summarization(content):
    """Use Google Gemini for smart summarization"""
    try:
        if not settings.GEMINI_API_KEY:
            return None
        
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        prompt = f"""Please summarize the following note content in 2-3 bullet points. 
Be concise and highlight the main ideas:

{content[:2000]}"""  # Limit to 2000 chars to stay within free tier limits
        
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        return None

def use_gemini_flashcards(content):
    """Use Google Gemini to generate flashcards"""
    try:
        if not settings.GEMINI_API_KEY:
            return None
        
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        prompt = f"""Create 5 flashcard Q&A pairs from this content. 
Return as JSON array with 'question' and 'answer' keys:

{content[:2000]}"""
        
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        try:
            # Extract JSON from response
            import json as json_module
            json_str = response.text
            if '```json' in json_str:
                json_str = json_str.split('```json')[1].split('```')[0]
            elif '```' in json_str:
                json_str = json_str.split('```')[1].split('```')[0]
            
            flashcards = json_module.loads(json_str)
            return flashcards if isinstance(flashcards, list) else None
        except:
            return None
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        return None

@login_required
def note_summarize(request, pk):
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    summary = None
    
    if request.method == 'POST':
        try:
            # Strip HTML from content
            plain_content = strip_html(note.content)
            
            # Try Gemini API first (if API key available)
            summary = use_gemini_summarization(plain_content)
            
            # Fallback to rule-based summarization if API fails or not configured
            if not summary:
                sentences = [s.strip() for s in plain_content.split('.') if len(s.strip()) > 20]
                
                # Get key sentences
                summary_sentences = []
                
                # Add first sentence
                if sentences:
                    summary_sentences.append(sentences[0])
                
                # Add longest sentences (likely most important)
                sorted_by_length = sorted(sentences[1:], key=len, reverse=True)
                for sent in sorted_by_length[:2]:
                    if sent not in summary_sentences:
                        summary_sentences.append(sent)
                
                # Format as bullet points
                summary = "• " + "\n• ".join(summary_sentences) if summary_sentences else "No content to summarize"
            
            # Track activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='view',
                note=note
            )
        except Exception as e:
            summary = f"Error generating summary: {str(e)}"
    
    return render(request, 'notes/note_summarize.html', {
        'note': note,
        'summary': summary
    })

@login_required
def generate_flashcards(request, pk):
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    success_message = None
    
    if request.method == 'POST':
        try:
            # Strip HTML from content
            plain_content = strip_html(note.content)
            
            flashcard_pairs = []
            
            # Try Gemini API first (if API key available)
            gemini_cards = use_gemini_flashcards(plain_content)
            
            if gemini_cards:
                # Create flashcards from Gemini response
                for card in gemini_cards:
                    if 'question' in card and 'answer' in card:
                        existing = Flashcard.objects.filter(
                            note=note,
                            question=card['question'],
                            answer=card['answer']
                        ).first()
                        
                        if not existing:
                            flashcard = Flashcard.objects.create(
                                note=note,
                                question=card['question'],
                                answer=card['answer']
                            )
                            flashcard_pairs.append(flashcard)
            else:
                # Fallback: Use rule-based flashcard generation
                sentences = [s.strip() for s in plain_content.split('.') if len(s.strip()) > 10]
                
                for i, sentence in enumerate(sentences[:5]):  # Create max 5 flashcards
                    # Extract first few words as the subject for the question
                    words = sentence.split()[:5]
                    subject = ' '.join(words)
                    
                    # Create simple Q&A
                    question = f"What is {subject}?"
                    answer = sentence.strip()
                    
                    # Check if flashcard already exists to avoid duplicates
                    existing = Flashcard.objects.filter(
                        note=note,
                        question=question,
                        answer=answer
                    ).first()
                    
                    if not existing:
                        flashcard = Flashcard.objects.create(
                            note=note,
                            question=question,
                            answer=answer
                        )
                        flashcard_pairs.append(flashcard)
            
            if flashcard_pairs:
                success_message = f"Generated {len(flashcard_pairs)} flashcards successfully!"
            else:
                success_message = "Flashcards already exist for this note."
            
            # Track activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='create',
                note=note
            )
        except Exception as e:
            success_message = f"Note: Could not generate all flashcards ({str(e)})"
    
    # Get existing flashcards
    existing_flashcards = note.flashcards.all()
    
    return render(request, 'notes/flashcards.html', {
        'note': note,
        'flashcards': existing_flashcards,
        'success_message': success_message
    })

@login_required
def view_flashcards(request, pk):
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    flashcards = note.flashcards.all()
    
    return render(request, 'notes/flashcards_view.html', {
        'note': note,
        'flashcards': flashcards
    })

@login_required
def share_note(request, pk):
    """Share a note with another user"""
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        can_edit = request.POST.get('can_edit') == 'on'
        
        try:
            shared_with = User.objects.get(username=username)
            
            if shared_with == request.user:
                messages.error(request, "You cannot share a note with yourself.")
            else:
                shared_note, created = SharedNote.objects.get_or_create(
                    note=note,
                    shared_with=shared_with,
                    defaults={'shared_by': request.user, 'can_edit': can_edit}
                )
                
                if not created:
                    shared_note.can_edit = can_edit
                    shared_note.save()
                    messages.info(request, f"Updated sharing permissions for {username}.")
                else:
                    messages.success(request, f"Note shared with {username} successfully!")
                
                # Log activity
                UserActivity.objects.create(
                    user=request.user,
                    note=note,
                    activity_type='share'
                )
                
        except User.DoesNotExist:
            messages.error(request, f"User '{username}' not found.")
    
    # Get current shares
    shared_with_users = SharedNote.objects.filter(note=note).select_related('shared_with')
    
    return render(request, 'notes/share_note.html', {
        'note': note,
        'shared_with_users': shared_with_users
    })

@login_required
def unshare_note(request, pk, user_id):
    """Remove sharing access from a user"""
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    SharedNote.objects.filter(note=note, shared_with_id=user_id).delete()
    messages.success(request, "Sharing removed successfully.")
    return redirect('share_note', pk=pk)

@login_required
def shared_notes_list(request):
    """List all notes shared with the current user"""
    shared_notes = SharedNote.objects.filter(shared_with=request.user).select_related('note', 'shared_by')
    
    return render(request, 'notes/shared_notes_list.html', {
        'shared_notes': shared_notes
    })

@login_required
def add_comment(request, pk):
    """Add a comment to a note"""
    note = get_object_or_404(Note, pk=pk)
    
    # Check if user has access to the note
    if note.owner != request.user and not SharedNote.objects.filter(note=note, shared_with=request.user).exists():
        messages.error(request, "You don't have permission to comment on this note.")
        return redirect('note_list')
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')
        
        if content:
            parent = None
            if parent_id:
                parent = Comment.objects.filter(id=parent_id, note=note).first()
            
            Comment.objects.create(
                note=note,
                user=request.user,
                content=content,
                parent=parent
            )
            
            # Log activity
            UserActivity.objects.create(
                user=request.user,
                note=note,
                activity_type='comment'
            )
            
            messages.success(request, "Comment added successfully!")
        else:
            messages.error(request, "Comment cannot be empty.")
    
    return redirect('note_detail', pk=pk)

@login_required
def delete_comment(request, pk, comment_id):
    """Delete a comment"""
    note = get_object_or_404(Note, pk=pk)
    comment = get_object_or_404(Comment, id=comment_id, note=note)
    
    # Only comment author or note owner can delete
    if comment.user == request.user or note.owner == request.user:
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
    else:
        messages.error(request, "You don't have permission to delete this comment.")
    
    return redirect('note_detail', pk=pk)

@login_required
def export_note_pdf(request, pk):
    """Export a note as PDF"""
    note = get_object_or_404(Note, pk=pk)
    
    # Check if user has access to the note
    if note.owner != request.user and not SharedNote.objects.filter(note=note, shared_with=request.user).exists():
        messages.error(request, "You don't have permission to export this note.")
        return redirect('note_list')
    
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{note.title}.pdf"'
    
    # Create the PDF object using ReportLab
    doc = SimpleDocTemplate(response, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#1E40AF',
        spaceAfter=12,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#4B5563',
        spaceAfter=6,
    )
    
    # Add title
    story.append(Paragraph(note.title, title_style))
    story.append(Spacer(1, 0.2 * inch))
    
    # Add metadata
    metadata = f"Course: {note.topic.course.name} | Topic: {note.topic.name}"
    story.append(Paragraph(metadata, styles['Normal']))
    story.append(Spacer(1, 0.1 * inch))
    
    created_info = f"Created: {note.created_at.strftime('%B %d, %Y')} | Updated: {note.updated_at.strftime('%B %d, %Y')}"
    story.append(Paragraph(created_info, styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))
    
    # Add content (strip HTML and convert to plain text)
    content = strip_html(note.content)
    # Split content into paragraphs
    paragraphs = content.split('\n')
    for para in paragraphs:
        if para.strip():
            story.append(Paragraph(para, styles['BodyText']))
            story.append(Spacer(1, 0.1 * inch))
    
    # Build PDF
    doc.build(story)
    
    return response

@login_required
def export_note_markdown(request, pk):
    """Export a note as Markdown"""
    note = get_object_or_404(Note, pk=pk)
    
    # Check if user has access to the note
    if note.owner != request.user and not SharedNote.objects.filter(note=note, shared_with=request.user).exists():
        messages.error(request, "You don't have permission to export this note.")
        return redirect('note_list')
    
    # Create Markdown content
    md_content = f"# {note.title}\n\n"
    md_content += f"**Course:** {note.topic.course.name}\n"
    md_content += f"**Topic:** {note.topic.name}\n"
    md_content += f"**Created:** {note.created_at.strftime('%B %d, %Y')}\n"
    md_content += f"**Updated:** {note.updated_at.strftime('%B %d, %Y')}\n\n"
    
    # Add tags
    if note.tags.exists():
        tags = ", ".join([tag.name for tag in note.tags.all()])
        md_content += f"**Tags:** {tags}\n\n"
    
    md_content += "---\n\n"
    
    # Add content (strip HTML)
    content = strip_html(note.content)
    md_content += content
    
    # Create the HttpResponse object with Markdown headers
    response = HttpResponse(md_content, content_type='text/markdown')
    response['Content-Disposition'] = f'attachment; filename="{note.title}.md"'
    
    return response

@login_required
def voice_notes(request, pk):
    """View and manage voice notes for a note"""
    note = get_object_or_404(Note, pk=pk)
    
    # Check if user has access to the note
    if note.owner != request.user and not SharedNote.objects.filter(note=note, shared_with=request.user).exists():
        messages.error(request, "You don't have permission to access this note.")
        return redirect('note_list')
    
    # Handle file upload
    if request.method == 'POST' and request.FILES.get('audio_file'):
        audio_file = request.FILES['audio_file']
        voice_note = VoiceNote.objects.create(
            note=note,
            audio_file=audio_file
        )
        
        # Log activity
        UserActivity.objects.create(
            user=request.user,
            note=note,
            activity_type='edit'  # Using edit as general activity
        )
        
        messages.success(request, "Voice note uploaded successfully!")
        return redirect('voice_notes', pk=pk)
    
    voice_notes_list = note.voice_notes.all().order_by('-created_at')
    
    return render(request, 'notes/voice_notes.html', {
        'note': note,
        'voice_notes': voice_notes_list
    })

@login_required
def delete_voice_note(request, pk, voice_note_id):
    """Delete a voice note"""
    note = get_object_or_404(Note, pk=pk, owner=request.user)
    voice_note = get_object_or_404(VoiceNote, id=voice_note_id, note=note)
    
    # Delete the file
    if voice_note.audio_file:
        voice_note.audio_file.delete()
    
    voice_note.delete()
    messages.success(request, "Voice note deleted successfully.")
    return redirect('voice_notes', pk=pk)

@login_required
def analytics_dashboard(request):
    """Analytics dashboard showing study statistics"""
    user = request.user
    
    # Date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Basic stats
    total_notes = Note.objects.filter(owner=user).count()
    total_courses = Course.objects.filter(owner=user).count()
    total_topics = Topic.objects.filter(owner=user).count()
    total_flashcards = Flashcard.objects.filter(note__owner=user).count()
    
    # Activity stats
    notes_this_week = Note.objects.filter(owner=user, created_at__gte=week_ago).count()
    notes_this_month = Note.objects.filter(owner=user, created_at__gte=month_ago).count()
    
    # Recent activity
    recent_activities = UserActivity.objects.filter(user=user).select_related('note').order_by('-timestamp')[:10]
    
    # Study sessions (mock data for now)
    total_study_time = StudySession.objects.filter(user=user).aggregate(
        total=Sum('duration_minutes')
    )['total'] or 0
    
    # Most active courses
    active_courses = Course.objects.filter(owner=user).annotate(
        note_count=Count('topics__notes', filter=Q(topics__notes__owner=user))
    ).order_by('-note_count')[:5]
    
    # Activity by type
    activity_counts = UserActivity.objects.filter(user=user).values('activity_type').annotate(
        count=Count('id')
    )
    
    # Prepare data for charts
    activity_labels = [act['activity_type'].title() for act in activity_counts]
    activity_data = [act['count'] for act in activity_counts]
    
    # Notes created over last 7 days
    daily_notes = []
    daily_labels = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = Note.objects.filter(owner=user, created_at__date=day).count()
        daily_notes.append(count)
        daily_labels.append(day.strftime('%a'))
    
    context = {
        'total_notes': total_notes,
        'total_courses': total_courses,
        'total_topics': total_topics,
        'total_flashcards': total_flashcards,
        'notes_this_week': notes_this_week,
        'notes_this_month': notes_this_month,
        'recent_activities': recent_activities,
        'total_study_time': total_study_time,
        'active_courses': active_courses,
        'activity_labels': json.dumps(activity_labels),
        'activity_data': json.dumps(activity_data),
        'daily_labels': json.dumps(daily_labels),
        'daily_notes': json.dumps(daily_notes),
    }
    
    return render(request, 'notes/analytics_dashboard.html', context)
