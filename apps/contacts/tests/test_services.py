from unittest.mock import patch

from django.core import mail
from django.core.exceptions import ValidationError
from django.db import transaction
from django.test import TestCase, override_settings

from apps.contacts.models import Contact
from apps.contacts.services import EnquiryInput, notify_contact, submit_enquiry


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class EnquiryServiceTests(TestCase):
    def setUp(self):
        self.data = EnquiryInput(
            name="Visitor",
            email="visitor@example.com",
            subject="Hello",
            message="Saved first",
        )

    def test_notification_waits_for_commit_and_uses_persisted_enquiry(self):
        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            contact = submit_enquiry(data=self.data)
            self.assertTrue(Contact.objects.filter(pk=contact.pk).exists())
            self.assertEqual(contact.notification_status, "pending")
            self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(len(callbacks), 1)
        contact.refresh_from_db()
        self.assertEqual(contact.notification_status, "sent")
        self.assertEqual(mail.outbox[0].reply_to, [self.data.email])

    def test_rollback_discards_enquiry_and_notification(self):
        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            with self.assertRaises(RuntimeError), transaction.atomic():
                submit_enquiry(data=self.data)
                raise RuntimeError("rollback")
        self.assertEqual(callbacks, [])
        self.assertFalse(Contact.objects.exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_invalid_service_input_never_writes_or_sends(self):
        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            with self.assertRaises(ValidationError):
                submit_enquiry(
                    data=EnquiryInput(name="", email="invalid", subject="", message="")
                )
        self.assertFalse(Contact.objects.exists())
        self.assertEqual(callbacks, [])

    def test_transport_failure_is_durable_and_retryable(self):
        with patch(
            "apps.contacts.services.send_enquiry_notification",
            side_effect=OSError("offline"),
        ):
            with self.captureOnCommitCallbacks(execute=True):
                contact = submit_enquiry(data=self.data)
        contact.refresh_from_db()
        self.assertEqual(contact.notification_status, "failed")
        self.assertEqual(contact.message, "Saved first")
        self.assertEqual(notify_contact(contact), "sent")

    def test_zero_deliveries_are_failure(self):
        contact = Contact.objects.create(**self.data.__dict__)
        with patch(
            "apps.contacts.services.send_enquiry_notification", return_value=False
        ):
            self.assertEqual(notify_contact(contact), "failed")

    def test_invalid_email_header_keeps_enquiry_with_failed_delivery(self):
        data = EnquiryInput(
            name="Visitor",
            email="visitor@example.com",
            subject="Hello\nInjected header",
            message="Keep enquiry",
        )
        with self.captureOnCommitCallbacks(execute=True):
            contact = submit_enquiry(data=data)
        contact.refresh_from_db()
        self.assertEqual(contact.notification_status, "failed")
        self.assertEqual(len(mail.outbox), 0)
