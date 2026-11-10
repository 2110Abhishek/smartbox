from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Administrator"
    WAREHOUSE_MANAGER = "WAREHOUSE_MANAGER", "Warehouse Manager"
    WAREHOUSE_STAFF = "WAREHOUSE_STAFF", "Warehouse Staff"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(
        max_length=32,
        choices=UserRole.choices,
        default=UserRole.WAREHOUSE_STAFF
    )
    phone_number = models.CharField(max_length=32, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN or self.user.is_superuser

    @property
    def is_manager(self):
        return self.role in [UserRole.ADMIN, UserRole.WAREHOUSE_MANAGER] or self.user.is_superuser


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        role = UserRole.ADMIN if instance.is_superuser else UserRole.WAREHOUSE_STAFF
        UserProfile.objects.create(user=instance, role=role)
    else:
        if hasattr(instance, "profile"):
            instance.profile.save()
