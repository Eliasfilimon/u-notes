from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('notes/', views.note_list, name='note_list'),
    path('note/<int:pk>/', views.note_detail, name='note_detail'),
    path('course/<int:course_id>/', views.note_list, name='notes_by_course'),
    path('topic/<int:topic_id>/', views.note_list, name='notes_by_topic'),
    path('tag/<slug:tag_slug>/', views.note_list, name='notes_by_tag'),
    path('note/create/', views.note_create, name='note_create'),
    path('note/<int:pk>/update/', views.note_update, name='note_update'),
    path('note/<int:pk>/delete/', views.note_delete, name='note_delete'),
    path('signup/', views.signup, name='signup'),
    path('courses/', views.course_list, name='course_list'),
    path('course/new/', views.course_create, name='course_create'),
    path('course/<int:pk>/edit/', views.course_update, name='course_update'),
    path('course/<int:pk>/delete/', views.course_delete, name='course_delete'),
    path('topics/', views.topic_list, name='topic_list'),
    path('topic/new/', views.topic_create, name='topic_create'),
    path('topic/<int:pk>/edit/', views.topic_update, name='topic_update'),
    path('topic/<int:pk>/delete/', views.topic_delete, name='topic_delete'),
    path('profile/', views.profile, name='profile'),
    path('search/', views.search_results, name='search_results'),
    path('documents/', views.document_list, name='document_list'),
    path('documents/upload/', views.document_upload, name='document_upload'),
    path('documents/<int:pk>/', views.document_view, name='document_view'),
    path('documents/<int:pk>/delete/', views.document_delete, name='document_delete'),
]
