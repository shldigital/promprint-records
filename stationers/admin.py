import datetime
from django.contrib import admin
import logging
from .models import (Register, RegisterEntry, LibraryEntry, MatchCandidate,
                     search_for_match)
from import_export.admin import ImportExportModelAdmin
from import_export import fields, resources, widgets

logger = logging.getLogger(__name__)


def redo_match_search(modeladmin, request, queryset):
    start = datetime.datetime.now()
    for register in queryset:
        entries = RegisterEntry.objects.filter(register=register.id)
        for entry in entries:
            search_for_match(entry, LibraryEntry)

    end = datetime.datetime.now()
    logger.info(f"match search process takes: {end - start}")


redo_match_search.short_description = "Redo match search on each entry" \
                                      " in selected registers"


def delete_all(modeladmin, request, queryset):
    queryset.delete()


class RegisterAdmin(admin.ModelAdmin):
    list_display = ["name", "pages", "file", "_entry_count"]
    actions = [redo_match_search]

    def _entry_count(self, obj):
        return obj.registerentry_set.count()

    _entry_count.short_description = "Entry Count"


class MatchInline(admin.TabularInline):
    model = MatchCandidate
    extra = 1


class RegisterEntryResource(resources.ModelResource):
    register = fields.Field(column_name='register',
                            attribute='register',
                            widget=widgets.ForeignKeyWidget(Register,
                                                            field='name'))

    class Meta:
        skip_unchanged = True
        report_skipped = False
        fields = ('id', 'register', 'date', 'creator', 'title')
        model = RegisterEntry


class RegisterEntryAdmin(ImportExportModelAdmin):
    resource_classes = [RegisterEntryResource]
    inlines = [MatchInline]
    list_display = [
        "title", "creator", "date", "register", "_match_count", "_has_match"
    ]
    list_filter = ["register", "matchcandidate__match_confirmed"]
    search_fields = ["title", "creator"]

    def _match_count(self, obj):
        return obj.matchcandidate_set.count()

    @admin.display(boolean=True)
    def _has_match(self, obj):
        matched = list(
            filter(lambda m: m.match_confirmed == m.MatchConfirmed.YES,
                   obj.matchcandidate_set.all()))
        return len(matched) > 0

    _match_count.short_description = "Match Candidate Count"


class LibraryEntryResource(resources.ModelResource):
    register = fields.Field(column_name='register',
                            attribute='register',
                            widget=widgets.ManyToManyWidget(Register,
                                                            field='name',
                                                            separator='|'))

    class Meta:
        skip_unchanged = True
        report_skipped = False
        fields = ('id', 'source_library', 'register', 'min_date', 'max_date',
                  'creator', 'title')
        model = LibraryEntry


class LibraryEntryAdmin(ImportExportModelAdmin):
    resource_classes = [LibraryEntryResource]
    inlines = [MatchInline]
    list_display = [
        "title", "creator", "min_date", "max_date", "source_library"
    ]
    list_filter = ["source_library"]
    search_fields = ["title", "creator"]


class MatchResource(resources.ModelResource):

    class Meta:
        skip_unchanged = True
        report_skipped = False
        fields = ('match_type', 'score', 'register_entry__title',
                  'library_entry__title')
        model = MatchCandidate


class MatchAdmin(ImportExportModelAdmin):
    actions = [delete_all]
    resource_classes = [MatchResource]
    list_display = [
        "match_type", "score", "register_entry__title", "library_entry__title",
        "register_entry__creator", "library_entry__creator",
        "register_entry__register", "library_entry__source_library",
        "match_confirmed"
    ]
    list_filter = [
        "score", "register_entry__register", "library_entry__source_library",
        "match_type", "match_confirmed"
    ]
    search_fields = [
        "register_entry__title", "register_entry__creator",
        "library_entry__title", "library_entry__creator"
    ]


admin.site.register(Register, RegisterAdmin)
admin.site.register(RegisterEntry, RegisterEntryAdmin)
admin.site.register(LibraryEntry, LibraryEntryAdmin)
admin.site.register(MatchCandidate, MatchAdmin)
