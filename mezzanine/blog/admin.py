
from copy import deepcopy

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from mezzanine.blog.models import BlogPost, BlogCategory
from mezzanine.conf import settings
from mezzanine.core.admin import DisplayableAdmin, OwnableAdmin


blogpost_fieldsets = deepcopy(DisplayableAdmin.fieldsets)
blogpost_fieldsets[0][1]["fields"].insert(1, "user")
blogpost_fieldsets[0][1]["fields"].insert(1, "categories")
blogpost_fieldsets[0][1]["fields"].extend(["content", "allow_comments"])
blogpost_list_display = ["title", "user", "category", "status", "admin_link"]
if settings.BLOG_USE_FEATURED_IMAGE:
    blogpost_fieldsets[0][1]["fields"].insert(-2, "featured_image")
    blogpost_list_display.insert(0, "admin_thumb")
blogpost_fieldsets = list(blogpost_fieldsets)
blogpost_fieldsets.insert(1, (_("Other posts"), {
    "classes": ("collapse-closed",),
    "fields": ("related_posts",)}))


class BlogPostAdmin(DisplayableAdmin, OwnableAdmin):
    """
    Admin class for blog posts.
    """

    fieldsets = blogpost_fieldsets
    list_display = blogpost_list_display
    filter_horizontal = ("categories", "related_posts",)

    def save_form(self, request, form, change):
        """
        Super class ordering is important here - user must get saved first.
        """
        OwnableAdmin.save_form(self, request, form, change)
        return DisplayableAdmin.save_form(self, request, form, change)

    def get_fieldsets(self, request, obj=None):
        if self.declared_fieldsets:
            if not request.user.is_superuser:
              fieldsets = deepcopy(self.declared_fieldsets)
              fields = fieldsets[0][1]['fields']
              if 'user' in fields:
                del fields[fields.index('user')]
                fieldsets[0][1]['fields'] = fields
              return fieldsets
            else:
              return self.declared_fieldsets
        form = self.get_formset(request).form
        return [(None, {'fields': form.base_fields.keys()})]

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = []
        if not request.user.is_superuser:
            self.exclude = ('user', )
        return super(BlogPostAdmin, self).get_form(request, obj, **kwargs)
    
class BlogCategoryAdmin(admin.ModelAdmin):
    """
    Admin class for blog categories. Hides itself from the admin menu
    unless explicitly specified.
    """

    fieldsets = ((None, {"fields": ("title",)}),)

    def in_menu(self):
        """
        Hide from the admin menu unless explicitly set in ``ADMIN_MENU_ORDER``.
        """
        for (name, items) in settings.ADMIN_MENU_ORDER:
            if "blog.BlogCategory" in items:
                return True
        return False


admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(BlogCategory, BlogCategoryAdmin)
