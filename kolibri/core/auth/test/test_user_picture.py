import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from kolibri.core.auth.constants import role_kinds
from kolibri.core.auth.models import Classroom
from kolibri.core.auth.models import Facility
from kolibri.core.auth.models import FacilityUser
from kolibri.core.auth.models import Membership
from kolibri.core.auth.models import Role
from kolibri.core.auth.test.helpers import create_superuser


class UserPictureUploadTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.facility = Facility.objects.create(name="Picture Test Facility")
        cls.superuser = create_superuser(cls.facility)

        cls.admin = FacilityUser.objects.create(
            username="facility_admin",
            facility=cls.facility,
        )
        Role.objects.create(
            user=cls.admin,
            collection=cls.facility,
            kind=role_kinds.ADMIN,
        )

        cls.coach = FacilityUser.objects.create(
            username="class_coach",
            facility=cls.facility,
        )
        cls.classroom = Classroom.objects.create(
            name="Class 1",
            parent=cls.facility,
        )
        Role.objects.create(
            user=cls.coach,
            collection=cls.classroom,
            kind=role_kinds.COACH,
        )

        cls.student = FacilityUser.objects.create(
            username="student_1",
            facility=cls.facility,
        )
        Membership.objects.create(
            user=cls.student,
            collection=cls.classroom,
        )

        cls.other_student = FacilityUser.objects.create(
            username="student_2",
            facility=cls.facility,
        )

    def test_upload_picture_as_admin_succeeds(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse(
            "kolibri:core:facilityuser-upload-picture", kwargs={"pk": self.student.id}
        )

        fake_image = io.BytesIO(b"fake image data content")
        uploaded_file = SimpleUploadedFile(
            "avatar.png", fake_image.read(), content_type="image/png"
        )

        response = self.client.post(
            url,
            {"file": uploaded_file},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("picture", response.data)
        self.assertTrue(response.data["picture"].startswith("/media/user_photos/"))

        self.student.refresh_from_db()
        self.assertEqual(self.student.picture, response.data["picture"])

    def test_coach_can_upload_picture_for_enrolled_student(self):
        self.client.force_authenticate(user=self.coach)
        url = reverse(
            "kolibri:core:facilityuser-upload-picture", kwargs={"pk": self.student.id}
        )

        fake_image = io.BytesIO(b"coach uploaded avatar")
        uploaded_file = SimpleUploadedFile(
            "student_avatar.jpg", fake_image.read(), content_type="image/jpeg"
        )

        response = self.client.post(
            url,
            {"file": uploaded_file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertTrue(self.student.picture.startswith("/media/user_photos/"))

    def test_coach_cannot_upload_picture_for_unenrolled_student(self):
        self.client.force_authenticate(user=self.coach)
        url = reverse(
            "kolibri:core:facilityuser-upload-picture",
            kwargs={"pk": self.other_student.id},
        )

        fake_image = io.BytesIO(b"coach upload attempt")
        uploaded_file = SimpleUploadedFile(
            "avatar.png", fake_image.read(), content_type="image/png"
        )

        response = self.client.post(
            url,
            {"file": uploaded_file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_learner_can_upload_own_picture_when_permitted(self):
        self.facility.dataset.learner_can_edit_name = True
        self.facility.dataset.save()

        self.client.force_authenticate(user=self.student)
        url = reverse(
            "kolibri:core:facilityuser-upload-picture", kwargs={"pk": self.student.id}
        )

        fake_image = io.BytesIO(b"learner self upload")
        uploaded_file = SimpleUploadedFile(
            "my_face.png", fake_image.read(), content_type="image/png"
        )

        response = self.client.post(
            url,
            {"file": uploaded_file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertTrue(self.student.picture.startswith("/media/user_photos/"))

    def test_learner_cannot_upload_own_picture_when_forbidden(self):
        self.facility.dataset.learner_can_edit_name = False
        self.facility.dataset.learner_can_edit_username = False
        self.facility.dataset.save()

        self.client.force_authenticate(user=self.student)
        url = reverse(
            "kolibri:core:facilityuser-upload-picture", kwargs={"pk": self.student.id}
        )

        fake_image = io.BytesIO(b"learner forbidden self upload")
        uploaded_file = SimpleUploadedFile(
            "my_face.png", fake_image.read(), content_type="image/png"
        )

        response = self.client.post(
            url,
            {"file": uploaded_file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_rejects_unsupported_file_extension(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse(
            "kolibri:core:facilityuser-upload-picture", kwargs={"pk": self.student.id}
        )

        uploaded_file = SimpleUploadedFile(
            "malicious.exe", b"not an image", content_type="application/octet-stream"
        )

        response = self.client.post(
            url,
            {"file": uploaded_file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Unsupported image file extension", response.data.get("detail", "")
        )

    def test_upload_rejects_oversized_file(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse(
            "kolibri:core:facilityuser-upload-picture", kwargs={"pk": self.student.id}
        )

        oversized_file = SimpleUploadedFile(
            "big.png", b"x" * (5 * 1024 * 1024 + 100), content_type="image/png"
        )

        response = self.client.post(
            url,
            {"file": oversized_file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("exceeds the 5MB maximum limit", response.data.get("detail", ""))

    def test_delete_picture_as_admin_succeeds(self):
        self.student.picture = "/media/user_photos/dummy.png"
        self.student.save()

        self.client.force_authenticate(user=self.admin)
        url = reverse(
            "kolibri:core:facilityuser-delete-picture", kwargs={"pk": self.student.id}
        )

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["picture"])

        self.student.refresh_from_db()
        self.assertIsNone(self.student.picture)

    def test_serializer_includes_picture_field(self):
        self.student.picture = "/media/user_photos/avatar123.png"
        self.student.save()

        self.client.force_authenticate(user=self.admin)
        url = reverse(
            "kolibri:core:facilityuser-detail", kwargs={"pk": self.student.id}
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get("picture"), "/media/user_photos/avatar123.png"
        )
