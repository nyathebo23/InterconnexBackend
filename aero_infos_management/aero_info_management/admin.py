from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Aerodrome)
admin.site.register(Unit)
admin.site.register(LocalInformer)
admin.site.register(NationalInformer)
admin.site.register(Agent)
admin.site.register(LocalAgent)
admin.site.register(NationalAgent)
