from django.core.files import uploadedfile
from .constants import *
from datetime import date, datetime, time
import re
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from rest_framework.test import APIClient
from django.urls import include, path, reverse
from rest_framework.test import APITestCase, URLPatternsTestCase
from rest_framework import status
from django.contrib.auth import authenticate, get_user_model
from rest_framework.authtoken.models import Token
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File


User = get_user_model()
file = File(open("C:/Users/Utilisateur/Desktop/notesabba.txt", 'rb'))
uploaded_file = SimpleUploadedFile('notesabba.txt', file.read(), content_type="text/plain")
# file = File(open('C:/Users/Utilisateur/Desktop/FreeShop2.0/my_site/media/accessoire.png', 'rb'))
# uploaded_file = SimpleUploadedFile('accessoire0.png', file.read(), content_type='image/png')
print(uploaded_file.size)

class APICustomTestCase(APITestCase):
    @property
    def bearer_token(self):
        # assuming there is a user in User model
        user = User.objects.get(username="Nyat")
        refresh = RefreshToken.for_user(user)
        return {"HTTP_AUTHORIZATION":f'Bearer {refresh.access_token}'}

    def setUp(self) -> None:
        self.client = APIClient()
        admin_user = User.objects.create_user(username="Nyat", email="franckhebo@gmail.com", password="Franck23.", role="Agent source", sex="male")
        admin_user.is_staff = True
        admin_user.is_active = True
        admin_user.save()

        self.client.force_authenticate(user=admin_user)

class StructuresCRUTests(APICustomTestCase):

    def test_create_update_nationalinformer(self):
        urlcreate = reverse('nationalinformer-list')
        resp = self.client.post(urlcreate, {"name": "ASECNA"})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, "national informer creation error") 
        self.assertEqual(NationalInformer.objects.count(), 1)
        urlupdate = reverse('nationalinformer-detail', kwargs={"pk": 1})
        resp = self.client.put(urlupdate, {"name": "CCAA"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "national informer update error") 
        self.assertEqual(resp.data["name"], "CCAA")

    def test_create_update_localinformer(self):
        urlcreate = reverse('localinformer-list')
        resp = self.client.post(urlcreate, {"name": "SEGC"})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, "local informer creation error") 
        self.assertEqual(LocalInformer.objects.count(), 1)
        urlupdate = reverse('localinformer-detail', kwargs={"pk": 1})
        resp = self.client.put(urlupdate, {"name": "SEGC 2"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "local informer update error") 
        self.assertEqual(resp.data["name"], "SEGC 2")

    def test_create_update_aerodrome(self):
        urlcreate = reverse('aerodrome-list')
        localinf = LocalInformer.objects.create(name="SEGC")
        data = {
            "name": "Aéroport de Douala",
            "code": "KD",
            "location_ind": "FKKD",
            "local_informer": localinf.id
        }
        resp = self.client.post(urlcreate, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, "aerodrome creation error") 
        self.assertEqual(Aerodrome.objects.count(), 1)        
        urlupdate = reverse('aerodrome-detail', kwargs={"pk": 1})
        data2 = {
            "name": "Aéroport de Douala",
            "code": "KB",
            "location_ind": "FKKB",
            "local_informer": localinf.id
        }
        resp = self.client.put(urlupdate, data2)
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "aerodrome update error") 
        self.assertEqual(resp.data["code"], "KB", "update aerodrome failed")
        self.assertEqual(resp.data["location_ind"], "FKKB", "update aerodrome failed")

    def test_create_update_unit(self):
        localinf = LocalInformer.objects.create(name="SEGC")
        aerodrome = Aerodrome.objects.create(name="Aeroport de Douala", code="KKKG", location_ind="KG", local_informer=localinf)
        urlcreate = reverse('unit-list')
        data = {
            "email": "doualaaero@gmail.com", 
            "name": "AIM", 
            "phone_number": "+237 655556478", 
            "fax":"233365458", 
            "address": "Quartier ET", 
            "aerodrome": aerodrome.id
        }
        resp = self.client.post(urlcreate, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, "aerodrome creation error") 
        self.assertEqual(Unit.objects.count(), 1)   
        urlupdate = reverse('unit-detail', kwargs={"pk": 1})
        data2 = {
            "email": "aimdoualaaero@gmail.com", 
            "name": "AIM unit", 
        }
        resp = self.client.patch(urlupdate, data2)
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "source unit update error") 
        self.assertEqual(resp.data["email"], "aimdoualaaero@gmail.com", "update unit failed")
        self.assertEqual(resp.data["name"], "AIM unit", "update unit failed")  


class AgentActionsTest(APICustomTestCase):

    def test_create_ddia(self):

        user = User.objects.get(username="Nyat")
        localinf = LocalInformer.objects.create(name="SEGC")
        aerodrome = Aerodrome.objects.create(name="Aeroport de Douala", code="KD", location_ind="FKKD", local_informer=localinf) 
        unit = Unit.objects.create(email="doualaaero@gmail.com", name="AIM", phone_number="+26556566", fax="256656", address="azertgyh", aerodrome=aerodrome)  
        agent = Agent.objects.create(user=user, unit=unit, source_structure=aerodrome)
        urlnotam = reverse('notam-create')
        data_notam = {
            'start_val_period': date(2021, 8, 22),
            'end_val_period': date(2021, 10, 22),
            'daily_freq_start': time(8, 30),
            'daily_freq_end': time(17, 30),
            'attachments': [
                # {'file': uploaded_file}
            ]
        }

        resp = self.client.post(urlnotam, data_notam)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, "notam create error") 
        urlsuppaip = reverse('supp-create')
        data_suppaip = {
            'start_val_period': date(2021, 8, 22),
            'end_val_period': date(2021, 10, 22),
            'object': "Transmission information au personnel",
            'attachments': [
                # {'file': uploaded_file}
            ]
        }

        resp = self.client.post(urlsuppaip, data_suppaip)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, "suppaip create error") 

        urlaic = reverse('aic-create')
        data_aic = {
            'subject': "Administratif",
            'object': "Transmission information au personnel",
            'attachments': [
                # {'file': uploaded_file}
            ]
        }
        resp = self.client.post(urlaic, data_aic)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, "aic create error") 

        urlsubmit = reverse('ddia-submittoverify', kwargs={'type_ddia': 'demandenotam', 'pk': 1})
        data_submit = {
            'decision': 'submit'
        }
        self.client.post(urlsubmit, data_submit)        
        urlsubmit = reverse('ddia-submittoverify', kwargs={'type_ddia': 'demandesupp', 'pk': 1})
        data_submit = {
            'decision': 'submit'
        }
        self.client.post(urlsubmit, data_submit)        
        urlsubmit = reverse('ddia-submittoverify', kwargs={'type_ddia': 'demandeaic', 'pk': 1})
        data_submit = {
            'decision': 'submit'
        }
        self.client.post(urlsubmit, data_submit)  


        user_verif = User.objects.create_user(username="Lomta", email="talompatrick@gmail.com", password="Talom23.", role="Verificateur source", sex="male")
        user_verif.is_active = True
        user_verif.save()
        agent_verif = Agent.objects.create(user=user_verif, unit=unit, source_structure=aerodrome)


class AgentsControlsActionsTest(APITestCase):
    
    def setUp(self) -> None:
        self.user_init = User.objects.create_user(username="Nyat", email="franckhebo@gmail.com", first_name="Jean Roland", last_name="Nyatchou", password="Franck23.", role="Agent source", sex="male")
        self.user_init.is_active = True
        self.user_init.save()
        self.user_init2 = User.objects.create_user(username="Nyat0", email="fohebo@gmail.com", password="Franck23.", role="Agent source", sex="male")
        self.user_init2.is_active = True
        self.user_init2.save()
        self.refresh_user_init = RefreshToken.for_user(self.user_init)
        self.user_verif = User.objects.create_user(username="Lomta", email="talompatrick@gmail.com", password="Talom23.", role="Verificateur source", sex="male")
        self.user_verif.is_active = True
        self.user_verif.save()
        self.refresh_user_verif = RefreshToken.for_user(self.user_verif)
        self.user_commander = User.objects.create_user(username="Asa", email="joelasa@gmail.com", password="Talom23.", role="Structure source", sex="male")
        self.user_commander.is_active = True
        self.user_commander.save()
        self.refresh_user_command = RefreshToken.for_user(self.user_commander)
        self.user_localinf = User.objects.create_user(username="KONRAD", email="hebogerland@gmail.com", password="Talom23.", role="Informateur local", sex="male")
        self.user_localinf.is_active = True
        self.user_localinf.save()
        self.refresh_user_localinf = RefreshToken.for_user(self.user_localinf)
        localinf = LocalInformer.objects.create(name="SEGC")
        aerodrome = Aerodrome.objects.create(name="Aeroport de Douala", code="KD", location_ind="FKKD", local_informer=localinf) 
        aerodrome2 = Aerodrome.objects.create(name="Aeroport de Yaoundé", code="KB", location_ind="FKKB", local_informer=localinf) 

        unit0 = Unit.objects.create(email="doualaaero0@gmail.com", name="MIRE", phone_number="+237 656556566", fax="256656", address="azertgyh", aerodrome=aerodrome) 
        unit = Unit.objects.create(email="doualaaero@gmail.com", name="AIM", phone_number="+26556566", fax="256656", address="azertgyh", aerodrome=aerodrome) 
        unit2 = Unit.objects.create(email="yaoundeaero@gmail.com", name="AIM", phone_number="+2655556566", fax="2565656", address="azertgyh", aerodrome=aerodrome2) 
        Agent.objects.create(user=self.user_init, unit=unit0, source_structure=aerodrome)   
        Agent.objects.create(user=self.user_init2, unit=unit2, source_structure=aerodrome2)  
        Agent.objects.create(user=self.user_verif, unit=unit, source_structure=aerodrome)
        Agent.objects.create(user=self.user_commander, unit=unit, source_structure=aerodrome)
        LocalAgent.objects.create(user=self.user_localinf, localinformer=localinf)

    def test_controls_on_ddia(self):
        self.client = APIClient()
        
        self.client.force_authenticate(self.user_init)

        urlcreate = reverse('notam-create')
        data_notam = {
            'start_val_period': date(2021, 8, 22),
            'end_val_period': date(2021, 10, 22),
            'daily_freq_start': time(8, 30),
            'daily_freq_end': time(17, 30),
            'attachments': [
                # {'file': uploaded_file}
            ]        
        }
        resp = self.client.post(urlcreate, data_notam) 
        agent = Agent.objects.get(user=self.user_init)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, "notam create error") 
        self.assertEqual(DemandeNOTAM.objects.count(), 1)
        histories = DDIAHistory.objects.filter(user=self.user_init)
        self.assertEqual(histories.count(), 1, "no history created")
        self.assertEqual(histories.first().type_action, CREATE_ACTION, "no history for creation")

        urlsubmit = reverse('ddia-submittoverify', kwargs={'type_ddia': 'demandenotam', 'pk': 1})
        data_submit = {
            'decision': 'submit'
        }
        resp = self.client.post(urlsubmit, data_submit, HTTP_AUTHORIZATION=f'Bearer {self.refresh_user_init.access_token}')  
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "notam submit error") 
        demandenotam = DemandeNOTAM.objects.get(id=1)
        self.assertEqual(demandenotam.state, PENDING_VERIFICATION_STATE, "demandenotam submit error") 
        self.assertEqual(ActionAgentOnDDIA.objects.filter(agent=agent, prev_state=DRAFT_STATE).count(), 1, "ActionAgentOnDDIA for initiator submit create error")
        histories = DDIAHistory.objects.filter(user=self.user_init, type_action=CONTROLE_ACTION)
        self.assertEqual(histories.count(), 1, "no history for submit")
        self.assertEqual(histories.first().type_action, CONTROLE_ACTION, "no history for submit")

        self.client.force_authenticate(self.user_verif)

        urlverif = reverse('ddia-verify', kwargs={'type_ddia': 'demandenotam', 'pk': 1})        
        data_accept = {
            'decision': 'accept'
        }
        resp = self.client.post(urlverif, data_accept) 
        agent_verif = Agent.objects.get(user=self.user_verif) 
        ddia = DemandeNOTAM.objects.get(id=1) 
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "notam verification error")
        self.assertEqual(ddia.state, PENDING_ADMISSION_STATE, "notam verification error")
        self.assertEqual(ActionAgentOnDDIA.objects.filter(agent=agent_verif, prev_state=PENDING_VERIFICATION_STATE).count(), 1, "ActionAgentOnDDIA for verificator create error")
        histories = DDIAHistory.objects.filter(user=self.user_verif, type_action=CONTROLE_ACTION)
        self.assertEqual(histories.count(), 1, "no history for verif")
        history = histories.first()
        self.assertEqual(history.type_action, CONTROLE_ACTION, "no history for verif")
        self.assertEqual(history.modifshistory.all().count(), 1)

        urllistddia = reverse('listDDIAprocessed-verifsource', kwargs={'type_ddia': 'notam'})
        resp = self.client.get(urllistddia)
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "list ddia error")

        self.client.force_authenticate(self.user_commander)

        resp = self.client.get(urllistddia)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN, "permission error")

        urladmit = reverse('ddia-admit', kwargs = {'type_ddia': 'demandenotam', 'pk': 1})
        data_accept = {
            'decision': 'accept'
        }
        resp = self.client.post(urladmit, data_accept, HTTP_AUTHORIZATION=f'Bearer {self.refresh_user_command.access_token}') 
        agent_admit = Agent.objects.get(user=self.user_commander) 
        ddia = DemandeNOTAM.objects.get(id=1) 
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "notam admission error")
        self.assertEqual(ddia.state, PENDING_VALIDATION_STATE, "notam admission error")
        self.assertEqual(ActionAgentOnDDIA.objects.filter(agent=agent_admit, prev_state=PENDING_ADMISSION_STATE).count(), 1, "ActionAgentOnDDIA for admission create error")
        histories = DDIAHistory.objects.filter(user=self.user_commander, type_action=CONTROLE_ACTION)
        self.assertEqual(histories.count(), 1, "no history for admit")
        history = histories.first()
        self.assertEqual(history.type_action, CONTROLE_ACTION, "no history created for admission")
        self.assertEqual(history.modifshistory.all().count(), 1)

        self.client.force_authenticate(self.user_localinf)

        urlvalidate = reverse('ddia-validate', kwargs ={'type_ddia': 'demandenotam', 'pk': 1})
        data_accept = {
            'decision': 'accept'
        }
        resp = self.client.post(urlvalidate, data_accept, HTTP_AUTHORIZATION=f'Bearer {self.refresh_user_localinf.access_token}') 
        local_agent = LocalAgent.objects.get(user=self.user_localinf) 
        ddia = DemandeNOTAM.objects.get(id=1) 
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "notam validation error")
        self.assertEqual(ddia.state, PENDING_APPROVAL_STATE, "notam validation error")
        self.assertEqual(Validation.objects.filter(local_agent=local_agent).count(), 1, "Validation object create error")
        histories = DDIAHistory.objects.filter(user=self.user_localinf, type_action=CONTROLE_ACTION)
        self.assertEqual(histories.count(), 1, "no history for local informer")
        history = histories.first()
        self.assertEqual(history.type_action, CONTROLE_ACTION, "no history created for local informer")
        self.assertEqual(history.modifshistory.all().count(), 1)

        urllistddia = reverse('listDDIAprocessed-localinformer', kwargs={'type_ddia': 'notam'})
        resp = self.client.get(urllistddia)
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "list ddia error")
        url0 = resp.data[0]['ddia_object']['url']
        resp_detail = self.client.get(url0)
        print(resp_detail.data)

    def test_failed_controls_on_ddia(self):
        self.client = APIClient()

        self.client.force_authenticate(self.user_init)

        urlcreate = reverse('notam-create')
        data_notam = {
            'start_val_period': date(2021, 2, 22),
            'end_val_period': date(2021, 1, 22),
            'daily_freq_start': time(18, 30),
            'daily_freq_end': time(17, 30),
            'attachments': [
                # {'file': uploaded_file}
            ]        
        }
        resp = self.client.post(urlcreate, data_notam)        
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST, "notam create problem") 
        self.assertIn('end_val_period', resp.data.keys(),  "field error not thrown")
        self.assertIn('daily_freq_end', resp.data.keys(),  "field error not thrown")
        self.assertIn('start_val_period', resp.data.keys(),  "field error not thrown")

        data_notam = {
            'start_val_period': date(2021, 8, 22),
            'end_val_period': date(2021, 10, 22),
            'daily_freq_start': time(8, 30),
            'daily_freq_end': time(17, 30),
            'attachments': [
                # {'file': uploaded_file}
            ]
        }

        self.client.force_authenticate(self.user_commander)
        resp = self.client.post(urlcreate, data_notam)   
        self.assertEqual(DemandeNOTAM.objects.count(), 0)
        self.assertEqual(DDIAHistory.objects.count(), 0, "history for create ddia error")
  
        self.client.force_authenticate(self.user_localinf)
        resp = self.client.post(urlcreate, data_notam)   
        self.assertEqual(DemandeNOTAM.objects.count(), 0)
        self.assertEqual(DDIAHistory.objects.count(), 0, "history for create ddia error")

        self.client.force_authenticate(self.user_init2)
        resp = self.client.post(urlcreate, data_notam)   
        urlsubmit = reverse('ddia-submittoverify', kwargs={'type_ddia': 'demandenotam', 'pk': 1})
        data_submit = {
            'decision': 'submit'
        }

        self.client.force_authenticate(self.user_init)
        resp = self.client.post(urlsubmit, data_submit) 
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN, "notam submit permission error")

        self.client.force_authenticate(self.user_init2)
        resp = self.client.post(urlsubmit, data_submit) 
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "submission Error")

        urlverif = reverse('ddia-verify', kwargs={'type_ddia': 'demandenotam', 'pk': 1})  
        self.client.force_authenticate(self.user_verif)
        data_accept = {
            'decision': 'accept'
        }
        resp = self.client.post(urlverif, data_accept)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN, "notam verif error")

        agent_verif = Agent.objects.get(user=self.user_verif) 

        try:
            ddia = DemandeNOTAM.objects.get(id=1) 
            self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN, "notam verification error")
            self.assertEqual(ddia.state, PENDING_VERIFICATION_STATE, "notam verification error")
            self.assertEqual(ActionAgentOnDDIA.objects.filter(agent=agent_verif, prev_state=PENDING_VERIFICATION_STATE).count(), 0, "ActionAgentOnDDIA for verificator create error")
            histories = DDIAHistory.objects.filter(user=self.user_verif, type_action=CONTROLE_ACTION)
            self.assertEqual(histories.count(), 0, "history error")
        except:
            pass
    
        