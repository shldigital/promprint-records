from django.test import TestCase
from .models import Register, RegisterEntry, LibraryEntry, MatchCandidate


class RegisterEntryTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        Register.objects.create(name="mock register")

    def setUp(self):
        self.register = Register.objects.get(id=1)
        self.entry = RegisterEntry.objects.create(register=self.register,
                                                  title="mock title")
        self.library_entry = LibraryEntry.objects.create(title="mock title")
        self.library_entry.register.set([self.register])

    def test_str_representation(self):
        full_entry = RegisterEntry.objects.create(register=self.register,
                                                  title="mock title",
                                                  publisher="mock publisher")
        self.assertEqual(str(full_entry), "mock publisher: mock title")

    def test_str_representation_with_no_publisher(self):
        self.assertEqual(str(self.entry), "None: mock title")

    def test_created_with_no_match_candidates(self):
        self.assertEqual(self.entry.match_candidate_count, 0)

    def test_new_match_increments_candidate_count(self):
        MatchCandidate.objects.create(register_entry=self.entry,
                                      library_entry=self.library_entry)
        self.assertEqual(self.entry.match_candidate_count, 1)

    def test_updated_match_does_not_increment_candidate_count(self):
        mc = MatchCandidate.objects.create(register_entry=self.entry,
                                           library_entry=self.library_entry)
        mc.score = 99
        mc.save()
        self.assertEqual(self.entry.match_candidate_count, 1)


class MatchCandidateTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        Register.objects.create(name="mock register")

    def setUp(self):
        self.register = Register.objects.get(id=1)
        self.entry = RegisterEntry.objects.create(register=self.register,
                                                  title="mock title")
