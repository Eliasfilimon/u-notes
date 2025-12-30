import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'unotes_project.settings')
import django
django.setup()
from django.contrib.auth.models import User

admin = User.objects.get(username='admin')
admin.set_password('password123')
admin.is_staff = True
admin.is_superuser = True
admin.save()
print('Admin password reset to: password123')
print('Admin is_staff:', admin.is_staff)
print('Admin is_superuser:', admin.is_superuser)
