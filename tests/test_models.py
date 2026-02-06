"""Tests for domain models."""

from openfang.models import CronJob, User


def test_user_basic():
    user = User(id=1, email="test@example.com")
    assert user.id == 1
    assert user.email == "test@example.com"
    assert user.roles == set()
    assert user.org_id is None


def test_user_has_role():
    user = User(id=1, email="test@example.com", roles={"admin", "editor"})
    assert user.has_role("admin")
    assert user.has_role("editor")
    assert not user.has_role("viewer")


def test_user_is_admin():
    user = User(id=1, email="test@example.com")
    assert not user.is_admin

    admin = User(id=2, email="admin@example.com", roles={"admin"})
    assert admin.is_admin


def test_cronjob_basic():
    job = CronJob(id="job-1", schedule="* * * * *", task="echo hello")
    assert job.id == "job-1"
    assert job.schedule == "* * * * *"
    assert job.task == "echo hello"
    assert job.enabled is True
    assert job.created_by is None


def test_cronjob_disabled():
    job = CronJob(id="job-2", schedule="0 0 * * *", task="backup", enabled=False, created_by=42)
    assert not job.enabled
    assert job.created_by == 42
