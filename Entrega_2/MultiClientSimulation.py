import grpc
import numpy as np
# import the generated classes
import neonat_pb2 
import neonat_pb2_grpc

import random 
from threading import Thread
import sys

 

#Número de servidores
m = 3

#VARIÁVEIS GLOBAIS
ip = 'localhost'

list_medicos = []
list_pacientes = []
list_sexo = ['masculino', 'feminino']
list_parto = ['normal', 'cesaria']
list_status = ['Alta', "internado", "Obito"]

estados = ['SP', 'MG', 'AC','BA', 'AL', 'AM', 'GO', 'MA', 'MT', 'MS', 'RJ', 'RN', 'RS']

nclients = 25
ini = 4
fim = 5


#Check se existe servidor ativo
def is_port_in_use(port):
    global ip
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((ip, port)) == 0




class MultiClientSimulation():
    def __init__(self, nserver):
        self.stub, self.port = self.select_server(nserver)
        self.Commands = {
            1 : self.RegistrarPaciente,
            2 : self.RegistrarProcedimentos,
            3: self.RegistrarMedico,
            4: self.ListarPacientes,
            5: self.ListarMedicos
        }


    def RegistrarPaciente(self, i, CRM, peso, sexo, parto, idade, status, data):
        try:
            print("================= CADASTRAR PACIENTE =================\n")
            idPaciente = f"{i}"
            nomeRN = f"Teste nome paciente {i}"
            maeRN = f"Teste mae paciente {i}"
            dataHoraNasc = data
            peso = peso
            sexo = sexo
            cidadeNasc = 'Uberlandia'
            idadeGestacional = idade
            dataDiagnostico = data
            tipoParto = parto
            descricaoUTI = "UTI III"
            descricaoStatus = status
            # print('------------ INFORMAÇÕES DO MÉDICO ------------')

            # if((len(dataHoraNasc.split('-')) != 3) or (len(dataDiagnostico.split('-')) != 3)):
            #     print('Datas inseridas no formato incorreto.')
            #     self.RegistrarPaciente()

            inserirPaciente = neonat_pb2.RegistrarPacientes(pacientes = neonat_pb2.Pacientes(idPaciente=idPaciente, 
            nomeRN=nomeRN, maeRN=maeRN,
            dataHoraNasc=dataHoraNasc, peso=float(peso), sexo=neonat_pb2.Pacientes.Sexo.Value(sexo.upper()), 
            cidadeNasc = cidadeNasc, idadeGestacional=int(idadeGestacional), dataDiagnostico=dataDiagnostico,
            tipoParto=neonat_pb2.Pacientes.Parto.Value(tipoParto.upper()), descricaoUTI=descricaoUTI, descricaoStatus=descricaoStatus,
            medico=neonat_pb2.Medicos(CRM=CRM)))

            respostaInserirPaciente = self.stub.InserirPacientes(inserirPaciente)
            print(respostaInserirPaciente.resposta)
            print("===================================================\n")

        except Exception as e:
            print(f'Erro: {e}')
    def ListarPacientes(self):
        listarPacientes = neonat_pb2.TodosPacientes()
        respostaListarPacientes = self.stub.ListarPacientes(listarPacientes)
       
        if len(respostaListarPacientes.pacientes) == 0:
            print('Nenhum paciente cadastrado ainda.')
        else:
            for paciente in respostaListarPacientes.pacientes:
                if paciente.sexo == 0:
                    sexo = 'Sexo desconhecido'
                elif paciente.sexo == 1:
                    sexo = 'Feminino'
                elif paciente.sexo == 2:
                    sexo = 'Masculino'
                else:
                    sexo = ''
                
                if paciente.tipoParto == 0:
                    parto = 'Parto desconhecido'
                elif paciente.tipoParto == 1:
                    parto = 'Cesária'
                elif paciente.tipoParto == 2:
                    parto = 'Normal'

                print(f"ID Paciente: {paciente.idPaciente}")
                print('---------------------------------------------------')
                print(f'Nome do paciente: {paciente.nomeRN}')
                print(f'Nome da mãe: {paciente.maeRN}')
                print(f'Data de Nascimento: {paciente.dataHoraNasc}')
                print(f'Cidade natal: {paciente.cidadeNasc}')
                print(f'Peso: {paciente.peso}')
                print(f'Sexo: {sexo}')
                print(f'Idade Gestacional: {paciente.idadeGestacional}')
                print(f'Data Diagnostico: {paciente.dataDiagnostico}')
                print(f'Tipo do parto: {parto}')
                print(f'Descrição UTI: {paciente.descricaoUTI}')
                print(f'Descrição Status: {paciente.descricaoStatus}')
                print('------------ INFORMAÇÕES DO MÉDICO ------------')
                print(f'CRM: {paciente.medico.CRM}')
                print('---------------------------------------------------\n')

    def RegistrarProcedimentos(self, i, idPaciente):
        try:
            print("================= CADASTRAR PROCEDIMENTO UTILIZADO =================\n")
            idProcedimento = f'{i}'
            descricaoProcedimento = f"Procedimento teste cliente {i}"
            data = "05-10-2019"
            
            # if(len(data.split('-')) != 3):
            #     print('Data inserida no formato incorreto.')
            #     self.RegistrarProcedimentos()

            inserirProcedimentos = neonat_pb2.RegistrarProcedimentos(procedimentos = neonat_pb2.Procedimentos(idProcedimento=idProcedimento, 
            descricaoProcedimento=descricaoProcedimento, idPaciente=idPaciente, data=data))

            respostaInserirProcedimentos = self.stub.InserirProcedimentos(inserirProcedimentos)
            print(respostaInserirProcedimentos.resposta)
            print("===================================================\n")

        except Exception as e:
            print(f'Erro: {e}')
    

    def RegistrarMedico(self, CRM, i):
        print('============== CADASTRAR MÉDICO =============\n')
        nome = f"Teste client {i}"
        dataNasc = "10-10-1980"

        registrarMedico = neonat_pb2.RegistrarMedico(medico=neonat_pb2.Medicos(CRM=CRM,
        nome=nome, dataNasc=dataNasc))

        respostaregistrarMedico = self.stub.InserirMedico(registrarMedico)
        print(respostaregistrarMedico.resposta)

    def ListarMedicos(self):
        listarMedicos = neonat_pb2.TodosMedicos()
        respostaListarMedicos = self.stub.ListarMedicos(listarMedicos)
        print("============== MÉDICOS CADASTRADOS ==============\n")
        for medico in respostaListarMedicos.medicos:
            print('---------------------------------------------------')
            print(f'CRM: {medico.CRM}')
            print(f'Nome do médico: {medico.nome}')
            print(f'Data de nascimento: {medico.dataNasc}')
            print('---------------------------------------------------') 

    def select_server(self, m):
        stub = None
        ports = [str(50051 + i) for i in range(m)]
        ports_perm = np.random.permutation(ports)
        for i in ports_perm:
            if is_port_in_use(int(i)):
            # open a gRPC channel
                channel = grpc.insecure_channel(ip + ':' + i)

                # channel2 = grpc.insecure_channel('10.246.88.139:50052')
                # create a stub (client)
                stub = neonat_pb2_grpc.NeoNatStub(channel)
                break
        return stub, i

    


def MultiClient(i):

    global list_medicos, list_pacientes

    client = MultiClientSimulation(m)
    args = []
    if client.stub is None:
        print('Nenhum servidor ativo.')
        sys.exit()

    value = random.randint(ini, fim)
    
    
    if (value == 2) and (len(list_pacientes) == 0):
        value = 1
    
    if (value == 1) and (len(list_medicos) == 0):
        value = 3

    if value == 1:
        paciente = random.randint(1,100000)
        CRM = random.choice(list_medicos)
        peso = random.randint(1,4)
        parto = random.choice(list_parto)
        sexo = random.choice(list_sexo)
        status = random.choice(list_status)
        idade = random.randint(1,8)
        dd = random.randint(1,30)
        mm = random.randint(1,12)
        yy = random.randint(2015,2019)
        data = f'{dd}-{mm}-{yy}'
        list_pacientes.append(str(i))
        args = [paciente, CRM, peso, sexo, parto, idade, status, data]
 
        #Thread(target=obj_client[i].RegistrarPaciente, args=(i, CRM, peso, sexo, parto, idade, status, data,)).start()

    elif value == 2:
        idPaciente = random.choice(list_pacientes)
        args = [i, idPaciente]
        #Thread(target=obj_client[i].RegistrarProcedimentos, args=(i, idPaciente,)).start()

    elif value == 3:
        number = random.randint(10000, 99999)
        CRM = f'{number}-{random.choice(estados)}'
        list_medicos.append(CRM)
        args = [CRM, i]
    
    client.Commands[value](*args)
        #Thread(target=obj_client[i].RegistrarMedico, args=(CRM, i,)).start()

def run_client():
    threads = []
    for i in range(nclients):
        t = Thread(target=MultiClient, args=(i, ))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()


if __name__ == "__main__":
    run_client()