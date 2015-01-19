from django.contrib import admin
from .models import Project, IDC, AssetType, Asset, AssetField, AssetFieldValue

# Register your models here.


class ProjectAdmin(admin.ModelAdmin):
    class Meta:
        model = Project

    list_display = ["name", "contact"]

admin.site.register(Project, ProjectAdmin)


class AssetTypeAdmin(admin.ModelAdmin):
    class Meta:
        model = AssetType

admin.site.register(AssetType, AssetTypeAdmin)


class AssetAdmin(admin.ModelAdmin):
    class Meta:
        model = Asset

admin.site.register(Asset, AssetAdmin)


class AssetFieldAdmin(admin.ModelAdmin):
    class Meta:
        model = AssetField

admin.site.register(AssetField, AssetAdmin)


class AssetFieldValueAdmin(admin.ModelAdmin):
    class Meta:
        model = AssetFieldValue

admin.site.register(AssetFieldValue, AssetAdmin)


class IDCAdmin(admin.ModelAdmin):
    class Meta:
        model = IDC

admin.site.register(IDC, IDCAdmin)
