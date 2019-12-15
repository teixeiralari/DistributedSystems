import grpc
from concurrent import futures
import time
import json
import glob, os

import neonat_pb2
import neonat_pb2_grpc
import datetime

import numpy as np
import threading


from aux_functions import *


myport = ''
#n_servers = 3
#n_replicas = 3
#ports = ['500' + str(i) for i in range(50, 50 + (n_servers * n_replicas))]
ip = 'localhost'

class NeonatServer(neonat_pb2_grpc.NeoNatServicer):
    def __init__(self):
        self.auxFunctions = Clusters_Servers()

    def InsertPatient(self, request, context): 
        
        port = '52' + myport.split('500')[1]

        if self.auxFunctions.IsMyData(port, request.patient.idPatient[0]):
            clusters = self.auxFunctions.getMyCluster(port)
            response = neonat_pb2.Response()
            print(self.auxFunctions.IsMyData(port, request.patient.doctor.CRM[0]))
            if self.auxFunctions.IsMyData(port, request.patient.doctor.CRM[0]):
                i = 0
                while True:
                    if i == len(clusters):
                        i = 0
                    try:
                        crud = CRUD_Distributed(int(clusters[i]))
                        check_doctor_register = crud.is_doctor_register(request.patient.doctor.CRM)
                        break
                    except socket_error as serr:
                        i += 1
                        if serr.errno != errno.ECONNREFUSED:
                            raise serr
            
            else:
                cluster_CRM = self.auxFunctions.getClusterByKey(request.patient.doctor.CRM[0])
                i = 0
                while True:
                    if i == len(cluster_CRM):
                        i = 0
                    try:
                        crud = CRUD_Distributed(int(cluster_CRM[i]))
                        check_doctor_register = crud.is_doctor_register(request.patient.doctor.CRM)
                        break
                    except socket_error as serr:
                        i += 1
                        if serr.errno != errno.ECONNREFUSED:
                            raise serr

            if check_doctor_register == 'yes':
                i = 0
                while True:
                    if i == len(clusters):
                        i = 0
                    try:
                        crud = CRUD_Distributed(int(clusters[i]))
                        response.response = crud.set_patient(request.patient.idPatient, request.patient.nameRN, 
                        request.patient.motherRN, 
                        request.patient.birth,request.patient.sex, 
                        request.patient.age, 
                        request.patient.doctor.CRM) 
                        break
                    except socket_error as serr:
                        i += 1
                        if serr.errno != errno.ECONNREFUSED:
                            raise serr
            
                return response
            else:
                response.response = 'Doctor not registered.'
                return response
        else:
            cluster = self.auxFunctions.getClusterByKey(request.patient.idPatient[0])
            response = self.RetransmitSet(1, cluster, request)

            return response
    

    def SearchPatient(self, request, context):
        result = None
        port = '52' + myport.split('500')[1]
        if self.auxFunctions.IsMyData(port, request.idPatient[0]):
            clusters = self.auxFunctions.getMyCluster(port)
            i = 0
            while True:
                if i == len(clusters):
                    i = 0
                try:
                    crud = CRUD_Distributed(int(clusters[i]))
                    result = crud.get_patient(request.idPatient) 
                    break
                except socket_error as serr:
                    i += 1
                    if serr.errno != errno.ECONNREFUSED:
                        raise serr

            if result:
                result = string_to_dict(result)
                return neonat_pb2.GetPatientResponse(patient = neonat_pb2.Patients(
                                nameRN=result['nameNB'], motherRN=result['MotherName'], birth=result['Birth'], 
                                age=result['Age'], sex=result['Sex'], 
                                doctor=neonat_pb2.Doctors(CRM=result['Doctor'])))
            else:
                return neonat_pb2.GetPatientResponse(patient = neonat_pb2.Patients(
                nameRN=None, motherRN=None, birth=None, 
                age=None, sex=None, 
                doctor=neonat_pb2.Doctors(CRM=None)))

        else:
            cluster = self.auxFunctions.getClusterByKey(request.idPatient[0])
            result = self.RetransmitGet(1, cluster, request)

            return neonat_pb2.GetPatientResponse(patient = neonat_pb2.Patients(
                            nameRN=result.patient.nameRN, motherRN=result.patient.motherRN, birth=result.patient.birth, 
                            age=result.patient.age, sex=result.patient.sex, 
                            doctor=neonat_pb2.Doctors(CRM=result.patient.doctor.CRM)))
      
    def DeletePatient(self, request, context):
        port = '52' + myport.split('500')[1]
        if self.auxFunctions.IsMyData(port, request.idPatient[0]):
            clusters = self.auxFunctions.getMyCluster(port)
            response = neonat_pb2.Response()
            i = 0
            while True:
                if i == len(clusters):
                    i = 0
                try:
                    crud = CRUD_Distributed(int(clusters[i]))
                    response.response = crud.delete_patient(request.idPatient) 
                    break
                except socket_error as serr:
                    i += 1
                    if serr.errno != errno.ECONNREFUSED:
                        raise serr
           
            return response
        else:
            cluster = self.auxFunctions.getClusterByKey(request.idPatient[0])
            response = self.RetransmitDelete(1, cluster, request)

            return response



    def AllPatients(self, request, context):
        all_patients = neonat_pb2.ListPatientsResponse()
        list_all_patients = []

        clusters = self.auxFunctions.clusters
        result = None
        i = 0
        count = 0
        for cluster in clusters:
            count = 0
            while True:
                if count > 100:
                    break
                if i == len(cluster):
                    i = 0
                    count += 1
                try:
                    crud = CRUD_Distributed(int(cluster[i]))
                    result = crud.list_patients()
                    break
                except socket_error:
                    i += 1
                    
            
            if result:
                for patient in result:
                    values = string_to_dict(patient[1])
                    list_all_patients.append([patient[0], values])

        for patient in list_all_patients: 
            patients = all_patients.patients.add()
            patients.idPatient = patient[0]
            patients.nameRN = patient[1]['nameNB']
            patients.motherRN = patient[1]['MotherName']
            patients.birth = patient[1]['Birth']
            patients.sex = patient[1]['Sex']
            patients.age = patient[1]['Age']
            patients.doctor.CRM = patient[1]['Doctor']
        return all_patients

    def InsertProcedure(self, request, context):
        port = '52' + myport.split('500')[1]

        if self.auxFunctions.IsMyData(port, request.procedure.idPatient[0]):
            clusters = self.auxFunctions.getMyCluster(port)
            response = neonat_pb2.Response()
            i = 0
            while True:
                if i == len(clusters):
                    i = 0
                try:
                    crud = CRUD_Distributed(int(clusters[i]))
                    response.response = crud.set_procedure(request.procedure.idPatient, request.procedure.idProcedure, 
                    request.procedure.date, 
                    request.procedure.description) 
                    break
                except socket_error as serr:
                    i += 1
                    if serr.errno != errno.ECONNREFUSED:
                        raise serr
           
            return response
        else:
            cluster = self.auxFunctions.getClusterByKey(request.procedure.idPatient[0])
            response = self.RetransmitSet(3, cluster, request)

            return response

    def SearchProcedure(self, request, context):
        port = '52' + myport.split('500')[1]

        if self.auxFunctions.IsMyData(port, request.idPatient[0]):
            clusters = self.auxFunctions.getMyCluster(port)
            all_procedures = neonat_pb2.GetProcedures()
            i = 0
            while True:
                if i == len(clusters):
                    i = 0
                try:
                    crud = CRUD_Distributed(int(clusters[i]))
                    result = crud.get_procedure(request.idPatient) 
                    break
                except socket_error as serr:
                    i += 1
                    if serr.errno != errno.ECONNREFUSED:
                        raise serr

            if result and (result != "Patient not found."):
                    for procedure in result: 
                        procedures = all_procedures.procedure.add()
                        procedures.idProcedure = procedure['idProcedure']
                        procedures.description = procedure['description']
                        procedures.date = procedure['date']
            
            elif (result == "Patient not found."):
                procedures = all_procedures.procedure.add()
                procedures.idProcedure = "Patient not found."
                procedures.description = "Patient not found."
                procedures.date = "Patient not found."

            return all_procedures
        else:
            cluster = self.auxFunctions.getClusterByKey(request.idPatient[0])
            response = self.RetransmitGet(3, cluster, request)

            return response

    def InsertDoctor(self, request, context):
        port = '52' + myport.split('500')[1]
        if self.auxFunctions.IsMyData(port, request.doctor.CRM[0]):
            clusters = self.auxFunctions.getMyCluster(port)
            i = 0
            while True:
                if i == len(clusters):
                    i = 0
                try:
                    crud = CRUD_Distributed(int(clusters[i]))
                    response = neonat_pb2.Response()
                    response.response = crud.set_doctor(request.doctor.CRM, request.doctor.name, 
                    request.doctor.birth) 
                    break
                except socket_error as serr:
                    i += 1
                    if serr.errno != errno.ECONNREFUSED:
                        raise serr
        
            
            
            return response
        else:
            cluster = self.auxFunctions.getClusterByKey(request.doctor.CRM[0])
            response = self.RetransmitSet(2, cluster, request)
            return response

        
    def SearchDoctor(self, request, context):
        result = None
        port = '52' + myport.split('500')[1]
        if self.auxFunctions.IsMyData(port, request.CRM[0]):
            clusters = self.auxFunctions.getMyCluster(port)
            i = 0
            while True:
                if i == len(clusters):
                    i = 0
                try:
                    crud = CRUD_Distributed(int(clusters[i]))
                    result = crud.get_doctor(request.CRM) 
                    break
                except socket_error as serr:
                    i += 1
                    if serr.errno != errno.ECONNREFUSED:
                        raise serr

           
            
            if result:
                result = string_to_dict(result)
                return neonat_pb2.GetDoctorResponse(doctor = neonat_pb2.Doctors(
                                name=result['name'], birth=result['birth']))
            else:
                return neonat_pb2.GetDoctorResponse(doctor = neonat_pb2.Doctors(
                name=None, birth=None))

        else:
            cluster = self.auxFunctions.getClusterByKey(request.CRM[0])
            result = self.RetransmitGet(2, cluster, request)

            return neonat_pb2.GetDoctorResponse(doctor = neonat_pb2.Doctors(
                            name=result.doctor.name, birth=result.doctor.birth))

    def AllDoctors(self, request, context):
        all_doctors = neonat_pb2.ListDoctorsResponse()
        list_all_doctors = []

        clusters = self.auxFunctions.clusters
        result = None
        i = 0
        count = 0
        for cluster in clusters:
            count = 0
            while True:
                if count > 100:
                    break
                if i == len(cluster):
                    i = 0
                    count += 1
                try:
                    crud = CRUD_Distributed(int(cluster[i]))
                    result = crud.list_doctors()
                    break
                except socket_error:
                    i += 1
                    
            
            if result:
                for doctor in result:
                    values = string_to_dict(doctor[1])
                    list_all_doctors.append([doctor[0], values])

        for doctor in list_all_doctors: 
            doctors = all_doctors.doctors.add()
            doctors.CRM = doctor[0]
            doctors.name = doctor[1]['name']
            doctors.birth = doctor[1]['birth']
        return all_doctors


    # def AllPatientsDoctor(self, request, context):
    #     result = None
    #     port = '52' + myport.split('500')[1]
    #     all_patients_doctor = neonat_pb2.ListPatientsResponse()
    #     if self.auxFunctions.IsMyData(port, request.CRM[-1]):
    #         clusters = self.auxFunctions.getMyCluster(port)
    #         i = 0
    #         while True:
    #             if i == len(clusters):
    #                 i = 0
    #             try:
    #                 crud = CRUD_Distributed(int(clusters[i]))
    #                 result = crud.list_all_patients_doctor(request.CRM) 
    #                 break
    #             except socket_error as serr:
    #                 i += 1
    #                 if serr.errno != errno.ECONNREFUSED:
    #                     raise serr

           
            
    #         if result:
    #             for patient in result:
    #                 patients = all_patients_doctor.patients.add()
    #                 patients.idPatient = patient[0]
    #                 patients.nameRN = patient[1]['nameNB']
    #                 patients.motherRN = patient[1]['MotherName']
    #                 patients.birth = patient[1]['Birth']
    #                 patients.sex = patient[1]['Sex']
    #                 patients.age = patient[1]['Age']
    #                 patients.doctor.CRM = patient[1]['Doctor']

    #     else:
    #         cluster = self.auxFunctions.getClusterByKey(request.CRM[-1])
    #         result = self.RetransmitGet(4, cluster, request)

    #         return result

    def RetransmitSet(self, type, cluster, request):
        if type == 1:
            for server in cluster:
                if is_port_in_use(int('500' + server[2::])):
                    channel = grpc.insecure_channel(ip + ':' + '500' + server[2::])
                    stub = neonat_pb2_grpc.NeoNatStub(channel)

                    setPatient = neonat_pb2.SetPatient(patient = neonat_pb2.Patients(idPatient=request.patient.idPatient, 
                    nameRN=request.patient.nameRN, motherRN=request.patient.motherRN, birth=request.patient.birth, 
                    age=request.patient.age, sex=request.patient.sex, 
                    doctor=neonat_pb2.Doctors(CRM=request.patient.doctor.CRM)))
                    
                    response = stub.InsertPatient(setPatient)
                    break

            return response
        elif type == 2:
            for server in cluster:
                if is_port_in_use(int('500' + server[2::])):
                    channel = grpc.insecure_channel(ip + ':' + '500' + server[2::])
                    stub = neonat_pb2_grpc.NeoNatStub(channel)

                    setDoctor = neonat_pb2.SetDoctor(doctor = neonat_pb2.Doctors(CRM=request.doctor.CRM, 
                    name=request.doctor.name, birth=request.doctor.birth))

                    response = stub.InsertDoctor(setDoctor)
                    break
            return response
        elif type == 3:
            for server in cluster:
                if is_port_in_use(int('500' + server[2::])):
                    channel = grpc.insecure_channel(ip + ':' + '500' + server[2::])
                    stub = neonat_pb2_grpc.NeoNatStub(channel)

                    procedure = neonat_pb2.SetProcedure(procedure = neonat_pb2.Procedure(idProcedure=request.procedure.idProcedure, 
                    description=request.procedure.description, idPatient=request.procedure.idPatient, date=request.procedure.date))
                    response = stub.InsertProcedure(procedure)
                    break
            return response

    
    def RetransmitGet(self, type, cluster, request):
        response = None
        if type == 1:
            for server in cluster:
                if is_port_in_use(int('500' + server[2::])):
                    channel = grpc.insecure_channel(ip + ':' + '500' + server[2::])
                    stub = neonat_pb2_grpc.NeoNatStub(channel)
                    getPatient = neonat_pb2.GetPatient(idPatient=request.idPatient)
                    response = stub.SearchPatient(getPatient)
                    break

            return response

        elif type == 2:
            for server in cluster:
                if is_port_in_use(int('500' + server[2::])):
                    channel = grpc.insecure_channel(ip + ':' + '500' + server[2::])
                    stub = neonat_pb2_grpc.NeoNatStub(channel)
                    getDoctor = neonat_pb2.GetDoctor(CRM=request.CRM)
                    response = stub.SearchDoctor(getDoctor)
                    break

            return response
        
        elif type == 3:
            for server in cluster:
                if is_port_in_use(int('500' + server[2::])):
                    channel = grpc.insecure_channel(ip + ':' + '500' + server[2::])
                    stub = neonat_pb2_grpc.NeoNatStub(channel)
                    patient = neonat_pb2.Procedure(idPatient = request.idPatient)
                    response = stub.SearchProcedure(patient)
            return response

        elif type == 4:
            for server in cluster:
                if is_port_in_use(int('500' + server[2::])):
                    channel = grpc.insecure_channel(ip + ':' + '500' + server[2::])
                    stub = neonat_pb2_grpc.NeoNatStub(channel)

                    listpatients = neonat_pb2.GetDoctor(CRM=request.CRM)
                    response = stub.AllPatientsDoctor(listpatients)
                    break

            return response


    def RetransmitDelete(self, type, cluster, request):
        response = None
        if type == 1:
            for server in cluster:
                if is_port_in_use(int('500' + server[2::])):
                    channel = grpc.insecure_channel(ip + ':' + '500' + server[2::])
                    stub = neonat_pb2_grpc.NeoNatStub(channel)

                    deletePatient = neonat_pb2.GetPatient(idPatient=request.idPatient)
                    
                    response = stub.DeletePatient(deletePatient)
                    break

            return response

    def CheckDoctorRegister(self, CRM):
        cluster = self.auxFunctions.getClusterByKey(request.CRM[-1])

def is_port_in_use(port):
    global ip
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((ip, port)) == 0

def run_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),
    options=(('grpc.so_reuseport', 1),))

    neonat_pb2_grpc.add_NeoNatServicer_to_server(
            NeonatServer(), server)

    global myport

    # for port in ports:
    #     if not is_port_in_use(int(port)):
    
    myport = os.environ.get('SERVER_PORT')
    server.add_insecure_port('[::]:' + myport)
    server.start()
            # break

    print(f'Starting server. Listening on port {myport}.')
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        server.stop(0) 
  
if __name__ == "__main__":
    run_server()