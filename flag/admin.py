from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.core import urlresolvers

from flag.models import FlaggedContent, FlagInstance

_absolute_url_resolvers = {}
_group_to_flag_type = {}


def register_absolute_url_resolver(model_class, func):
    _absolute_url_resolvers[model_class] = func


def register_group_to_flag_types(*mappings):
    _group_to_flag_type.update(mappings)


def flagged_object_link(model):
    content = getattr(model, 'flagged_content', model)
    obj = content.content_object
    url = obj.get_absolute_url() if hasattr(obj, 'get_absolute_url') else None
    if not url:
        resolver = _absolute_url_resolvers.get(type(obj), None)
        if resolver:
            url = resolver(obj)
    if not url: return ''
    return "<a href='%s'>%s</a>" % (url, obj._meta.verbose_name)
flagged_object_link.short_description = 'The Flagged Item'
flagged_object_link.allow_tags = True


def user_link(flag_instance):
    user = flag_instance.user
    return "<a href='%s'>%s</a>" % (user.get_absolute_url(), user.username)
user_link.short_description = 'User'
user_link.allow_tags = True


def flagged_content_link(flag_instance):
    url = urlresolvers.reverse("admin:flag_flaggedcontent_change",
                    args=(flag_instance.flagged_content.id,))
    return "<a href='%s'>%s</a>" % (url, 'Admin Link')
flagged_content_link.short_description = 'Flagged Content'
flagged_content_link.allow_tags = True


class InlineFlagInstance(admin.TabularInline):
    readonly_fields = ('user', 'flag_type', 'comment', 'when_added', 'when_recalled')
    model = FlagInstance
    extra = 0


class FlaggedContentForm(forms.ModelForm):
    moderator = forms.ModelChoiceField(queryset=
        User.objects.filter(groups__name__in=_group_to_flag_type.keys()))
    class Meta:
        model = FlaggedContent


class FlaggedContentAdmin(admin.ModelAdmin):
    form = FlaggedContentForm
    exclude = ('content_type', 'object_id')
    readonly_fields = ('creator', 'count')
    inlines = [InlineFlagInstance]


class FlagInstanceAdmin(admin.ModelAdmin):
    ordering = ('-when_added', )
    list_display = ('pk', flagged_content_link, user_link, 'when_recalled',
                    'when_added', 'comment', 'flag_type', flagged_object_link)
    list_filter = ('flag_type',)

    def queryset(self, request):
        qs = super(FlagInstanceAdmin, self).queryset(request)
        groups = request.user.groups.values_list('name', flat=True)
        for group, flag_type in _group_to_flag_type.items():
            if group in groups:
                qs = qs.filter(flag_type=flag_type)
        return qs


admin.site.register(FlaggedContent, FlaggedContentAdmin)
admin.site.register(FlagInstance, FlagInstanceAdmin)
