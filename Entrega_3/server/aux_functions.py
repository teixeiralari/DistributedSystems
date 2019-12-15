import sys

sys.path.insert(0, 'zatt')
from zatt.client import DistributedDict
import errno
from socket import error as socket_error
import glob
from  builtins import any as b_any
import string

n_nodes = 3

def dict_to_string(d):
    return d.__str__()

def string_to_dict(s):
    return eval(f"{s}")  

class Clusters_Servers():
    def __init__(self):
        self.finger_table = {}
        self.n_nodes = n_nodes
        self.clusters = []
        self.numbers_keys = list('123456789')
        self.getClusters()
        self.create_finger_table() 
        
    
    def IsMyData(self, port, key):
        mykeys = self.getKey(port)
        if key in list(mykeys):
            return True
        else:
            return False
    
    def getKey(self, port):
        for key, value in self.finger_table.items():
            if port in value:
                return key
        
        return None

    def create_finger_table(self):
        clusters = sorted(self.clusters)
        keys_servers = self.split()
        
        for i, value in enumerate(clusters):
            self.finger_table[''.join(keys_servers[i])] = value

    def split(self):
        k, m = divmod(len(self.numbers_keys), self.n_nodes)
        return list(self.numbers_keys[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(self.n_nodes))


    def getClusters(self):
        path_to_folder = 'zatt/*zatt_cluster*'
        paths = glob.glob(path_to_folder)
        for path in paths:
            aux = []
            with open(path + '/zatt.conf', 'r') as f:
                cluster = "".join(list(f.read().splitlines()))
                cluster = string_to_dict(cluster)
                for i in cluster['cluster']:
                    aux.append(str(i[1]))
            self.clusters.append(aux)

    def getMyCluster(self, port):
        for c in self.clusters:
            if port in c:
                return c

    def getClusterByKey(self, key):
        keys_ = [*self.finger_table.keys()]
        for i in keys_:
            if key in list(i):
                return self.finger_table[i]

 
class CRUD_Distributed():
    def __init__(self, port):
        self.data = DistributedDict('127.0.0.1', port)
    
    def set_patient(self, idPatient, nameRN, motherRN, birth, sex, age, doctor):
        # if not b_any(f'doctor:{doctor.lower()}' in x.lower() for x in self.data):
        #     return 'Doctor is not registered.'

        if f'Patient:{idPatient}' in self.data:
            return "Patient already exists."
        else:

            self.data[f'Patient:{idPatient}'] = dict_to_string(
                {
                        "nameNB" : nameRN,
                        "MotherName": motherRN,
                        "Birth": birth,
                        "Sex": sex,
                        "Age": age,
                        "Doctor": doctor,
                        "Procedure": []     
                })
            return "New patient succesfully inserted."
        

    def get_patient(self, idPatient):
        if f'Patient:{idPatient}' in [*self.data.keys()]:
            return self.data[f'Patient:{idPatient}']
        else:
            return None
       
 
    def delete_patient(self, idPatient):
        if f'Patient:{idPatient}' in [*self.data.keys()]:
            del self.data[f'Patient:{idPatient}']
            return "Patient succesfully deleted."
        else:
            return "Patient not found."

    
    def list_patients(self):
        patient = []
        keys_ = [*self.data.keys()]
        for key in keys_:
            if (key != 'cluster') and ('patient' in key.lower()):
                patient.append([key.split(':')[1], self.data[key]])
        return patient
      
    def get_procedure(self, idPatient):
        if f'Patient:{idPatient}' in [*self.data.keys()]:
            patient = string_to_dict(self.data[f'Patient:{idPatient}'])
            patient = string_to_dict(patient)
            if len(patient['Procedure']) > 0:
                return patient['Procedure']
            else:
                return None
        else:
            return "Patient not found."

    def set_procedure(self, idPatient, idProcedure, date, description):
        if f'Patient:{idPatient}' in [*self.data.keys()]:
            patient_data = self.data[f'Patient:{idPatient}']
            patient_data = string_to_dict(patient_data)

            patient_data['Procedure'].append(
                {'idProcedure': idProcedure, 'description': description, 'date': date}
                )

            self.data[f'Patient:{idPatient}'] = dict_to_string(patient_data)
            return "New procedure succesfully inserted."
        else:
            return "Patient not found."

    def set_doctor(self, CRM, name, birth):
        if f'Doctor:{CRM}' in self.data:
            return "Doctor already exists."
        else:
            self.data[f'Doctor:{CRM}'] = dict_to_string(
                {
                    "name": name,
                    "birth": birth  
                })
            return "New doctor succefully inserted."
      

    def get_doctor(self, CRM):
        if f'Doctor:{CRM}' in  [*self.data.keys()]:
            return self.data[f'Doctor:{CRM}']
        else:
            return None
       
    def list_doctors(self):
        doctors = []
        keys_ = [*self.data.keys()]
        for key in keys_:
            if (key != 'cluster') and ('doctor' in key.lower()):
                doctors.append([key.split(':')[1], self.data[key]])
        return doctors

    def list_all_patients_doctor(self, CRM):
        CRM = CRM[0:-1]
        all_patients = []
        for key, value in self.data.items():
            if CRM in value:
                all_patients.append([key.split(':')[1], self.data[key]])
        return all_patients

    def is_doctor_register(self, CRM):
        if f'Doctor:{CRM}' in [*self.data.keys()]:
            return 'yes'
        else:
            return 'no'
       

# c = Clusters_Servers()
# print(c.split())