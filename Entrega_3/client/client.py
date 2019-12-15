import grpc
import numpy as np
# import the generated classes
import neonat_pb2 
import neonat_pb2_grpc

#Número de servidores
n_servers = 3
n_replicas = 3
#VARIÁVEIS GLOBAIS
ports = ['500' + str(i) for i in range(50, 50 + (n_servers*n_replicas))]
ports_perm = np.random.permutation(ports)

ip = 'localhost'

def is_port_in_use(port):
    global ip
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((ip, port)) == 0

for i in ports_perm:
    if is_port_in_use(int(i)):
        # open a gRPC channel
        channel = grpc.insecure_channel(ip + ':' + i)
        stub = neonat_pb2_grpc.NeoNatStub(channel)
        break

print('Connected to server on port: ' + i + '\n')

class Client():
    def menu(self):
        print('================= MENU =================\n')
        print('======= PACIENTES =======')
        print('1: Insert Patient.') #ok
        print('2: Delete Patient.') #ok
        print('3: Search Patient.') #ok
        print('4: List all patients.') #ok
        print('======= PROCEDIMENTOS =======')
        print('5: Insert Procedure.') #ok
        print('6: List all procedures of a patient.') #ok
        print('======= MÉDICOS =======')
        print('7: Insert Doctor.') #ok
        print('8: Search Doctor.') #ok
        print('9: List all doctors.') #ok
        #print("10: List all patients of a doctor.") #ok
        print('========== OUTROS ==========')
        print('0: Quit')
        print('menu: Show menu.')

    def InsertPatient(self):
        try:
            print("================= INSERT PATIENT =================\n")
            idPatient = input('ID Patient: ')

            nameRN = input("Patient's name: ")
            motherRN = input("Mother's name: ")
            birth = input('Date of birth (DD-MM-YYYY): ')
            sex = input("Patient's gender (Female/Male): ")
            age = input('Age: ')
            print('------------ DOCTOR INFORMATION ------------')
            CRM = input('CRM (xxxxx-UF): ')

            if((len(birth.split('-')) != 3) or (len(birth.split('-')) != 3)):
                print('Date in incorrect format.')
                self.InsertPatient()

            setPatient = neonat_pb2.SetPatient(patient = neonat_pb2.Patients(idPatient=idPatient, 
            nameRN=nameRN, motherRN=motherRN, birth=birth, age=int(age), 
            sex=neonat_pb2.Patients.Sex.Value(sex.upper()), 
            doctor=neonat_pb2.Doctors(CRM=CRM)))

            response = stub.InsertPatient(setPatient)
            print(response.response)
            print("===================================================\n")

        except Exception as e:
            print(f'Erro: {e}')

    def SearchPatient(self):
        try:
            print("================= SEARCH PATIENT =================\n")
            idPatient = input('ID Patient: ')
            getPatient = neonat_pb2.GetPatient(idPatient = idPatient)

            response = stub.SearchPatient(getPatient)
            if response.patient.nameRN:
                print(f"Patient's name: {response.patient.nameRN}")
                print(f"Mother's name: {response.patient.motherRN}")
                print(f'Date of birth: {response.patient.birth}')
                if response.patient.sex == 0:
                    sex = 'Unknown'
                elif response.patient.sex == 1:
                    sex = 'Female'
                else:
                    sex = 'Male'
                print(f"Patient's gender: {sex}")
                print(f'Age: {response.patient.age}')
                print('------------ DOCTOR INFORMATION ------------')
                print(f'CRM: {response.patient.doctor.CRM}')

            else:
                print('Patient not found.')
        except Exception as e:
            print(f'Erro: {e}')

    def DeletePatient(self):
        try:
            print("================= DELETE PATIENT =================\n")
            idPatient = input('ID Patient: ')
            getPatient = neonat_pb2.GetPatient(idPatient = idPatient)
            response = stub.DeletePatient(getPatient)
            print(response.response)
        except Exception as e:
            print(f'Erro: {e}')

    def AllPatients(self):
        try:
            listpatients = neonat_pb2.List()
            response = stub.AllPatients(listpatients)
            for patient in response.patients:
                print(f'ID Patient: {patient.idPatient}')
                print(f"Patient's name: {patient.nameRN}")
                print(f"Mother's name: {patient.motherRN}")
                print(f'Date of birth: {patient.birth}')
                if patient.sex == 0:
                    sex = 'Unknown'
                elif patient.sex == 1:
                    sex = 'Female'
                else:
                    sex = 'Male'
                print(f"Patient's gender: {sex}")
                print(f'Age: {patient.age}')
                print('------------ DOCTOR INFORMATION ------------')
                print(f'CRM: {patient.doctor.CRM}')
                print('-----------------------------------------------')
                print("________________________________________________")
        except Exception as e:
            print(f'Erro: {e}')

    def InsertProcedure(self):
        try:
            print("================= INSERT PROCEDURE =================\n")
            idProcedure = input('ID Procedure: ')
            description = input('Description: ')
            idPatient = input('ID Patient: ')

            date = input('Date (DD-MM-YYY): ')

            procedure = neonat_pb2.SetProcedure(procedure = neonat_pb2.Procedure(idProcedure=idProcedure, 
            description=description, idPatient=idPatient, date=date))

            response = stub.InsertProcedure(procedure)
            print(response.response)
            print("===================================================\n")

        except Exception as e:
            print(f'Erro: {e}')

    def SearchProcedures(self):
        try:
            idPatient = input('ID Patient: ')
            patient = neonat_pb2.Procedure(idPatient = idPatient)
            response = stub.SearchProcedure(patient)
            if len(response.procedure) > 0:
                    for procedure in response.procedure:
                        if procedure.idProcedure == "Patient not found.":
                            print("Patient not found.")
                            break
                        else:
                            print(f'ID Procedure: {procedure.idProcedure}')
                            print(f'Description: {procedure.description}')
                            print(f'Date: {procedure.date}')
                            print('--------------------------------------')
            else:
                print('No procedures entered yet.')
        except Exception as e:
            print(f'Erro: {e}')

    def InsertDoctor(self):
        try:
            print("================= INSERT DOCTOR =================\n")
            CRM = input('CRM: ')

            name = input("Doctor's name: ")
            birth = input('Date of birth (DD-MM-YYYY): ')

            if((len(birth) != 10) and (len(birth.split('-')) != 3)):
                print('Date in incorrect format.')
                self.InsertDoctor()

            setDoctor = neonat_pb2.SetDoctor(doctor = neonat_pb2.Doctors(CRM=CRM, 
            name=name, birth=birth))

            response = stub.InsertDoctor(setDoctor)
            print(response.response)
            print("===================================================\n")

        except Exception as e:
            print(f'Erro: {e}')


    def SearchDoctor(self):
        try:
            print("================= SEARCH DOCTOR =================\n")
            CRM = input('CRM: ')
            getDoctor = neonat_pb2.GetDoctor(CRM = CRM)

            response = stub.SearchDoctor(getDoctor)
            if response.doctor.name:
                print(f"Doctor's name: {response.doctor.name}")
                print(f'Date of birth: {response.doctor.birth}')
            else:
                print('Doctor not found.')
        except Exception as e:
            print(f'Erro: {e}')
    
    def AllDoctors(self):
        try:
            listdoctors = neonat_pb2.List()
            response = stub.AllDoctors(listdoctors)
            for doctor in response.doctors:
                print(f"Doctor's name: {doctor.name}")
                print(f"CRM: {doctor.CRM}")
                print(f"Date of birth: {doctor.birth}")
                print('-----------------------------------------------')
        except Exception as e:
            print(f'Erro: {e}')


    # def AllPatientsDoctor(self):
    #     try:
    #         CRM = input('CRM: ')

    #         listpatients = neonat_pb2.GetDoctor(CRM=CRM)
    #         response = stub.AllPatientsDoctor(listpatients)
    #         for patient in response.patients:
    #             print(f'ID Patient: {patient.idPatient}')
    #             print(f"Patient's name: {patient.nameRN}")
    #             print(f"Mother's name: {patient.motherRN}")
    #             print(f'Date of birth: {patient.birth}')
    #             if patient.sex == 0:
    #                 sex = 'Unknown'
    #             elif patient.sex == 1:
    #                 sex = 'Female'
    #             else:
    #                 sex = 'Male'
    #             print(f"Patient's gender: {sex}")
    #             print(f'Age: {patient.age}')
    #             print('-------------------------------------------------')
    #     except Exception as e:
    #         print(f'Erro: {e}')

def run_client():
    client = Client()
    client.menu()
    while True:
        try:
            print('\n')
            command = input('Type your option: ')
            print('\n\n')
            if command == '0':
                break
            elif command == 'menu':
                client.menu()
            elif command == '1':
                client.InsertPatient()
            elif command == '2':
                client.DeletePatient()
            elif command == '3':
                client.SearchPatient()
            elif command == '4':
                client.AllPatients()
            elif command == '5':
                client.InsertProcedure()
            elif command == '6':
                client.SearchProcedures()
            elif command == '7':
                client.InsertDoctor()
            elif command == '8':
                client.SearchDoctor()
            elif command == '9':
                client.AllDoctors()
            # elif command == '10':
            #     client.AllPatientsDoctor()
            else:
                print('Invalid command.')
                pass
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f'Error: {e}. Try again.')
            pass
        

if __name__ == "__main__":
    run_client()