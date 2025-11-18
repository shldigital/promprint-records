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


class RegisterEntryImportResource(resources.ModelResource):
    register = fields.Field(column_name='register',
                            attribute='register',
                            widget=widgets.ForeignKeyWidget(Register,
                                                            field='name'))

    class Meta:
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ('register', 'publisher', 'title')
        fields = ('register', 'date', 'publisher', 'title', 'clean_title',
                  'block', 'page', 'line', 'creator')
        model = RegisterEntry


class RegisterEntryExportResource(resources.ModelResource):
    register = fields.Field(column_name='register',
                            attribute='register',
                            widget=widgets.ForeignKeyWidget(Register,
                                                            field='name'))

    class Meta:
        fields = ('id', 'register', 'date', 'publisher', 'title',
                  'clean_title', 'block', 'page', 'line', 'creator')
        model = RegisterEntry


class RegisterEntryAdmin(ImportExportModelAdmin):
    resource_classes = [
        RegisterEntryImportResource, RegisterEntryExportResource
    ]
    inlines = [MatchInline]
    list_display = [
        "title", "publisher", "creator", "register", "block", "page", "line",
        "_match_count", "_has_match"
    ]
    list_filter = ["register", "matchcandidate__match_confirmed"]
    search_fields = ["title", "publisher"]

    def _match_count(self, obj):
        return obj.matchcandidate_set.count()

    @admin.display(boolean=True)
    def _has_match(self, obj):
        matched = list(
            filter(lambda m: m.match_confirmed == m.MatchConfirmed.YES,
                   obj.matchcandidate_set.all()))
        return len(matched) > 0

    _match_count.short_description = "Match Candidate Count"


class LibraryEntryImportResource(resources.ModelResource):
    register = fields.Field(column_name='register',
                            attribute='register',
                            widget=widgets.ManyToManyWidget(Register,
                                                            field='name',
                                                            separator='|'))
    artifact_type_field = fields.Field(attribute='artifact_type',
                                       column_name='type')
    artifact_format_field = fields.Field(attribute='artifact_format',
                                         column_name='format')
    date_string_field = fields.Field(attribute='date_string',
                                     column_name='date')

    class Meta:
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ('source_library', 'creator', 'title')
        fields = ('title', 'clean_title', 'source_library', 'register',
                  'min_date', 'max_date', 'creator', 'artifact_type_field',
                  'publisher', 'date_string', 'language',
                  'artifact_format_field', 'relation', 'rights', 'identifier',
                  'description', 'subject', 'coverage', 'contributor',
                  'source')
        model = LibraryEntry


class LibraryEntryExportResource(resources.ModelResource):
    register = fields.Field(column_name='register',
                            attribute='register',
                            widget=widgets.ManyToManyWidget(Register,
                                                            field='name',
                                                            separator='|'))
    artifact_type_field = fields.Field(attribute='artifact_type',
                                       column_name='type')
    artifact_format_field = fields.Field(attribute='artifact_format',
                                         column_name='format')

    class Meta:
        fields = ('id', 'title', 'clean_title', 'source_library', 'register',
                  'min_date', 'max_date', 'creator', 'artifact_type_field',
                  'publisher', 'date_string', 'language',
                  'artifact_format_field', 'relation', 'rights', 'identifier',
                  'description', 'subject', 'coverage', 'contributor',
                  'source')
        model = LibraryEntry


class LibraryEntryAdmin(ImportExportModelAdmin):
    resource_classes = [LibraryEntryImportResource, LibraryEntryExportResource]
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
        "register_entry__publisher", "library_entry__creator",
        "register_entry__register", "library_entry__source_library",
        "match_confirmed"
    ]
    list_filter = [
        "score", "register_entry__register", "library_entry__source_library",
        "match_type", "match_confirmed"
    ]
    search_fields = [
        "register_entry__title", "register_entry__publisher",
        "library_entry__title", "library_entry__creator"
    ]


admin.site.register(Register, RegisterAdmin)
admin.site.register(RegisterEntry, RegisterEntryAdmin)
admin.site.register(LibraryEntry, LibraryEntryAdmin)
admin.site.register(MatchCandidate, MatchAdmin)
