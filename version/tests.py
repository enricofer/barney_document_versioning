from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from version.models import Version
from version import views
from django.test.client import RequestFactory

import json
import os

SAMPLE_MD = """
# TITLE 1

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut **labore et dolore** magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

* consectetur adipiscing elit
* incididunt ut labore

- - -

## TITLE 2

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu *fugiat nulla pariatur*. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

1. Excepteur sint occaecat
2. mollit anim id

| minim | consequat | occaecat |
| ----- | --------- | -------- |
| 2 | 3 | 4 |
| 5 | 6 | 7 |
| 8 | 9 | 10 |
"""

SAMPLE_MD_V1 = """
# TITLE 1

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut **labore et dolore** magna aliqua. Excepteur sint occaecat cupidatat non proident, Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

* consectetur adipiscing elit
* cupidatat
* incididunt ut labore

- - -

## TITLE 2

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu *fugiat nulla pariatur*.Sunt in culpa qui **officia** deserunt mollit anim id est laborum.

1. Excepteur sint occaecat
2. mollit anim id

| minim | consequat | occaecat |
| ----- | --------- | -------- |
| 2 | 3 | 4 |
| 5 | X | 7 |
| 8 | 9 | 10 |
"""

SAMPLE_MD_V2 = """
# TITLE 1

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut **labore et dolore.** Excepteur sint occaecat quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

* consectetur adipiscing elit
* incididunt ut labore
* eiusmod
* sit amet

- - -

## TITLE 2

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu *fugiat nulla pariatur*. Excepteur sint cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

1. Excepteur sint occaecat
2. mollit anim id

| minim | consequat | occaecat |
| ----- | --------- | -------- |
| 2 | 3 | 4 |
| 5 | 6 | 7 |
| 8 | 9 | 10 |
"""

SAMPLE_MD_V3 = """
# TITLE 1

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut **labore et dolore.** 

## TITLE 2
Excepteur sint occaecat quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

* consectetur adipiscing elit
* sit amet

- - -

## TITLE 3

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu *fugiat nulla pariatur*. Excepteur sint cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

1. Excepteur sint occaecat
2. mollit anim id

| minim | consequat | occaecat |
| ----- | --------- | -------- |
| 8 | 9 | 10 |
| 2 | 3 | 4 |
| 5 | 6 | 7 |
"""

# Create your tests here.
class impianto(TestCase):
    @classmethod
    def setUpTestData(cls):
        print("setUpTestData: Run once to set up non-modified data for all class methods.")
        cls.ut1 = User.objects.create(
            username='ut1',
            email='ut1@ut.com',
            password='u1'
        )
        cls.ut2 = User.objects.create(
            username='ut2',
            email='ut2@ut.com',
            password='u2'
        )
        cls.d1 = Version.objects.create(
            title="TEST MD 1 - master",
            base = "",
            owner = cls.ut1,
            content = SAMPLE_MD,
        )
        cls.d2 = Version.objects.create(
            title="TEST MD 2 - version",
            base = "",
            parent = cls.d1,
            owner = cls.ut1,
            content = SAMPLE_MD_V1,
        )
        cls.d3 = Version.objects.create(
            title="TEST MD 3 - conflicted",
            base = SAMPLE_MD,
            parent = cls.d2,
            owner = cls.ut2,
            content = SAMPLE_MD_V2,
            condiv = '[]',
        )
        cls.d4 = Version.objects.create(
            title="TEST MD 4 - conflicted",
            base = SAMPLE_MD,
            parent = cls.d2,
            owner = cls.ut1,
            content = SAMPLE_MD_V3,
            condiv = '["ut2"]',
        )
        print (Version.objects.all())

    def setUp(self):
        print(" ...................\n")
        self.factory = RequestFactory()
        pass

    def test_01_details_0(self):
        print("Method: details 0")
        request = self.factory.get('/version/details/0/')
        request.user = self.ut1
        response = views.details(request,self.d1.pk)
        print ("Response:",response.content)
        self.assertEqual(response.status_code, 200)

    def test_02_details_1(self):
        print("Method: details 1")
        request = self.factory.get('/version/details/0/')
        request.user = self.ut1
        response = views.details(request,self.d2.pk)
        print ("Response:",response.content)
        self.assertEqual(response.status_code, 200)

    def test_03_details_2(self):
        print("Method: details 2")
        request = self.factory.get('/version/details/2/')
        request.user = self.ut1
        response = views.details(request,self.d3.pk)
        print ("Response:",response.content)
        self.assertEqual(response.status_code, 200)

    def test_04_save_same_user(self):
        print("Method: save same_user")
        data = {'pk':1, "title": "save test", 'content': SAMPLE_MD_V2, 'condiv': '["ut2"]'}
        request = self.factory.post('/version/save/', data, content_type='application/json')
        request.user = self.ut1
        response = views.save(request)
        print ("Response:",response.content)
        self.assertEqual(response.status_code, 200)

    def test_05_save_other_user(self):
        print("Method: save other_user")
        data = {'pk':1, "title": "save test", 'content': SAMPLE_MD_V2, 'condiv': ''}
        request = self.factory.post('/version/save/', data, content_type='application/json')
        request.user = self.ut2
        response = views.save(request)
        print ("Response:",response.content)
        self.assertEqual(response.status_code, 500)

    def test_06_save_new_same_user(self):
        print("Method: save new doc same_user")
        data = {'pk':-1, "title": "save new test", 'content': SAMPLE_MD_V1, 'condiv': ''}
        request = self.factory.post('/version/save/', data, content_type='application/json')
        request.user = self.ut1
        response = views.save(request)
        print ("Response:",response.content)
        self.assertEqual(response.status_code, 200)

    def test_07_tree_base(self):
        print("Method: test tree")
        request = self.factory.get('/version/tree/0/')
        request.user = self.ut1
        response = views.vtree(request,None)
        print ("Response:",response.content)
        self.assertEqual(response.status_code, 200)

    def test_08_new_version(self):
        print("Method: new_version_same_user")
        request = self.factory.get('/version/new/0/')
        request.user = self.ut1
        response = views.new_version(request,self.d1.pk)
        print ("Response:",response.content)
        print (Version.objects.all())
        self.assertEqual(response.status_code, 200)

    def test_09_merge_version_same_user(self):
        print("Method: test_merge_version_same_user")
        request = self.factory.get('/version/merge/0/')
        request.user = self.ut1
        response = views.merge(request,self.d3.pk)
        print ("Response:",response.content)
        self.assertEqual(response.status_code, 200)

    def test_10_merge_version_other_user(self):
        print("Method: test_merge_version_other_user")
        request = self.factory.get('/version/merge/0/')
        request.user = self.ut2
        response = views.merge(request,self.d3.pk)
        print ("Response:",response.content)
        self.assertEqual(response.status_code, 500)

    def test_11_merge_master(self):
        print("Method: test_merge_version_other_user")
        request = self.factory.get('/version/merge/0/')
        request.user = self.ut1
        response = views.merge(request,self.d1.pk)
        print ("Response:",response.content)
        self.assertEqual(response.status_code, 500)

    def test_12_no_conflicts(self):
        print("Method: test_no_conflicts")
        request = self.factory.get('/version/merge/0/')
        request.user = self.ut1
        response = views.conflicts(request,self.d2.pk)
        print ("Response:",response.content)
        self.assertEqual(json.loads(response.content)["conflicts"], 0)

    def test_13_conflicts(self):
        print("Method: test_conflicts1")
        request = self.factory.get('/version/merge/0/')
        request.user = self.ut1
        response = views.conflicts(request,self.d3.pk)
        print ("Response:",response.content)
        self.assertEqual(json.loads(response.content)["conflicts"], 3)

    def test_14_conflicts(self):
        print("Method: test_no_conflicts2")
        request = self.factory.get('/version/merge/0/')
        request.user = self.ut1
        response = views.conflicts(request,self.d4.pk)
        print ("Response:",response.content)
        self.assertEqual(json.loads(response.content)["conflicts"], 6)

    def test_14_download_odt(self):
        print("Method: test_download_odt")
        request = self.factory.get('/version/odt/0/')
        request.user = self.ut1
        response = views.download(request,'odt',self.d2.pk)
        #print ("Response:",response.content)
        self.assertEqual(response.status_code, 200)

    def test_16_upload_odt_new_doc(self):
        print("Method: upload_odt_new_doc")
        file_path = os.path.join(os.path.dirname(__file__), "template.odt")
        with open(file_path, 'rb') as f:
            file_upload = SimpleUploadedFile("file", f.read(), content_type="application/vnd.oasis.opendocument.text")
            data = {
                "uploaded_content" : file_upload
            }
            request = self.factory.post('/version/upload//', data=data, format='multipart')
        request.user = self.ut1
        response = views.upload(request,None)
        print ("Response:",response.content)
        self.assertEqual(response.status_code, 200)

    def test_17_upload_odt_new_ver(self):
        print("Method: upload_odt_new_doc")
        file_path = os.path.join(os.path.dirname(__file__), "template.odt")
        with open(file_path, 'rb') as f:
            file_upload = SimpleUploadedFile("file", f.read(), content_type="application/vnd.oasis.opendocument.text")
            data = {
                "uploaded_content" : file_upload
            }
            request = self.factory.post('/version/upload//', data=data, format='multipart')
        request.user = self.ut1
        response = views.upload(request,self.d1.pk)
        print ("Response:",response.content)
        self.assertEqual(response.status_code, 200)

    def test_18_upload_md_new_doc(self):
        print("Method: upload_md_new_doc")
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "README.md")
        with open(file_path, 'rb') as f:
            file_upload = SimpleUploadedFile("file", f.read(), content_type="text/markdown")
            data = {
                "uploaded_content" : file_upload
            }
            request = self.factory.post('/version/upload//', data=data, format='multipart')
        request.user = self.ut1
        response = views.upload(request, None)
        print ("Response:",response.content)
        self.assertEqual(response.status_code, 200)