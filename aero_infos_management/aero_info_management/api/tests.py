from ..models import *
from datetime import date, datetime, time
from rest_framework.test import APIClient
from django.urls import include, path, reverse
from rest_framework.test import APITestCase, URLPatternsTestCase
from rest_framework import status, generics
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File
from django.contrib.auth import get_user_model

User = get_user_model()
file = File(open("C:/Users/Utilisateur/Desktop/notesabba.txt", 'rb'))
uploaded_file = SimpleUploadedFile('notesabba.txt', file.read())

class AgentActionsTest(APITestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        admin_user = User.objects.create_user(username="Nyat", email="franckhebo@gmail.com", password="Franck23.", role="Agent source", sex="male", is_staff=True)
        admin_user.is_active = True
        admin_user.save()
        self.client.force_authenticate(user=admin_user)

    def test_create_submit_ddia(self):
        user = User.objects.get(username="Nyat")
        aerodrome = Aerodrome.objects.create(name="Aeroport de Douala", location_ind="FKKD", is_conceded=True) 
        unit = Unit.objects.create(email="doualaaero@gmail.com", name="AIM", phone_number="+26556566", fax="256656", address="azertgyh", aerodrome=aerodrome)  
        agent = Agent.objects.create(user=user, unit=unit, aerodrome=aerodrome)
        urlnotam = reverse('notam-create')
        data_notam = {
            'start_val_period': datetime(2021, 8, 22, 8, 30, 15),
            'end_val_period': datetime(2021, 10, 22, 8, 30, 15),
            'daily_freq_start': time(8, 30),
            'daily_freq_end': time(17, 30),
            'attachments': [
                # {'file': uploaded_file}
            ]
        }

        resp = self.client.post(urlnotam, data_notam,  format="json")
        print(resp.data, resp.headers)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, "notam create error") 
        urlsuppaip = reverse('supp-create')
        data_suppaip = {
            'start_val_period': datetime(2021, 8, 22, 8, 30, 15),
            'end_val_period': datetime(2021, 10, 22, 8, 30, 15),
            'object': "Transmission information au personnel",
            "aip_target_sections": "Secrion A",
            'attachments': [
                # {'file': uploaded_file}
            ]
        }

        resp = self.client.post(urlsuppaip, data_suppaip)
        print(resp.data)
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
        resp = self.client.post(urlsubmit, data_submit) 
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "notam submit error") 

        urlsubmit = reverse('ddia-submittoverify', kwargs={'type_ddia': 'demandesupp', 'pk': 1})
        data_submit = {
            'decision': 'submit'
        }
        resp = self.client.post(urlsubmit, data_submit)      
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "suppaip submit error") 
   
        urlsubmit = reverse('ddia-submittoverify', kwargs={'type_ddia': 'demandeaic', 'pk': 1})
        data_submit = {
            'decision': 'submit'
        }
        self.client.post(urlsubmit, data_submit)  
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "aic submit error") 

class AgentsControlsActionsTest(APITestCase):
    
    def setUp(self) -> None:
        self.user_init = User.objects.create_user(username="Nyat", email="franckhebo@gmail.com", first_name="Jean Roland", last_name="Nyatchou", password="Franck23.", role="Agent source", sex="male")
        self.user_init.is_active = True
        self.user_init.save()
        self.client_init = APIClient()
        self.client_init.force_authenticate(self.user_init)
        self.user_init1 = User.objects.create_user(username="Nyat1", email="franckhebo1@gmail.com", first_name="Jean Franck", last_name="Nyatchou", password="Franck23.", role="Agent source", sex="male")
        self.user_init1.is_active = True
        self.user_init1.save()
        self.client_init1 = APIClient()
        self.client_init1.force_authenticate(self.user_init1)
        self.user_init2 = User.objects.create_user(username="Nyat0", email="fohebo@gmail.com", password="Franck23.", role="Agent source", sex="male")
        self.user_init2.is_active = True
        self.user_init2.save()
        self.client_init2 = APIClient()
        self.client_init2.force_authenticate(self.user_init2)
        self.user_verif = User.objects.create_user(username="Lomta", email="talompatrick@gmail.com", password="Talom23.", role="Verificateur source", sex="male")
        self.user_verif.is_active = True
        self.user_verif.save()
        self.client_verif = APIClient()
        self.client_verif.force_authenticate(self.user_verif)
        self.user_commander = User.objects.create_user(username="Asa", email="joelasa@gmail.com", password="Talom23.", role="Structure source", sex="male")
        self.user_commander.is_active = True
        self.user_commander.save()
        self.client_commander = APIClient()
        self.client_commander.force_authenticate(self.user_commander)
        self.user_localinf = User.objects.create_user(username="KONRAD", email="hebogerland@gmail.com", password="Talom23.", role="Informateur local", sex="male")
        self.user_localinf.is_active = True
        self.user_localinf.save()
        self.client_localinf = APIClient()
        self.client_localinf.force_authenticate(self.user_localinf)
        self.user_nationalinf = User.objects.create_user(username="Kolo", email="hebond@gmail.com", password="Talom23.", role="Informateur national", sex="male")
        self.user_nationalinf.is_active = True
        self.user_nationalinf.save()
        self.client_nationalinf = APIClient()
        self.client_nationalinf.force_authenticate(self.user_localinf)
        nationalinf = NationalInformer.objects.create(name="CCAA")
        localinf = LocalInformer.objects.create(name="SEGC")
        aerodrome = Aerodrome.objects.create(name="Aeroport de Douala", location_ind="FKKD", is_conceded=True) 
        aerodrome2 = Aerodrome.objects.create(name="Aeroport de Yaoundé", location_ind="FKKB", is_conceded=True) 

        unit0 = Unit.objects.create(email="doualaaero0@gmail.com", name="MIRE", phone_number="+237 656556566", fax="256656", address="azertgyh", aerodrome=aerodrome) 
        unit = Unit.objects.create(email="doualaaero@gmail.com", name="AIM", phone_number="+26556566", fax="256656", address="azertgyh", aerodrome=aerodrome) 
        unit2 = Unit.objects.create(email="yaoundeaero@gmail.com", name="AIM", phone_number="+2655556566", fax="2565656", address="azertgyh", aerodrome=aerodrome2) 
        Agent.objects.create(user=self.user_init, unit=unit0, aerodrome=aerodrome)   
        Agent.objects.create(user=self.user_init1, unit=unit0, aerodrome=aerodrome)   
        Agent.objects.create(user=self.user_init2, unit=unit2, aerodrome=aerodrome2)  
        Agent.objects.create(user=self.user_verif, unit=unit, aerodrome=aerodrome)
        Agent.objects.create(user=self.user_commander, unit=unit, aerodrome=aerodrome)
        LocalAgent.objects.create(user=self.user_localinf, localinformer=localinf)
        NationalAgent.objects.create(user=self.user_nationalinf, nationalinformer=nationalinf)

    def test_controls_on_ddia(self):

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
        histories = DDIAHistory.objects.filter(user=self.user_init)
        self.assertEqual(histories.count(), 1, "no history created")
        self.assertEqual(histories.first().type_action, CREATE_ACTION, "no history for creation")

        resp = self.client_verif.post(urlcreate, data_notam)
        print(resp.data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp = self.client_commander.post(urlcreate, data_notam)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)        
        resp = self.client_localinf.post(urlcreate, data_notam)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)        
        resp = self.client_nationalinf.post(urlcreate, data_notam)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        urlsubmit = reverse('ddia-submittoverify', kwargs={'type_ddia': 'demandenotam', 'pk': 1})
        data_submit = {
            'decision': 'submit'
        }
        resp = self.client_init.post(urlsubmit, data_submit)  
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "notam submit error") 
        demandenotam = DemandeNOTAM.objects.get(id=1)
        self.assertEqual(demandenotam.state, PENDING_VERIFICATION_STATE, "demandenotam submit error") 
        self.assertEqual(SourceStructureAction.objects.filter(agent=agent, prev_state=DRAFT_STATE).count(), 1, "SourceStructureAction for initiator submit create error")
        histories = DDIAHistory.objects.filter(user=self.user_init, type_action=CONTROLE_ACTION)
        self.assertEqual(histories.count(), 1, "no history for submit")
        self.assertEqual(histories.first().type_action, CONTROLE_ACTION, "no history for submit")

        resp = self.client_init2.post(urlsubmit, data_notam)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        resp = self.client_verif.post(urlsubmit, data_notam)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        resp = self.client_init1.post(urlsubmit, data_notam)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        resp = self.client_commander.post(urlsubmit, data_notam)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)        
        resp = self.client_localinf.post(urlsubmit, data_notam)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)        
        resp = self.client_nationalinf.post(urlsubmit, data_notam)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        urlverif = reverse('ddia-verify', kwargs={'type_ddia': 'demandenotam', 'pk': 1})        
        data_accept = {
            'decision': 'accept'
        }
        resp = self.client_verif.post(urlverif+'?is_localinf=no', data_accept) 
        agent_verif = Agent.objects.get(user=self.user_verif) 
        ddia = DemandeNOTAM.objects.get(id=1) 
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "notam verification error")
        self.assertEqual(ddia.state, PENDING_ADMISSION_STATE, "notam verification error")
        self.assertEqual(SourceStructureAction.objects.filter(agent=agent_verif, prev_state=PENDING_VERIFICATION_STATE).count(), 1, "SourceStructureAction for verificator create error")
        histories = DDIAHistory.objects.filter(user=self.user_verif, type_action=CONTROLE_ACTION)
        self.assertEqual(histories.count(), 1, "no history for verif")
        history = histories.first()
        self.assertEqual(history.type_action, CONTROLE_ACTION, "no history for verif")
        self.assertEqual(history.modifshistory.all().count(), 1)

        resp = self.client_init2.post(urlverif+'?is_localinf=no', data_notam)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        resp = self.client_init.post(urlverif+'?is_localinf=no', data_notam)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        resp = self.client_commander.post(urlverif+'?is_localinf=no', data_notam)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)        
        resp = self.client_localinf.post(urlverif+'?is_localinf=no', data_notam)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)        
        resp = self.client_nationalinf.post(urlverif+'?is_localinf=no', data_notam)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        urllistddia = reverse('listDDIAprocessed-verifsource', kwargs={'type_ddia': 'notam'})
        resp = self.client_verif.get(urllistddia)
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "list ddia error")

        resp = self.client_commander.get(urllistddia)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN, "permission error")

        urladmit = reverse('ddia-admit', kwargs = {'type_ddia': 'demandenotam', 'pk': 1})
        data_accept = {
            'decision': 'accept'
        }
        resp = self.client_commander.post(urladmit+'?from_localinf=no', data_accept) 
        agent_admit = Agent.objects.get(user=self.user_commander) 
        ddia = DemandeNOTAM.objects.get(id=1) 
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "notam admission error")
        self.assertEqual(ddia.state, PENDING_VALIDATION_STATE, "notam admission error")
        self.assertEqual(SourceStructureAction.objects.filter(agent=agent_admit, prev_state=PENDING_ADMISSION_STATE).count(), 1, "SourceStructureAction for admission create error")
        histories = DDIAHistory.objects.filter(user=self.user_commander, type_action=CONTROLE_ACTION)
        self.assertEqual(histories.count(), 1, "no history for admit")
        history = histories.first()
        self.assertEqual(history.type_action, CONTROLE_ACTION, "no history created for admission")
        self.assertEqual(history.modifshistory.all().count(), 1)

        resp = self.client_init2.post(urladmit+'?from_localinf=no', data_notam)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        resp = self.client_init.post(urladmit+'?from_localinf=no', data_notam)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        resp = self.client_verif.post(urladmit+'?from_localinf=no', data_notam)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)        
        resp = self.client_localinf.post(urladmit+'?from_localinf=no', data_notam)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)        
        resp = self.client_nationalinf.post(urladmit+'?from_localinf=no', data_notam)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


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
        histories = DDIAHistory.objects.filter(user=self.user_localinf, type_action=CONTROLE_ACTION)
        self.assertEqual(histories.count(), 1, "no history for local informer")
        history = histories.first()
        self.assertEqual(history.type_action, CONTROLE_ACTION, "no history created for local informer")
        self.assertEqual(history.modifshistory.all().count(), 1)


        resp = self.client_init2.post(urlvalidate, data_notam)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        resp = self.client_init.post(urlvalidate, data_notam)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        resp = self.client_verif.post(urlvalidate, data_notam)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)        
        resp = self.client_commander.post(urlvalidate, data_notam)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)        
        resp = self.client_nationalinf.post(urlvalidate, data_notam)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


        urllistddia = reverse('listDDIAprocessed-localinformer', kwargs={'type_ddia': 'notam'})
        resp = self.client_localinf.get(urllistddia)
        self.assertEqual(resp.status_code, status.HTTP_200_OK, "list ddia error")


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

