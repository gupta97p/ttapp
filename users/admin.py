from django.contrib import admin
from .models import user_reg
from django.contrib.auth.admin import UserAdmin


class user_reqAdmin(UserAdmin):
    # list_filter = UserAdmin.list_filter + ('email',)
    list_display_links = ('username', 'email', 'first_name')
    list_display = ('username', 'email', "first_name", 'last_name', 'rank', 'match_played', 'match_won')
    save_as = True
    search_fields = ('username',)

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(super().get_fieldsets(request, obj))
        if obj:
            list_display = ('first_name', 'last_name')
            fieldsets.append(('extra', {'classes': ('collapse',), 'fields': ('age', ('first_name', 'last_name',), 'gender', 'image', 'mobile', 'match_played', 'match_won', 'rank')}))
        return fieldsets

    class Meta:
        model = user_reg

admin.site.register(user_reg,user_reqAdmin)
