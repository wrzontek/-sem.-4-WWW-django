from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from .models import *
from .views import *

example_content = R'''/*@ predicate Sorted{L}(int *a, integer l, integer h) =
  @   \forall integer i,j; l <= i <= j < h ==> a[i] <= a[j] ;
  @*/

/*@ requires \valid_range(t,0,n-1);
  @ ensures Sorted(t,0,n-1);
  @*/
void insert_sort(int t[], int n) {
  int i,j;
  int mv;
  if (n <= 1) return;
  /*@ loop invariant 0 <= i <= n;
    @ loop invariant Sorted(t,0,i);
    @ loop variant n-i;
    @*/
  for (i=1; i<n; i++) {
    // assuming t[0..i-1] is sorted, insert t[i] at the right place
    mv = t[i]; 
    /*@ loop invariant 0 <= j <= i;
      @ loop invariant j == i ==> Sorted(t,0,i);
      @ loop invariant j < i ==> Sorted(t,0,i+1);
      @ loop invariant \forall integer k; j <= k < i ==> t[k] > mv;
      @ loop variant j;
      @*/
    // look for the right index j to put t[i]
    for (j=i; j > 0; j--) {
      if (t[j-1] <= mv) break;
      t[j] = t[j-1];
    }
    t[j] = mv;
  }
}


/*
Local Variables:
compile-command: "frama-c -jessie insertion_sort.c"
End:
*/
'''

class ModelTests(TestCase):

    def test_create_and_cascade_delete(self):
        user = User(username="test_usr", password="examplepassword123124$")
        dir = Directory(name="test_dir", description="test_desc", owner=user)
        file = File(name="test_file", description="test_desc", owner=dir.owner, directory=dir, content="łubudubu")
        fs = FileSection(file=file, line_number=0, content=file.content)

        sc = SectionCategory(category="fake_category", file_section=fs)
        status = SectionStatus(status="fake_status", file_section=fs)
        status_data = StatusData(data="fake_data", user=file.owner, file_section=fs)

        user.save()
        dir.save()
        file.save()
        fs.save()

        self.assertEqual(dir.owner, user)
        self.assertEqual(file.owner, user)
        self.assertEqual(status_data.user, user)

        dir.delete()

        self.assertEqual(len(Directory.objects.all()), 0)
        self.assertEqual(len(File.objects.all()), 0)
        self.assertEqual(len(FileSection.objects.all()), 0)
        self.assertEqual(len(SectionCategory.objects.all()), 0)
        self.assertEqual(len(SectionStatus.objects.all()), 0)
        self.assertEqual(len(StatusData.objects.all()), 0)
        self.assertEqual(len(User.objects.all()), 1)


class ViewsTests(TestCase):

    def test_no_logon(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_logon_invalid(self):
        c = Client()
        response = c.post('/framaw/', {'username': 'john', 'password': 'smith'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"invalid username or password")

    def test_logon_valid(self):
        c = Client()
        User.objects.create_user(username="usr", password="password123").save()
        response = c.post('/framaw/', {'username': 'usr', 'password': 'password123'})
        self.assertEqual(response.status_code, 302)

    def test_new_file(self):
        c = Client()
        User.objects.create_user(username="usr", password="password123").save()
        response = c.post('/framaw/', {'username': 'usr', 'password': 'password123'})
        self.assertEqual(response.status_code, 302)
        response = c.post('/framaw/new_file/')
        self.assertEqual(response.status_code, 200)

    def test_new_dir(self):
        c = Client()
        User.objects.create_user(username="usr", password="password123").save()
        response = c.post('/framaw/', {'username': 'usr', 'password': 'password123'})
        self.assertEqual(response.status_code, 302)
        response = c.post('/framaw/new_directory/')
        self.assertEqual(response.status_code, 200)

    def test_create_dir(self):
        c = Client()
        User.objects.create_user(username="usr", password="password123").save()
        response = c.post('/framaw/', {'username': 'usr', 'password': 'password123'})
        self.assertEqual(response.status_code, 302)
        response = c.post('/framaw/create_directory/', {'name': 'testdir', 'description': '1234145', 'parent_dir': ""})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Directory.objects.all()[0].name, 'testdir')
        self.assertEqual(Directory.objects.all()[0].description, '1234145')

    def test_describe_section(self):
        user = User(username="test_usr", password="examplepassword123124$")
        dir = Directory(name="test_dir", description="test_desc", owner=user)
        file = File(name="test_file", description="test_desc", owner=dir.owner, directory=dir, content="łubudubu")

        user.save()
        dir.save()
        file.save()

        fs = FileSection(file=file, line_number=0,
                         content="  @   ensures \\result >= 0 ==> t[\\result] == v;\r\n  @ behavior failure:\r\n")
        fs.save()

        describe_section(fs, user)

        self.assertEqual(len(FileSection.objects.all()), 1)
        self.assertEqual(len(SectionCategory.objects.all()), 1)
        self.assertEqual(len(SectionStatus.objects.all()), 1)
        self.assertEqual(len(StatusData.objects.all()), 1)

        sc = SectionCategory.objects.all()[0]
        ss = SectionStatus.objects.all()[0]
        sd = StatusData.objects.all()[0]

        self.assertEqual(sc.category, "ensures")
        self.assertEqual(ss.status, "unchecked")
        self.assertEqual(sd.data, "")

    def test_recursive_delete_dir(self):
        user = User(username="test_usr", password="examplepassword123124$")
        dir = Directory(name="test_dir", description="test_desc", owner=user)
        dir2 = Directory(name="test_dir2", description="test_desc2", owner=user, parent_dir=dir)
        file = File(name="test_file", description="test_desc", owner=dir2.owner, directory=dir2, content="łubudubu")

        user.save()
        dir.save()
        dir2.save()
        file.save()

        self.assertEqual(file.valid, True)
        self.assertEqual(dir2.valid, True)

        recursive_delete_dir(dir)

        file = File.objects.get(name="test_file")
        dir2 = Directory.objects.get(name="test_dir2")
        self.assertEqual(file.valid, False)
        self.assertEqual(dir2.valid, False)

    def test_display_file(self):
        c = Client()
        user = User.objects.create_user(username="usr", password="password123")
        dir = Directory(name="test_dir", description="test_desc", owner=user)
        user.save()
        dir.save()
        file = File(name="test_file", description="test_desc", owner=dir.owner, directory=dir,
             content=example_content)
        file.save()

        response = c.post('/framaw/', {'username': 'usr', 'password': 'password123'})
        self.assertEqual(response.status_code, 302)
        response = c.get('/framaw/display_file/', {'name': 'test_file'})
        self.assertEqual(response.status_code, 200)

    def test_parse_file(self):
        c = Client()
        user = User.objects.create_user(username="usr", password="password123")
        dir = Directory(name="test_dir", description="test_desc", owner=user)
        user.save()
        dir.save()
        file = File(name="test_file", description="test_desc", owner=dir.owner, directory=dir,
             content=example_content)
        file.save()

        response = c.post('/framaw/', {'username': 'usr', 'password': 'password123'})
        self.assertEqual(response.status_code, 302)

        parse_file_content(file.content, file)

        self.assertEqual(len(FileSection.objects.all()), 11)
        self.assertEqual(len(SectionStatus.objects.all()), 11)
        self.assertEqual(len(StatusData.objects.all()), 11)
