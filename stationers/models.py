import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
import logging
import re

from thefuzz import fuzz

logger = logging.getLogger(__name__)


def _create_match(entry, matched_entry, is_register_entry, match_type, score):
    """
    Helper function to create a Match object.
    """
    if is_register_entry:
        entries_dict = {
            'register_entry': entry,
            'library_entry': matched_entry,
            'score': score
        }
    else:
        entries_dict = {
            'register_entry': matched_entry,
            'library_entry': entry,
            'score': score
        }
    MatchCandidate.objects.get_or_create(match_type=match_type, **entries_dict)


def remove_metadata(title_string: str) -> str:
    square_brackets_clean = re.sub(
        r'\[(?:microform|illustrated|a novel|plates)\]', '',
        title_string.lower())
    editions_clean = re.sub(r'\b(?:n|ed|vol(?:s|ume|umes|))\b', '',
                            square_brackets_clean)
    return re.sub(r'\d{1,4}', '', editions_clean)


def clean_title_string(title_string: str) -> str:
    no_ampersand = re.sub(r'(&amp;|&)', 'and', title_string)
    no_apostrophe = re.sub(r"['`]", '', no_ampersand)
    alphanum = re.sub(r'[^a-zA-Z0-9]', ' ', no_apostrophe)
    single_spaced = re.sub(r'\s{2,}', ' ', alphanum)
    return single_spaced.strip().lower()


def search_for_match(entry, collection_class):
    """
    Finds and creates matches for a given entry in a collection.
    """
    start = datetime.datetime.now()
    logger.debug(f"Search for {entry} match starts: {start}")
    registers = []
    is_register_entry = True

    if isinstance(entry, LibraryEntry):
        registers.extend(entry.register.all())
        is_register_entry = False
    elif isinstance(entry, RegisterEntry):
        registers.append(entry.register)

    clean_entry_title = clean_title_string(remove_metadata(entry.title))
    for register in registers:
        relevant_entries = collection_class.objects.filter(
            register=register.id)
        scores = [{
            "id":
            collection_entry.id,
            "title_score":
            fuzz.ratio(
                clean_entry_title,
                clean_title_string(remove_metadata(collection_entry.title)))
        } for collection_entry in relevant_entries]

        # Find entries with the same string in each title
        matched_titles = list(filter(lambda s: s["title_score"] == 100,
                                     scores))

        for matched_entry in matched_titles:
            _create_match(entry, relevant_entries.get(pk=matched_entry["id"]),
                          is_register_entry, "EXC",
                          matched_entry["title_score"])

        # Find entries with similar title
        unmatched_titles = list(
            filter(lambda s: s not in matched_titles, scores))
        match_threshold = 65
        fuzzy_titles = list(
            filter(lambda s: s["title_score"] > match_threshold,
                   unmatched_titles))
        for matched_entry in fuzzy_titles:
            _create_match(entry, relevant_entries.get(pk=matched_entry["id"]),
                          is_register_entry, "FUZ",
                          matched_entry["title_score"])
        logger.debug(f"Entry: {clean_entry_title}")
        logger.debug(f"Relevant collection entries: {len(relevant_entries)}")
        logger.debug(f"Matched titles: {len(matched_titles)}")
        logger.debug(f"Unmatched titles: {len(unmatched_titles)}")
        logger.debug(f"fuzzy titles: {len(fuzzy_titles)}")

        end = datetime.datetime.now()
        logger.debug(f"Search for {entry} match ends: {end}")
        logger.debug(f"Search for {entry} match takes: {end - start}")


class Register(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField("register start date", null=True, blank=True)
    end_date = models.DateField("register end date", null=True, blank=True)
    pages = models.IntegerField(default=0)
    file = models.FileField(upload_to="register_pdfs", blank=True, null=True)

    def __str__(self):
        return self.name


class LibraryEntry(models.Model):

    class Library(models.TextChoices):
        BODLEIAN_LIBRARY = "BDL", _("Bodleian Library")
        BRITISH_LIBRARY = "BTL", _("British Library")
        CAMBRIDGE_LIBRARY = "CAL", _("Cambridge Library")
        SCOTLAND_LIBRARY = "NLS", _("National Library of Scotland")
        TRINITY_LIBRARY = "TCD", _("Trinity College Dublin Library")

    source_library = models.CharField(max_length=3,
                                      choices=Library,
                                      default=Library.BRITISH_LIBRARY)
    title = models.CharField(max_length=500)
    register = models.ManyToManyField(Register)
    min_date = models.DateField("earliest date of entry",
                                blank=True,
                                null=True)
    max_date = models.DateField("latest date of entry", blank=True, null=True)
    creator = models.CharField(max_length=100, blank=True, null=True)
    clean_title = models.CharField(max_length=500, blank=True, null=True)
    artifact_type = models.CharField(max_length=100, blank=True, null=True)
    publisher = models.CharField(max_length=500, blank=True, null=True)
    date_string = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=100, blank=True)
    artifact_format = models.CharField(max_length=100, blank=True)
    relation = models.CharField(max_length=500, blank=True, null=True)
    rights = models.CharField(max_length=500, blank=True, null=True)
    identifier = models.CharField(max_length=500, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    subject = models.CharField(max_length=500, blank=True, null=True)
    coverage = models.CharField(max_length=500, blank=True, null=True)
    contributor = models.CharField(max_length=500, blank=True, null=True)
    source = models.CharField(max_length=500, blank=True, null=True)
    volumes = models.CharField(max_length=100, blank=True)
    edition = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.source_library}: {self.title}"


class RegisterEntry(models.Model):

    register = models.ForeignKey(Register, on_delete=models.CASCADE)
    date = models.DateField("date of entry", blank=True, null=True)
    publisher = models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=1000)
    clean_title = models.CharField(max_length=1000, blank=True, null=True)
    volumes = models.CharField(max_length=100, blank=True, null=True)
    edition = models.CharField(max_length=100, blank=True, null=True)
    block = models.IntegerField(blank=True, null=True)
    page = models.IntegerField(blank=True, null=True)
    line = models.IntegerField(blank=True, null=True)
    creator = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return f"{self.publisher}: {self.title}"


class MatchCandidate(models.Model):

    class MatchType(models.TextChoices):
        EXACT = "EXC", _("Exact match")
        PARTIAL = "PAR", _("Partial match")
        FUZZY = "FUZ", _("Fuzzy match")
        FUZPA = "FZP", _("Fuzzy partial match")

    class MatchConfirmed(models.TextChoices):
        NOT = "NOT", _("Not confirmed")
        YES = "YES", _("Confirmed")
        REJECTED = "REJ", _("Rejected")

    match_type = models.CharField(max_length=3, choices=MatchType, null=True)
    register_entry = models.ForeignKey(RegisterEntry, on_delete=models.CASCADE)
    library_entry = models.ForeignKey(LibraryEntry,
                                      on_delete=models.CASCADE,
                                      null=True)
    score = models.IntegerField(default=0)
    match_confirmed = models.CharField(max_length=3,
                                       choices=MatchConfirmed,
                                       default=MatchConfirmed.NOT)

    def __str__(self):
        return (f"{self.register_entry} | {self.library_entry} |"
                f"{self.library_entry.source_library}")
