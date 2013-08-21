from django.contrib import admin

from flag.models import FlaggedContent, FlagInstance


class InlineFlagInstance(admin.TabularInline):
    model = FlagInstance
    extra = 0


class FlaggedContentAdmin(admin.ModelAdmin):
    inlines = [InlineFlagInstance]


def flagged_object_link(flag_instance):
    content = flag_instance.flagged_content
    obj = content.content_object
    print dir(obj._meta)
    return "<a href='%s'>%s</a>" % (obj.get_absolute_url(), obj._meta.verbose_name)
flagged_object_link.short_description = 'The Flagged Item'
flagged_object_link.allow_tags = True


class FlagInstanceAdmin(admin.ModelAdmin):
    list_display = ('user','comment','flag_type', flagged_object_link)
    list_filter = ('flag_type',)


admin.site.register(FlaggedContent, FlaggedContentAdmin)
admin.site.register(FlagInstance, FlagInstanceAdmin)
