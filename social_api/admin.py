from django.contrib import admin

from .models import Friendship, User

# Register your models here.
admin.site.register(User)
admin.site.register(Friendship)
