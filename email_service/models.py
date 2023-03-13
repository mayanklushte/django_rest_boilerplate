import uuid

# Third Party Stuff
from django.db import models
from django.utils.translation import gettext_lazy as _



class EmailService(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    security_code = models.CharField(
        _("Security Code"), null=True, max_length=120)
    email = models.EmailField()
    session_token = models.CharField(_("Device Session Token"), max_length=500)
    is_verified = models.BooleanField(
        _("Security Code Verified"), default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        db_table = "email_service"
        verbose_name = _("Email Service")
        verbose_name_plural = _("Email Services")
        ordering = ("-modified_at",)
        unique_together = ("email", "session_token")

    def __str__(self):
        return "{}: {}".format(str(self.email), self.security_code)
