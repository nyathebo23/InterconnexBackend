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

print(uploaded_file.size)

# class APICustomTestCase(APITestCase):
    # @property
    # def bearer_token(self):
    #     user = User.objects.get(username="Nyat")
    #     refresh = RefreshToken.for_user(user)
    #     return {"HTTP_AUTHORIZATION":f'Bearer {refresh.access_token}'}



class StructuresCRUTests(APITestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        admin_user = User.objects.create_user(username="Nyat", email="franckhebo@gmail.com", password="Franck23.", role="Agent source", sex="male", is_staff=True)
        admin_user.is_active = True
        admin_user.save()

        self.client.force_authenticate(user=admin_user)

    def test_create_update_nationalinformer(self):
        urlcreate = reverse('nationalinformer-list')
        resp = self.client.post(urlcreate, {"name": "ASECNA"})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, "national informer creation error") 
        self.assertEqual(NationalInformer.objects.count(), 1)
        print(resp.data)
        urlupdate = reverse('nationalinformer-detail', kwargs={"pk": 1})
        resp = self.client.put(urlupdate, {"name": "CCAA"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "national informer update error") 
        self.assertEqual(resp.data["name"], "CCAA")

    def test_create_update_localinformer(self):
        urlcreate = reverse('localinformer-list')
        print(urlcreate)
        resp = self.client.post(urlcreate, {"name": "SEGC"})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, "local informer creation error") 
        self.assertEqual(LocalInformer.objects.count(), 1)
        print(resp.data)
        urlupdate = reverse('localinformer-detail', kwargs={"pk": 1})
        resp = self.client.put(urlupdate, {"name": "SEGC 2"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "local informer update error") 
        self.assertEqual(resp.data["name"], "SEGC 2")

    def test_create_update_aerodrome(self):
        urlcreate = reverse('aerodrome-list')
        localinf = LocalInformer.objects.create(name="SEGC")
        data = {
            "name": "Aéroport de Douala",
            "location_ind": "FKKD",
            "is_conceded": True
        }
        resp = self.client.post(urlcreate, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, "aerodrome creation error") 
        self.assertEqual(Aerodrome.objects.count(), 1)      
        print(resp.data)  
        urlupdate = reverse('aerodrome-detail', kwargs={"pk": 1})
        data2 = {
            "name": "Aéroport de Douala",
            "location_ind": "FKKB",
            "is_conceded": False
        }
        resp = self.client.put(urlupdate, data2)
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "aerodrome update error") 
        self.assertEqual(resp.data["location_ind"], "FKKB", "update aerodrome failed")

    def test_create_update_unit(self):
        aerodrome = Aerodrome.objects.create(name="Aeroport de Douala", location_ind="KKKG")
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
        print(resp.data)

        urlupdate = reverse('unit-detail', kwargs={"pk": 1})
        data2 = {
            "email": "aimdoualaaero@gmail.com", 
            "name": "AIM unit", 
        }
        resp = self.client.patch(urlupdate, data2)
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "source unit update error") 
        self.assertEqual(resp.data["email"], "aimdoualaaero@gmail.com", "update unit failed")
        self.assertEqual(resp.data["name"], "AIM unit", "update unit failed")  


class AgentsControlsActionsTest(APITestCase):
    
    def setUp(self) -> None:
        self.user_init = User.objects.create_user(username="Nyat0", email="franckheo@gmail.com", first_name="Jean Roland", last_name="Nyatchou", password="Franck23.", role=SOURCE_AGENT, sex="male")
        self.user_init.is_active = True
        self.user_init.save()
        self.client_init = APIClient()
        self.client_init.force_authenticate(self.user_init)
        self.user_verif = User.objects.create_user(username="Lomta", email="talompatrick@gmail.com", password="Talom23.", role=SOURCE_VERIFIER, sex="male")
        self.user_verif.is_active = True
        self.user_verif.save()
        self.client_verif = APIClient()
        self.client_verif.force_authenticate(self.user_verif)
        self.user_commander = User.objects.create_user(username="Asa", email="joelasa@gmail.com", password="Talom23.", role=SOURCE_STRUCTURE, sex="male")
        self.user_commander.is_active = True
        self.user_commander.save()
        self.client_commander = APIClient()
        self.client_commander.force_authenticate(self.user_commander)
        self.user_localinf = User.objects.create_user(username="KONRAD", email="hebogerland@gmail.com", password="Talom23.", role=LOCAL_INFORMER, sex="male")
        self.user_localinf.is_active = True
        self.user_localinf.save()
        self.client_localinf = APIClient()
        self.client_localinf.force_authenticate(self.user_localinf)
        self.user_nationalinf = User.objects.create_user(username="Kolo", email="hebond@gmail.com", password="Talom23.", role=NATIONAL_INFORMER, sex="male")
        self.user_nationalinf.is_active = True
        self.user_nationalinf.save()
        self.client_nationalinf = APIClient()
        self.client_nationalinf.force_authenticate(self.user_nationalinf)
        self.user_nationalinf2 = User.objects.create_user(username="Kolo2", email="hebodonal@gmail.com", password="Talom23.", role=NATIONAL_INFORMER, sex="male")
        self.user_nationalinf2.is_active = True
        self.user_nationalinf2.save()
        self.client_nationalinf2 = APIClient()
        self.client_nationalinf2.force_authenticate(self.user_nationalinf2)
        nationalinf = NationalInformer.objects.create(name="CCAA", is_authority=True)
        nationalinf2 = NationalInformer.objects.create(name="ASECNA representant")
        localinf = LocalInformer.objects.create(name="SEGC")
        aerodrome = Aerodrome.objects.create(name="Aeroport de Douala", location_ind="FKKD") 
        unit = Unit.objects.create(email="doualaaero@gmail.com", name="AIM", phone_number="+26556566", fax="256656", address="azertgyh", aerodrome=aerodrome) 
        localinf_aerodrome = LocalInformer.objects.create(name="Bureau AIM de l'aéroport de Douala", unit=unit, aerodrome=aerodrome)
        Agent.objects.create(user=self.user_init, unit=unit, aerodrome=aerodrome)    
        LocalAgent.objects.create(user=self.user_verif, localinformer=localinf_aerodrome)
        Agent.objects.create(user=self.user_commander, unit=unit, aerodrome=aerodrome)
        LocalAgent.objects.create(user=self.user_localinf, localinformer=localinf)
        NationalAgent.objects.create(user=self.user_nationalinf, nationalinformer=nationalinf)
        NationalAgent.objects.create(user=self.user_nationalinf2, nationalinformer=nationalinf2)

    def test_controls_on_ddia(self):
        resp = self.client_init.get(reverse('agent-infos'))
        print(resp.data)
        resp = self.client_verif.get(reverse('agent-infos'))
        print(resp.data)
        resp = self.client_localinf.get(reverse('localagent-infos'))
        print(resp.data)
        resp = self.client_nationalinf.get(reverse('nationalagent-infos'))
        print(resp.data)
        urlcreate = reverse('notam-create')
        data_notam = {
            'start_val_period': datetime(2021, 8, 22, 8, 30, 15),
            'end_val_period': datetime(2021, 10, 22, 8, 30, 15),
            'daily_freq_start': time(8, 30),
            'daily_freq_end': time(17, 30),
            'attachments': [
                # {'file': uploaded_file}
            ]        
        }
        resp = self.client_init.post(urlcreate, data_notam) 
        agent = Agent.objects.get(user=self.user_init)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, "notam create error") 
        self.assertEqual(DemandeNOTAM.objects.count(), 1)
        histories = DDIAHistory.objects.filter(agent=agent)
        self.assertEqual(histories.count(), 1, "no history created")
        self.assertEqual(histories.first().type_action, CREATE_ACTION, "no history for creation")

        urlsubmit = reverse('ddia-submittoverify', kwargs={'type_ddia': 'demandenotam', 'pk': 1})
        data_submit = {
            'decision': 'submit'
        }
        resp = self.client_init.post(urlsubmit, data_submit)  
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "notam submit error") 
        demandenotam = DemandeNOTAM.objects.get(id=1)
        self.assertEqual(demandenotam.state, PENDING_VERIFICATION_STATE, "demandenotam submit error") 
        self.assertEqual(SourceStructureAction.objects.filter(agent=agent, prev_state=DRAFT_STATE).count(), 1, "SourceStructureAction for initiator submit create error")
        histories = DDIAHistory.objects.filter(agent=agent, type_action=CONTROLE_ACTION)
        self.assertEqual(histories.count(), 1, "no history for submit")
        self.assertEqual(histories.first().type_action, CONTROLE_ACTION, "no history for submit")

        urlverif = reverse('ddia-verify', kwargs={'type_ddia': 'demandenotam', 'pk': 1})        
        data_accept = {
            'decision': 'accept',
            # 'nationalinf_id': 1
        }
        resp = self.client_verif.post(urlverif+'?is_localinf=yes', data_accept) 
        agent_verif = LocalAgent.objects.get(user=self.user_verif) 
        ddia = DemandeNOTAM.objects.get(id=1) 
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "notam verification error")
        self.assertEqual(ddia.state, PENDING_ADMISSION_STATE, "notam verification error")
        self.assertEqual(LocalInformerAction.objects.filter(local_agent=agent_verif, prev_state=PENDING_VERIFICATION_STATE).count(), 1, "SourceStructureAction for verificator create error")
        histories = DDIAHistory.objects.filter(local_agent=agent_verif, type_action=CONTROLE_ACTION)
        self.assertEqual(histories.count(), 1, "no history for verif")
        history = histories.first()
        self.assertEqual(history.type_action, CONTROLE_ACTION, "no history for verif")
        self.assertEqual(history.modifshistory.all().count(), 1)


        urllistddia = reverse('listDDIAprocessed-verifsource', kwargs={'type_ddia': 'notam'})
        resp = self.client_verif.get(urllistddia+'?is_localinf=yes')
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "list ddia error")

        resp = self.client_commander.get(urllistddia)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN, "permission error")

        urladmit = reverse('ddia-admit', kwargs = {'type_ddia': 'demandenotam', 'pk': 1})
        data_accept = {
            'decision': 'accept'
        }
        resp = self.client_commander.post(urladmit, data_accept) 
        agent_admit = Agent.objects.get(user=self.user_commander) 
        ddia = DemandeNOTAM.objects.get(id=1) 
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "notam admission error")
        self.assertEqual(ddia.state, PENDING_VALIDATION_STATE, "notam admission error")
        self.assertEqual(SourceStructureAction.objects.filter(agent=agent_admit, prev_state=PENDING_ADMISSION_STATE).count(), 1, "SourceStructureAction for admission create error")
        histories = DDIAHistory.objects.filter(agent=agent_admit, type_action=CONTROLE_ACTION)
        self.assertEqual(histories.count(), 1, "no history for admit")
        history = histories.first()
        self.assertEqual(history.type_action, CONTROLE_ACTION, "no history created for admission")
        self.assertEqual(history.modifshistory.all().count(), 1)


        urlvalidate = reverse('ddia-validate', kwargs ={'type_ddia': 'demandenotam', 'pk': 1})
        data_accept = {
            'decision': 'accept'
        }
        resp = self.client_localinf.post(urlvalidate, data_accept) 
        local_agent = LocalAgent.objects.get(user=self.user_localinf) 
        ddia = DemandeNOTAM.objects.get(id=1) 
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "notam validation error")
        self.assertEqual(ddia.state, PENDING_APPROVAL_STATE, "notam validation error")
        self.assertEqual(LocalInformerAction.objects.filter(local_agent=local_agent).count(), 1, "Validation object create error")
        histories = DDIAHistory.objects.filter(local_agent=local_agent, type_action=CONTROLE_ACTION)
        self.assertEqual(histories.count(), 1, "no history for local informer")
        history = histories.first()
        self.assertEqual(history.type_action, CONTROLE_ACTION, "no history created for local informer")
        self.assertEqual(history.modifshistory.all().count(), 1)


        urllistddia = reverse('listDDIAprocessed-localinformer', kwargs={'type_ddia': 'notam'})
        resp = self.client_localinf.get(urllistddia)
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "list ddia error")
        self.assertEqual(len(resp.data), 1, "list ddia error")
        print(resp.data)
        urldetail = resp.data[0]['ddia_object']['url']
        resp_detail = self.client_localinf.get(urldetail)
        self.assertEqual(resp_detail.status_code, status.HTTP_200_OK, "retrieve error")
        self.assertIn('history', resp_detail.data.keys(), "no history in response detail")
        print(resp_detail.data)

    def test_failed_controls_on_ddia(self):
        self.client = APIClient()

        self.client.force_authenticate(self.user_init)

        urlcreate = reverse('notam-create')
        data_notam = {
            'start_val_period': datetime(2021, 4, 22, 8, 30, 15),
            'end_val_period': datetime(2021, 3, 22, 8, 30, 15),
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

