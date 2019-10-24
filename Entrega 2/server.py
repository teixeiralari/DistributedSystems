import grpc
from concurrent import futures
import time
import json
# import the generated classes
import neonat_pb2 
import neonat_pb2_grpc
import datetime
from chord import *
import numpy as np

#NÚMEROS DE SERVIDORES
m = 4

#VARIÁVEIS GLOBAIS
ports = [str(50051 + i) for i in range(m)]
myport = ''
succesor_port = ''
ports_perm = np.random.permutation(ports)

with open('snapshot.txt') as f:
    dados = json.load(f)

server_name = 'SRV0'

keysProcedimentos = [*dados['Procedimentos'].keys()]
#countProcedimentos = max([int(x.split(server_name + 'P')[1]) for x in keysProcedimentos]) + 1
countProcedimentos = 0

channel = grpc.insecure_channel('localhost:' + succesor_port)
stub = neonat_pb2_grpc.NeoNatStub(channel)

def get_procedimento_paciente(idPaciente, idProcedimento):
    for key, value in dados['Procedimentos'].items():
        if (idPaciente == value['idPaciente']) and (idProcedimento == value['idProcedimento']):
            return key
    
    return None

def get_medico(crm):
    if crm in [*dados['Medico'].keys()]:
        return 'cadastrado'
    return 'naocadastrado'
    

def inserirPacientes(idPaciente, nomeRN, maeRN, dataHoraNasc, peso, sexo, cidadeNasc, idadeGestacional, dataDiagnostico,
tipoParto, descricaoUTI, descricaoStatus, crmMedico):
    try:
        crm = get_medico(crmMedico)
        if crm == 'naocadastrado':
            return 'Não foi possível cadastrar paciente, médico não cadastrado ou CRM inválido.'

        dados['Pacientes'][idPaciente] = {
                "Dados Pessoais" : 
                        {
                            "NomeRN" : nomeRN,
                            "NomeMae": maeRN,
                            "CidadeNascimento": cidadeNasc,
                            "DataNascimento": dataHoraNasc,
                            "Peso": peso,
                            "Sexo": sexo,
                            "IdadeGestacional": idadeGestacional,
                            "DataDiagnostico" : dataDiagnostico,
                            "TipoParto": tipoParto,
                            "descricaoUTI": descricaoUTI,
                            "descricaoStatus" : descricaoStatus,
                            "Procedimentos" : [],
                            "Medico": crmMedico                
                        }
        }

        return "Novo paciente inserido com sucesso."
    except Exception as e:
        return str(e)

def atualizarPacientes(idPaciente, nomeRN, maeRN, dataHoraNasc, peso, sexo, cidadeNasc, idadeGestacional, dataDiagnostico,
tipoParto, descricaoUTI, descricaoStatus, CRM):
    try:
        dados['Pacientes'][idPaciente]['Dados Pessoais']['NomeRN'] = nomeRN
        dados['Pacientes'][idPaciente]['Dados Pessoais']['NomeMae'] = maeRN
        dados['Pacientes'][idPaciente]['Dados Pessoais']['DataNascimento'] = dataHoraNasc
        dados['Pacientes'][idPaciente]['Dados Pessoais']['Peso'] = peso
        dados['Pacientes'][idPaciente]['Dados Pessoais']['Sexo'] = sexo
        dados['Pacientes'][idPaciente]['Dados Pessoais']['CidadeNascimento'] = cidadeNasc
        dados['Pacientes'][idPaciente]['Dados Pessoais']['IdadeGestacional'] = idadeGestacional
        dados['Pacientes'][idPaciente]['Dados Pessoais']['DataDiagnostico'] = dataDiagnostico
        dados['Pacientes'][idPaciente]['Dados Pessoais']['TipoParto'] = tipoParto
        dados['Pacientes'][idPaciente]['Dados Pessoais']['descricaoUTI'] = descricaoUTI
        dados['Pacientes'][idPaciente]['Dados Pessoais']['descricaoStatus'] = descricaoStatus
        dados['Pacientes'][idPaciente]['Dados Pessoais']['Medico'] = CRM
        return "Paciente atualizado com sucesso."
    except Exception as e:
        return str(e)

def deletarPaciente(idPaciente):
    try:
        del dados['Pacientes'][idPaciente]
        return "Paciente excluído com sucesso."
    except Exception as e:
        return str(e)

def pesquisarPaciente(idPaciente):
    nomeRN = None
    maeRN = None 
    dataHoraNasc = None
    peso = None
    sexo = None
    cidadeNasc = None
    idadeGestacional = None
    tipoParto = None
    descricaoUTI = None
    descricaoStatus = None
    dataDiagnostico = None
    CRM = None

    try:
        nomeRN = dados['Pacientes'][idPaciente]['Dados Pessoais']['NomeRN'] 
        maeRN = dados['Pacientes'][idPaciente]['Dados Pessoais']['NomeMae'] 
        dataHoraNasc = dados['Pacientes'][idPaciente]['Dados Pessoais']['DataNascimento'] 
        peso = dados['Pacientes'][idPaciente]['Dados Pessoais']['Peso'] 
        sexo = dados['Pacientes'][idPaciente]['Dados Pessoais']['Sexo'] 
        cidadeNasc = dados['Pacientes'][idPaciente]['Dados Pessoais']['CidadeNascimento'] 
        idadeGestacional = dados['Pacientes'][idPaciente]['Dados Pessoais']['IdadeGestacional'] 
        dataDiagnostico = dados['Pacientes'][idPaciente]['Dados Pessoais']['DataDiagnostico'] 
        tipoParto = dados['Pacientes'][idPaciente]['Dados Pessoais']['TipoParto'] 
        descricaoUTI = dados['Pacientes'][idPaciente]['Dados Pessoais']['descricaoUTI'] 
        descricaoStatus = dados['Pacientes'][idPaciente]['Dados Pessoais']['descricaoStatus']
        CRM = dados['Pacientes'][idPaciente]['Dados Pessoais']['Medico']
    except:
        pass
    
    return [nomeRN, maeRN, dataHoraNasc, peso, sexo, cidadeNasc, idadeGestacional, dataDiagnostico, tipoParto, 
    descricaoUTI, descricaoStatus, CRM]

def listarTodosPacientes():
    todosPacientes = []
    for key, _ in dados['Pacientes'].items():
        todosPacientes.append([key, dados['Pacientes'][key]['Dados Pessoais']['NomeRN'], 
        dados['Pacientes'][key]['Dados Pessoais']['NomeMae'], dados['Pacientes'][key]['Dados Pessoais']['DataNascimento'],
        dados['Pacientes'][key]['Dados Pessoais']['Peso'], dados['Pacientes'][key]['Dados Pessoais']['Sexo'], 
        dados['Pacientes'][key]['Dados Pessoais']['CidadeNascimento'], dados['Pacientes'][key]['Dados Pessoais']['IdadeGestacional'],
        dados['Pacientes'][key]['Dados Pessoais']['DataDiagnostico'], dados['Pacientes'][key]['Dados Pessoais']['TipoParto'],
        dados['Pacientes'][key]['Dados Pessoais']['descricaoUTI'], dados['Pacientes'][key]['Dados Pessoais']['descricaoStatus'], 
        dados['Pacientes'][key]['Dados Pessoais']['Medico']])

    return todosPacientes

def inserirProcedimentos(idProcedimento, descricaoProcedimento, idPaciente, data):
    try:

        if idPaciente not in [*dados['Pacientes'].keys()]:
            return "Não foi possível cadastrar procedimento. Paciente não encontrado."


        procedimento = get_procedimento_paciente(idPaciente, idProcedimento)

        if procedimento is not None:
            return "Procedimento já cadastrado para este paciente."

        global countProcedimentos

        dados['Procedimentos'][server_name + 'P' + str(countProcedimentos)] = {
            "idProcedimento" : idProcedimento,
            "descricaoProcedimento" : descricaoProcedimento,
            "idPaciente": idPaciente,
            "Data": data
            }

        dados['Pacientes'][idPaciente]['Dados Pessoais']['Procedimentos'].append(server_name + 'P' + str(countProcedimentos))
        countProcedimentos += 1
        return "Procedimentos inserido com sucesso."
    except Exception as e:
        return str(e)

def atualizarProcedimentos(idProcedimento, idPaciente, descricaoProcedimento, data):
    procedimento = get_procedimento_paciente(idPaciente, idProcedimento)
    try:
        dados['Procedimentos'][procedimento]["descricaoProcedimento"] = descricaoProcedimento
        dados['Procedimentos'][procedimento]["Data"] = data
        return "Procedimentos  atualizado com sucesso."
    except Exception as e:
        return str(e)

def excluirProcedimentos(idProcedimento, idPaciente):
    procedimento = get_procedimento_paciente(idPaciente, idProcedimento)
    try:
        del dados['Procedimentos'][procedimento]
        dados['Pacientes'][idPaciente]['Dados Pessoais']['Procedimentos'].remove(procedimento)
        return "Procedimentos  excluído com sucesso."
    except Exception as e:
        return str(e)

def pesquisarProcedimentos(idPaciente, idProcedimento):
    procedimento = get_procedimento_paciente(idPaciente, idProcedimento)
    descricaoProcedimento = None
    data = None
    try:
        descricaoProcedimento = dados['Procedimentos'][procedimento]['descricaoProcedimento']
        data = dados['Procedimentos'][procedimento]['Data']
    except:
        pass

    return descricaoProcedimento, data

def listarProcedimentos(idPaciente):
    todosProcedimentos = []
    nomePaciente = None
    dataNasc = None
    try:
        procedimentos = dados['Pacientes'][idPaciente]['Dados Pessoais']['Procedimentos']
        nomePaciente = dados['Pacientes'][idPaciente]['Dados Pessoais']['NomeRN']
        dataNasc = dados['Pacientes'][idPaciente]['Dados Pessoais']['DataNascimento']

        for procedimento in procedimentos:
            todosProcedimentos.append([dados['Procedimentos'][procedimento]['idProcedimento'],
            dados['Procedimentos'][procedimento]['descricaoProcedimento'],
            dados['Procedimentos'][procedimento]['idPaciente'],
            dados['Procedimentos'][procedimento]['Data']])
    except:
        pass

    return todosProcedimentos, nomePaciente, dataNasc 

def inserirMedico(CRM, nome, dataNasc):
    try:
        crm = get_medico(CRM)
        if crm == 'naocadastrado':
            dados['Medico'][CRM] = {
                "nome": nome,
                "dataNasc": dataNasc
            }

            return "Médico cadastrado com sucesso."
        else:
            return "Médico já cadastrado."
    except:
        return "Erro ao cadastrar médico."

def listarTodosMedicos():
    todosMedicos = []
    for key, _ in dados['Medico'].items():
        todosMedicos.append([key, dados['Medico'][key]['nome'], 
        dados['Medico'][key]['dataNasc']])

    return todosMedicos


def listarPacientesMedico(CRM):
    todosPacientes = []
    for key, _ in dados['Pacientes'].items():
        if dados['Pacientes'][key]['Dados Pessoais']['Medico'] == CRM:
            todosPacientes.append([key, dados['Pacientes'][key]['Dados Pessoais']['NomeRN'],
            dados['Pacientes'][key]['Dados Pessoais']['DataNascimento']])
    
    return todosPacientes

class NeonatServer(neonat_pb2_grpc.NeoNatServicer): 
    def InserirPacientes(self, request, context): #Nome do serviço
        resposta_inserir_paciente = neonat_pb2.RegistrarPacientesResposta() #Função resposta de registrar pacientes
        resposta_inserir_paciente.resposta = inserirPacientes(request.pacientes.idPaciente, request.pacientes.nomeRN, 
        request.pacientes.maeRN, request.pacientes.dataHoraNasc, request.pacientes.peso, request.pacientes.sexo, 
        request.pacientes.cidadeNasc, request.pacientes.idadeGestacional, 
        request.pacientes.dataDiagnostico, request.pacientes.tipoParto, request.pacientes.descricaoUTI, 
        request.pacientes.descricaoStatus, request.pacientes.medico.CRM)

        with open('log.txt', 'a') as log:
            log.write(f'InserirPacientes {datetime.datetime.now()} {request.usuario.usuario}\n')

        with open('snapshot.txt', 'w') as f:
            json.dump(dados, f)

        return resposta_inserir_paciente
    
    def EditarPacientes(self, request, context): #Nome do serviço
        resposta_atualizar_paciente = neonat_pb2.AtualizarPacientesResposta() #Função resposta de registrar pacientes
        resposta_atualizar_paciente.resposta = atualizarPacientes(request.pacientes.idPaciente, request.pacientes.nomeRN, request.pacientes.maeRN,
        request.pacientes.dataHoraNasc, request.pacientes.peso, request.pacientes.sexo, request.pacientes.cidadeNasc, request.pacientes.idadeGestacional, 
        request.pacientes.dataDiagnostico, request.pacientes.tipoParto, request.pacientes.descricaoUTI, request.pacientes.descricaoStatus,
        request.pacientes.medico.CRM)

        with open('log.txt', 'a') as log:
            log.write(f'EditarPacientes {datetime.datetime.now()} {request.usuario.usuario}\n')

        with open('snapshot.txt', 'w') as f:
            json.dump(dados, f)

        return resposta_atualizar_paciente

    def ExcluirPacientes(self, request, context):
        resposta_excluir_paciente = neonat_pb2.DeletarPacientesResposta()
        resposta_excluir_paciente.resposta = deletarPaciente(request.idPaciente)

        with open('log.txt', 'a') as log:
            log.write(f'ExcluirPacientes {datetime.datetime.now()} {request.usuario.usuario}\n')

        with open('snapshot.txt', 'w') as f:
            json.dump(dados, f)

        return resposta_excluir_paciente
    
    def PesquisarPacientes(self, request, context):
        result = pesquisarPaciente(request.idPaciente)
        print('Server 1')
        with open('log.txt', 'a') as log:
            log.write(f'PesquisarPacientes {datetime.datetime.now()} {request.usuario.usuario}\n')

        return neonat_pb2.ConsultarPacientesResposta(pacientes = neonat_pb2.Pacientes(
            nomeRN = result[0], maeRN = result[1], dataHoraNasc=result[2], peso=result[3], 
            sexo=result[4], cidadeNasc=result[5], idadeGestacional=result[6], 
            dataDiagnostico=result[7], 
            tipoParto=result[8], 
            descricaoUTI=result[9], 
            descricaoStatus=result[10],
            medico=neonat_pb2.Medicos(CRM=result[11])))


    def ListarPacientes(self, request, context):
        pacientes = listarTodosPacientes()
        

        todospacientes = neonat_pb2.TodosPacientesResposta()
        
        for paciente in pacientes:
            p = todospacientes.pacientes.add()
            p.idPaciente = paciente[0]
            p.nomeRN = paciente[1]
            p.maeRN = paciente[2]
            p.dataHoraNasc=paciente[3]
            p.peso=paciente[4] 
            p.sexo=paciente[5]
            p.cidadeNasc=paciente[6]
            p.idadeGestacional=paciente[7] 
            p.dataDiagnostico=paciente[8] 
            p.tipoParto=paciente[9] 
            p.descricaoUTI=paciente[10] 
            p.descricaoStatus=paciente[11]
            p.medico.CRM=paciente[12]

        with open('log.txt', 'a') as log:
            log.write(f'ListarPacientes {datetime.datetime.now()} {request.usuario.usuario}\n')

        return todospacientes


    def InserirProcedimentos(self, request, context):
        resposta_inserir_Procedimentos = neonat_pb2.RegistrarProcedimentosResposta()
        resposta_inserir_Procedimentos.resposta = inserirProcedimentos(request.procedimentos.idProcedimento, request.procedimentos.descricaoProcedimento, 
        request.procedimentos.idPaciente, request.procedimentos.data)

        with open('log.txt', 'a') as log:
            log.write(f'InserirProcedimentos {datetime.datetime.now()} {request.usuario.usuario}\n')

        with open('snapshot.txt', 'w') as snapshot:
            json.dump(dados, snapshot)


        return resposta_inserir_Procedimentos
    
    def EditarProcedimentos(self, request, context):
        resposta_atualizar_Procedimentos = neonat_pb2.AtualizarProcedimentosResposta()
        resposta_atualizar_Procedimentos.resposta = atualizarProcedimentos(request.procedimentos.idProcedimento,
        request.procedimentos.idPaciente, request.procedimentos.descricaoProcedimento, 
        request.procedimentos.data)

        with open('log.txt', 'a') as log:
           log.write(f'EditarProcedimentos {datetime.datetime.now()} {request.usuario.usuario}\n')

        with open('snapshot.txt', 'w') as f:
            json.dump(dados, f)

        return resposta_atualizar_Procedimentos

    def ExcluirProcedimentos(self, request, context):
        resposta_excluir_Procedimentos = neonat_pb2.DeletarProcedimentosResposta()
        resposta_excluir_Procedimentos.resposta = excluirProcedimentos(request.idProcedimento, request.idPaciente)
        
        with open('log.txt', 'a') as log:
           log.write(f'ExcluirProcedimentos {datetime.datetime.now()} {request.usuario.usuario}\n')

        with open('snapshot.txt', 'w') as f:
            json.dump(dados, f)

        return resposta_excluir_Procedimentos

    def PesquisarProcedimentos(self, request, context):

        with open('log.txt', 'a') as log:
           log.write(f'PesquisarProcedimentos {datetime.datetime.now()} {request.usuario.usuario}\n')


        result = pesquisarProcedimentos(request.idPaciente, request.idProcedimento)
        return neonat_pb2.ConsultarProcedimentosResposta(procedimentos = neonat_pb2.Procedimentos(
            descricaoProcedimento=result[0],
            data=result[1]
        ))
    
    def ListarProcedimentos(self, request, context):
        
        resposta_todos_procedimentos = neonat_pb2.TodosProcedimentosPacienteResposta()
        procedimentos, nomeRN, dataNasc = listarProcedimentos(request.idPaciente)
        resposta_todos_procedimentos.nomeRN = nomeRN
        resposta_todos_procedimentos.dataHoraNasc = dataNasc
       
        for procedimento in procedimentos:
            p = resposta_todos_procedimentos.procedimentos.add()
            p.idProcedimento = procedimento[0]
            p.descricaoProcedimento = procedimento[1]
            p.idPaciente = procedimento[2]
            p.data = procedimento[3]

        with open('log.txt', 'a') as log:
           log.write(f'ListarProcedimentos {datetime.datetime.now()} {request.usuario.usuario}\n')


        return resposta_todos_procedimentos
            

    def InserirMedico(self, request, context):
        resposta_inserir_Medico = neonat_pb2.RegistrarMedicoResposta()
        resposta_inserir_Medico.resposta = inserirMedico(request.medico.CRM, request.medico.nome,
        request.medico.dataNasc)

        with open('log.txt', 'a') as log:
            log.write(f'InserirMedico {datetime.datetime.now()} {request.usuario.usuario}\n')

        with open('snapshot.txt', 'w') as f:
            json.dump(dados, f)

        return resposta_inserir_Medico
    

    def ListarMedicos(self, request, context):
        medicos = listarTodosMedicos()
        

        todosMedicos = neonat_pb2.TodosMedicosResposta()
        
        for medico in medicos:
            m = todosMedicos.medicos.add()
            m.CRM = medico[0]
            m.nome = medico[1]
            m.dataNasc = medico[2]
         
        with open('log.txt', 'a') as log:
           log.write(f'ListarProcedimentos {datetime.datetime.now()} {request.usuario.usuario}\n')


        return todosMedicos

    def PesquisarPacientesMedico(self, request, context):
        pacientes = listarPacientesMedico(request.CRM)

        todosPacientesMedico = neonat_pb2.TodosPacientesMedicoResposta()
        for paciente in pacientes:
            p = todosPacientesMedico.pacientes.add()
            p.idPaciente = paciente[0]
            p.nomeRN = paciente[1]
            p.dataHoraNasc = paciente[2]

        with open('log.txt', 'a') as log:
           log.write(f'PesquisarPacientesMedico {datetime.datetime.now()} {request.usuario.usuario}\n')

        return todosPacientesMedico

    def Ola(self, request, context):
        resposta_digaola = neonat_pb2.DigaOlaReposta()
        resposta_digaola.resposta = 'Olá'
        return resposta_digaola
        

    def EnviarOla(self):
        enviarOla = neonat_pb2.DigaOla()
        global myport, stub, succesor_port, m, channel, ports_perm
        count = 0
        for i in ports_perm:
            if i != myport:
                    if is_port_in_use(int(i)):
                        succesor_port = i
                        channel = grpc.insecure_channel('localhost:' + succesor_port)
                        stub = neonat_pb2_grpc.NeoNatStub(channel)
                        respostaenviarOla = stub.Ola(enviarOla)
                        break
                    else:
                        count += 1
            
        if count == (m - 1):
            print('Sou o primeiro')
        else:
            print(respostaenviarOla.resposta)

def is_port_in_use(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def run_server():
    #create gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),
    options=(('grpc.so_reuseport', 1),))

    neonat_pb2_grpc.add_NeoNatServicer_to_server(
            NeonatServer(), server)
    
    
    global ports, myport, ports_perm, server_name, countProcedimentos
    count = 0
    

    for i in ports_perm:
        if not is_port_in_use(int(i)):
            server.add_insecure_port('[::]:' + i)
            server.start()
            break
        else:
            count += 1


    if count != m:
        myport = i
        
        server_name = server_name + myport[-1]
        NeonatServer().EnviarOla()
        

        try:
            countProcedimentos = max([int(x.split(server_name + 'P')[1]) for x in keysProcedimentos]) + 1
        except:
            pass
        
        print(f'Starting server. Listening on port {myport}.')
        
        try:
            while True:
                time.sleep(86400)
        except KeyboardInterrupt:
            server.stop(0) 
    else:
        print('Número de servidores atingido.')

if __name__ == "__main__":
    run_server()