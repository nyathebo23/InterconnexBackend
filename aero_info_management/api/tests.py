from ..models import Aerodrome, LocalInformer, NationalInformer, Unit
from rest_framework.test import APIClient
from django.urls import include, path, reverse
from rest_framework.test import APITestCase, URLPatternsTestCase
from rest_framework.generics import status
from django.contrib.auth import get_user_model

# User = get_user_model()
# admin_user = User.objects.create(username="Nyat", password="Franck23.", role="Agent source", sex="male", is_superuser=True)

# client = APIClient()
# client.force_authenticate(user=admin_user)

# class StructuresCRUTests(APITestCase):

#     # def setUp(self) -> None:
#     #     User = get_user_model()
#     #     admin_user = User.objects.create(username="Nyat", password="Franck23.", role="Agent source", sex="male", is_superuser=True)

#     def test_create_nationalinformer(self):
#         url = reverse('nationalinformer-list')
#         response = client.post(url, {"name": "ASECNA"})
#         print(response.data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED, "national informer creation error") 
#         self.assertEqual(NationalInformer.objects.count(), 1)

#     def test_create_localinformer(self):
#         url = reverse('localinformer-list')
#         response = client.post(url, {"name": "SEGC"} )
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED, "local informer creation error") 
#         self.assertEqual(LocalInformer.objects.count(), 1)


#     def test_create_aerodrome(self):
#         url = reverse('aerodrome-list')
#         localinf = LocalInformer.objects.create(name="SEGC")
#         data = {
#             "name": "Aéroport de Douala",
#             "code": "KD",
#             "location_ind": "FKKD",
#             "local_informer": localinf.id
#         }
#         response = client.post(url, data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED, "aerodrome creation error") 
#         self.assertEqual(Aerodrome.objects.count(), 1)        

#     def test_create_unit(self):
#         localinf = LocalInformer.objects.create(name="SEGC")
#         aerodrome = Aerodrome.objects.create(name="Aeroport de Douala", code="KKKG", location_ind="KG", local_informer=localinf)
#         url = reverse('unit-list')
#         data = {
#             "email": "doualaaero@gmail.com", 
#             "name": "AIM", 
#             "phone_number": "+237 655556478", 
#             "fax":"233365458", 
#             "address": "Quartier ET", 
#             "aerodrome": aerodrome.id
#         }
#         response = client.post(url, data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED, "aerodrome creation error") 
#         self.assertEqual(Unit.objects.count(), 1)   

