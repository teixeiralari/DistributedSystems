import grpc
from concurrent import futures
import time
import json

import neonat_pb2 
import neonat_pb2_grpc
import datetime

import numpy as np
import threading
import glob, os
#NÚMEROS DE SERVIDORES
m = 4

#VARIÁVEIS GLOBAIS
ports = [str(50051 + i) for i in range(m)]
myport = ''
succesor_port = ''
ports_perm = np.random.permutation(ports)
countProcedimentos = 0

server_name = 'SRV0'

ip = 'localhost'
channel = grpc.insecure_channel(ip + ':' + succesor_port)
stub = neonat_pb2_grpc.NeoNatStub(channel)

log_name = ''
snapshot_name = ''
dados = {'Pacientes': {}, "Procedimentos":{}, "Medico": {}, "Dados a enviar" : {}}


hashs_servidores = {}

def getServidor(id_, by):
    # keys_ = [*hashs_servidores.keys()]
    if by == 'idPaciente':
        for key, value in hashs_servidores.items():
            ids = value['IDs Pacientes']
            if id_ in ids:
                return key

    elif by == 'CRM':
        for key, value in hashs_servidores.items():
            ids = value['IDs Medicos']
            if id_ in ids:
                return key


    return None

def getTodosIDs():
    keys_ = [*hashs_servidores.keys()]
    ids_pacientes = []
    ids_medicos = []
    ids_procedimentos = []

    for i in keys_:
        pacientes = hashs_servidores[i]['IDs Pacientes']
        medicos = hashs_servidores[i]['IDs Medicos']
        [ids_pacientes.append(x) for x in pacientes]
        [ids_medicos.append(x) for x in medicos]
    
    
    for servidor in keys_:
        procedimentos = hashs_servidores[servidor]['IDs Procedimentos']
        for i in procedimentos:
            ids_procedimentos.append([i['idProcedimento'], i['idPaciente']])

    return ids_pacientes, ids_procedimentos, ids_medicos

def getHashs():
    pacientes = [*dados['Pacientes'].keys()]
    procedimentos = []
    for _, value in dados['Procedimentos'].items():
        procedimentos.append([value['idPaciente'], value['idProcedimento']])
    
    #procedimentos = [*dados['Procedimentos'].keys()]
    medicos = [*dados['Medico'].keys()]

    return pacientes, procedimentos, medicos

def get_procedimento_paciente(idPaciente, idProcedimento):

    global hashs_servidores
    for key, value in dados['Procedimentos'].items():
        if (idPaciente == value['idPaciente']) and (idProcedimento == value['idProcedimento']):
            return key
    

    for key, value in hashs_servidores.items():
        for v in value['IDs Procedimentos']:
            if (idPaciente == v['idPaciente']) and (idProcedimento == v['idProcedimento']):
                return key

    return None

def get_medico(crm):
    _, _, ids_servidores = getTodosIDs()

    if (crm in [*dados['Medico'].keys()]):
        return 'cadastrado'
    if (crm in ids_servidores):
        return 'cadastrado+'

    return 'naocadastrado'
    

def inserirPacientes(idPaciente, nomeRN, maeRN, dataHoraNasc, peso, sexo, cidadeNasc, idadeGestacional, dataDiagnostico,
tipoParto, descricaoUTI, descricaoStatus, crmMedico):
    try:
        crm = get_medico(crmMedico)

        if 'Dados a enviar' not in [*dados.keys()]:
            dados['Dados a enviar'] = {}


        hashs_pacientes, _, _ = getTodosIDs()
        my_pacientes = [*dados['Pacientes'].keys()]
        if (idPaciente not in hashs_pacientes) and (idPaciente not in my_pacientes):
            if crm == 'naocadastrado':
                return 'Não foi possível cadastrar paciente, médico não cadastrado ou CRM inválido.'

            elif crm == 'cadastrado+':
                servidor = getServidor(crmMedico, by='CRM')
                if (servidor is not None) and  (servidor != server_name):
                    if servidor not in [*dados['Dados a enviar'].keys()]:
                        dados['Dados a enviar'][servidor] = {}
                        dados['Dados a enviar'][servidor] = {
                            'Procedimentos': {},
                            'Pacientes' : {},
                        }
                
                dados['Dados a enviar'][servidor]['Pacientes']\
                    [idPaciente] = {
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
                                "Medico": crmMedico,
                                "comando": "InserirPaciente"               
                            }

                return "Novo paciente inserido com sucesso."
            else:
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
        else:
            return "Paciente já cadastrado."    
    except Exception as e:
        return str(e)

def atualizarPacientes(idPaciente, nomeRN, maeRN, dataHoraNasc, peso, sexo, cidadeNasc, idadeGestacional, dataDiagnostico,
tipoParto, descricaoUTI, descricaoStatus, CRM):
    crm = get_medico(CRM)

    if 'Dados a enviar' not in [*dados.keys()]:
            dados['Dados a enviar'] = {}

    if crm == 'cadastrado+':
        servidor = getServidor(CRM, by='CRM')
       
        if (servidor is not None):
            if servidor not in [*dados['Dados a enviar'].keys()]:
                dados['Dados a enviar'][servidor] = {}
                dados['Dados a enviar'][servidor] = {
                    'Procedimentos': {},
                    'Pacientes' : {},
                }
        
        dados['Dados a enviar'][servidor]['Pacientes']\
            [idPaciente] = {
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
                        "Medico": CRM,
                        "comando": "AtualizarPaciente"               
                    }
        return "Paciente atualizado com sucesso." 

    elif crm == 'cadastrado':
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
    else:
        return "Médico não cadastrado."

def deletarPaciente(idPaciente):
    servidor = getServidor(idPaciente, 'idPaciente')

    if 'Dados a enviar' not in [*dados.keys()]:
            dados['Dados a enviar'] = {}

    hashs_pacientes, _, _ = getTodosIDs()
    my_pacientes = [*dados['Pacientes'].keys()]

    if (idPaciente in hashs_pacientes):# or (my_pacientes in my_pacientes):
        #if (servidor is not None) and  (servidor != server_name):
        if servidor not in [*dados['Dados a enviar'].keys()]:
            dados['Dados a enviar'][servidor] = {}
            dados['Dados a enviar'][servidor] = {
                'Procedimentos': {},
                'Pacientes' : {},
            }
    
        dados['Dados a enviar'][servidor]['Pacientes']\
        [idPaciente] = {
                    "comando": "ExcluirPaciente"               
                    }
        return "Paciente excluído com sucesso."
    elif (idPaciente in my_pacientes):
        try:
            del dados['Pacientes'][idPaciente]
            return "Paciente excluído com sucesso."
        except Exception as e:
            return str(e)
    else:
        return "Paciente não encontrado"

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

    servidor = getServidor(idPaciente, 'idPaciente')
    if servidor is not None:
        port = '5005' + servidor.split('SRV0')[1]
        if is_port_in_use(int(port)):
            consultarPaciente = neonat_pb2.ConsultarPacientes(idPaciente=idPaciente)
            channel = grpc.insecure_channel(ip + ':' +  port)
            stub = neonat_pb2_grpc.NeoNatStub(channel)
            respostaconsultarPaciente = stub.PesquisarPacientes(consultarPaciente)

            nomeRN = respostaconsultarPaciente.pacientes.nomeRN
            maeRN = respostaconsultarPaciente.pacientes.maeRN
            dataHoraNasc = respostaconsultarPaciente.pacientes.dataHoraNasc
            peso = respostaconsultarPaciente.pacientes.peso 
            sexo = respostaconsultarPaciente.pacientes.sexo
            cidadeNasc = respostaconsultarPaciente.pacientes.cidadeNasc
            idadeGestacional = respostaconsultarPaciente.pacientes.idadeGestacional
            dataDiagnostico = respostaconsultarPaciente.pacientes.dataDiagnostico
            tipoParto = respostaconsultarPaciente.pacientes.tipoParto
            descricaoUTI = respostaconsultarPaciente.pacientes.descricaoUTI
            descricaoStatus = respostaconsultarPaciente.pacientes.descricaoStatus
            CRM = respostaconsultarPaciente.pacientes.medico.CRM
        else:
            nomeRN = "Dados não disponíveis no momento"
            maeRN = "Dados não disponíveis no momento"
            dataHoraNasc = "Dados não disponíveis no momento"
            peso = 0
            sexo = 0
            cidadeNasc = "Dados não disponíveis no momento"
            idadeGestacional = 0
            dataDiagnostico = "Dados não disponíveis no momento"
            tipoParto = 0
            descricaoUTI = "Dados não disponíveis no momento"
            descricaoStatus = "Dados não disponíveis no momento"
            CRM = "Dados não disponíveis no momento"
    else: 
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

def listarTodosPacientes(nome_servidor):
    global server_name

    todosPacientes = []

    if (len(nome_servidor) == 0) or (server_name == nome_servidor):
        for i in ports_perm:
            if (i != myport) and (is_port_in_use(int(i))):
                listarPacientes = neonat_pb2.TodosPacientes(nome_servidor=server_name)
                channel = grpc.insecure_channel(ip  + ':' + i)
                stub = neonat_pb2_grpc.NeoNatStub(channel)
                respostaListarPacientes = stub.ListarPacientes(listarPacientes)
                
                if len(respostaListarPacientes.pacientes) > 0:
                    for paciente in respostaListarPacientes.pacientes:
                        todosPacientes.append([paciente.idPaciente, paciente.nomeRN, 
                        paciente.maeRN, paciente.dataHoraNasc,
                        paciente.peso, paciente.sexo, 
                        paciente.cidadeNasc, paciente.idadeGestacional,
                        paciente.dataDiagnostico, paciente.tipoParto,
                        paciente.descricaoUTI, paciente.descricaoStatus, 
                        paciente.medico.CRM])
            else:
                servidor = 'SRV0' + i.split('5005')[1]
                for key, value in hashs_servidores.items():
                    if key == servidor:
                        for v in value['IDs Pacientes']:

                            todosPacientes.append([v, "Dados não disponíveis no momento", 
                            "Dados não disponíveis no momento", "Dados não disponíveis no momento",
                            0, 0, 
                            "Dados não disponíveis no momento", 0,
                            "Dados não disponíveis no momento", 0,
                            "Dados não disponíveis no momento", "Dados não disponíveis no momento", 
                            "Dados não disponíveis no momento"])


        for key, _ in dados['Pacientes'].items():
            todosPacientes.append([key, dados['Pacientes'][key]['Dados Pessoais']['NomeRN'], 
            dados['Pacientes'][key]['Dados Pessoais']['NomeMae'], dados['Pacientes'][key]['Dados Pessoais']['DataNascimento'],
            dados['Pacientes'][key]['Dados Pessoais']['Peso'], dados['Pacientes'][key]['Dados Pessoais']['Sexo'], 
            dados['Pacientes'][key]['Dados Pessoais']['CidadeNascimento'], dados['Pacientes'][key]['Dados Pessoais']['IdadeGestacional'],
            dados['Pacientes'][key]['Dados Pessoais']['DataDiagnostico'], dados['Pacientes'][key]['Dados Pessoais']['TipoParto'],
            dados['Pacientes'][key]['Dados Pessoais']['descricaoUTI'], dados['Pacientes'][key]['Dados Pessoais']['descricaoStatus'], 
            dados['Pacientes'][key]['Dados Pessoais']['Medico']])
    else:
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
    global countProcedimentos

    try:
        
        servidor = getServidor(idPaciente, 'idPaciente')
        paciente, _, _ = getTodosIDs()
        procedimento = get_procedimento_paciente(idPaciente, idProcedimento)

        #MODIFICAÇÃO ==================================
        if 'Dados a enviar' not in [*dados.keys()]:
            dados['Dados a enviar'] = {
                # 'Procedimentos': {},
                # 'Pacientes' : {},
                # 'Medico' : {}
            }

        if (idPaciente not in [*dados['Pacientes'].keys()]) and (idPaciente not in paciente):
            return "Não foi possível cadastrar procedimento. Paciente não encontrado."

        elif procedimento is not None:
            return "Procedimento já cadastrado para este paciente."

        

        elif (servidor is not None) and  (servidor != server_name):
            if servidor not in [*dados['Dados a enviar'].keys()]:
                dados['Dados a enviar'][servidor] = {}
                dados['Dados a enviar'][servidor] = {
                    'Procedimentos': {},
                    'Pacientes' : {},
                }
            
            dados['Dados a enviar'][servidor]['Procedimentos']\
                [server_name + 'P' + str(countProcedimentos)] = {
                    "idProcedimento" : idProcedimento,
                    "descricaoProcedimento" : descricaoProcedimento,
                    "idPaciente": idPaciente,
                    "Data": data,
                    "comando" : "InserirProcedimento"
                    }


            countProcedimentos += 1
            return "Procedimentos inserido com sucesso."
        else:
        #============================================================
        
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
    global countProcedimentos

    procedimento = get_procedimento_paciente(idPaciente, idProcedimento)
    servidor = getServidor(idPaciente, 'idPaciente')
    #MODIFICAÇÃO
    if 'Dados a enviar' not in [*dados.keys()]:
            dados['Dados a enviar'] = {}

    if (servidor is not None) and  (servidor != server_name):
            if servidor not in [*dados['Dados a enviar'].keys()]:
                dados['Dados a enviar'][servidor] = {}
                dados['Dados a enviar'][servidor] = {
                    'Procedimentos': {},
                    'Pacientes' : {},
                }
            
            dados['Dados a enviar'][servidor]['Procedimentos']\
                [server_name + 'P' + str(countProcedimentos)] = {
                    "idProcedimento" : idProcedimento,
                    "descricaoProcedimento" : descricaoProcedimento,
                    "idPaciente": idPaciente,
                    "Data": data,
                    "comando" : "AtualizarProcedimento"
                    }


            countProcedimentos += 1
            return "Procedimento atualizado com sucesso."
    else:
        #===========================================
        try:
            dados['Procedimentos'][procedimento]["descricaoProcedimento"] = descricaoProcedimento
            dados['Procedimentos'][procedimento]["Data"] = data
            return "Procedimento atualizado com sucesso."
        except Exception as e:
            return str(e)

def excluirProcedimentos(idProcedimento, idPaciente):
    global countProcedimentos

    procedimento = get_procedimento_paciente(idPaciente, idProcedimento)
    servidor = getServidor(idPaciente, 'idPaciente')

    if 'Dados a enviar' not in [*dados.keys()]:
            dados['Dados a enviar'] = {}

    if (servidor is not None):
        if servidor not in [*dados['Dados a enviar'].keys()]:
            dados['Dados a enviar'][servidor] = {}
            dados['Dados a enviar'][servidor] = {
                'Procedimentos': {},
                'Pacientes' : {},
            }
        dados['Dados a enviar'][servidor]['Procedimentos']\
            [server_name + 'P' + str(countProcedimentos)] = {
                "idProcedimento" : idProcedimento,
                "idPaciente": idPaciente,
                "comando" : "ExcluirProcedimento"
                }

        countProcedimentos += 1
        return "Procedimentos  excluído com sucesso."
    else:
    
        try:
            del dados['Procedimentos'][procedimento]
            dados['Pacientes'][idPaciente]['Dados Pessoais']['Procedimentos'].remove(procedimento)
            return "Procedimentos  excluído com sucesso."
        except Exception as e:
            return str(e)

def pesquisarProcedimentos(idPaciente, idProcedimento):
    procedimento = get_procedimento_paciente(idPaciente, idProcedimento)
    servidor = getServidor(idPaciente, 'idPaciente')

    descricaoProcedimento = None
    data = None

    if (procedimento is not None) and (servidor is None):
        descricaoProcedimento = dados['Procedimentos'][procedimento]['descricaoProcedimento']
        data = dados['Procedimentos'][procedimento]['Data']
    
    elif (servidor is not None):
        port = '5005' + procedimento[-1]

        if is_port_in_use(int(port)):
            consultarProcedimentos = neonat_pb2.ConsultarProcedimentos(idPaciente=idPaciente, 
            idProcedimento=idProcedimento)
            channel = grpc.insecure_channel(ip + ':' + port)
            stub = neonat_pb2_grpc.NeoNatStub(channel)
        
            respostaConsultarProcedimentos = stub.PesquisarProcedimentos(consultarProcedimentos)
            descricaoProcedimento = respostaConsultarProcedimentos.procedimentos.descricaoProcedimento
            data = respostaConsultarProcedimentos.procedimentos.data
        else:
            descricaoProcedimento = 'Dado não disponível'
            data = 'Dado não disponível'

    return descricaoProcedimento, data

def listarProcedimentos(idPaciente):
    todosProcedimentos = []
    nomePaciente = None
    dataNasc = None

    servidor = getServidor(idPaciente, by='idPaciente')

    if servidor:
        port = '5005' + servidor.split('SRV0')[1]
        if is_port_in_use(int(port)):
            listarProcedimentos = neonat_pb2.TodosProcedimentosPaciente(idPaciente=idPaciente)
            channel = grpc.insecure_channel(ip + ':' + port)
            stub = neonat_pb2_grpc.NeoNatStub(channel)
            respostaListarProcedimentos = stub.ListarProcedimentos(listarProcedimentos)
            nomePaciente = respostaListarProcedimentos.nomeRN
            dataNasc = respostaListarProcedimentos.dataHoraNasc
            
            for procedimento in respostaListarProcedimentos.procedimentos:
                todosProcedimentos.append([procedimento.idProcedimento,
                procedimento.descricaoProcedimento,
                procedimento.idPaciente,
                procedimento.data])
        else:
            if len(hashs_servidores[servidor]['IDs Procedimentos']) > 0:
                nomePaciente = "Dados não disponíveis no momento"
                dataNasc = "Dados não disponíveis no momento"
                for i in hashs_servidores[servidor]['IDs Procedimentos']:
                    if i['idPaciente'] == idPaciente:
                        todosProcedimentos.append([i['idProcedimento'],
                        "Dados não disponíveis no momento",
                        i['idPaciente'],
                        "Dados não disponíveis no momento"])             
    else:
        try:
            procedimentos = dados['Pacientes'][idPaciente]['Dados Pessoais']['Procedimentos']
            nomePaciente = dados['Pacientes'][idPaciente]['Dados Pessoais']['NomeRN']
            dataNasc = dados['Pacientes'][idPaciente]['Dados Pessoais']['DataNascimento']
            
            for procedimento in procedimentos:
                todosProcedimentos.append([dados['Procedimentos'][procedimento]['idProcedimento'],
                dados['Procedimentos'][procedimento]['descricaoProcedimento'],
                dados['Procedimentos'][procedimento]['idPaciente'],
                dados['Procedimentos'][procedimento]['Data']])
         
        except Exception as e:
            print(f'{e}')

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

def listarTodosMedicos(nome_servidor):
    global server_name

    todosMedicos = []

    # for key, _ in dados['Medico'].items():
    #     todosMedicos.append([key, dados['Medico'][key]['nome'], 
    #     dados['Medico'][key]['dataNasc']])



    if (len(nome_servidor) == 0) or (server_name == nome_servidor):
        for i in ports_perm:
            if (i != myport) and (is_port_in_use(int(i))):
              
                listarMedicos = neonat_pb2.TodosMedicos(nome_servidor=server_name) #adicionar nome_servidor neonat.proto
                channel = grpc.insecure_channel(ip + ':' + i)
                stub = neonat_pb2_grpc.NeoNatStub(channel)
                respostaListarMedicos = stub.ListarMedicos(listarMedicos)
                
                if len(respostaListarMedicos.medicos) > 0:
                     for medico in respostaListarMedicos.medicos:
                        todosMedicos.append([medico.CRM, medico.nome, 
                        medico.dataNasc])
            else:
             
                servidor = 'SRV0' + i.split('5005')[1]
                for key, value in hashs_servidores.items():
    
                    if key == servidor:
               
                        for v in value['IDs Medicos']:
                            
                            todosMedicos.append([v, "Dado não disponível no momento", 
                            "Dado não disponível no momento"])


        for key, _ in dados['Medico'].items():
            todosMedicos.append([key, dados['Medico'][key]['nome'], 
            dados['Medico'][key]['dataNasc']])

    else:
        for key, _ in dados['Medico'].items():
            todosMedicos.append([key, dados['Medico'][key]['nome'], 
            dados['Medico'][key]['dataNasc']])

    #return todosPacientes

    return todosMedicos


def listarPacientesMedico(CRM):
    todosPacientes = []
    crm = get_medico(CRM)

    if crm == 'cadastrado+':
        servidor = getServidor(CRM, by="CRM")

        port = '5005' + servidor.split('SRV0')[1]

        if is_port_in_use(int(port)):
            listarPacientesMedico = neonat_pb2.TodosPacientesMedico(CRM=CRM)
            channel = grpc.insecure_channel(ip + ':' + port)
            stub = neonat_pb2_grpc.NeoNatStub(channel)
            respostalistarPacientesMedico = stub.PesquisarPacientesMedico(listarPacientesMedico)
            
            for paciente in respostalistarPacientesMedico.pacientes:
                todosPacientes.append([paciente.idPaciente, paciente.nomeRN,
                paciente.dataHoraNasc])
        
        else:
            todosPacientes.append(["Dados não disponíveis", "Dados não disponíveis",
                "Dados não disponíveis"])

    elif crm == 'cadastrado': 
        for key, _ in dados['Pacientes'].items():
            if dados['Pacientes'][key]['Dados Pessoais']['Medico'] == CRM:
                todosPacientes.append([key, dados['Pacientes'][key]['Dados Pessoais']['NomeRN'],
                dados['Pacientes'][key]['Dados Pessoais']['DataNascimento']])
    else:
        todosPacientes.append(["Médico não encontrado", "Médico não encontrado",
                "Médico não encontrado"])

        
    
    return todosPacientes

class NeonatServer(neonat_pb2_grpc.NeoNatServicer): 
    def InserirPacientes(self, request, context): #Nome do serviço
        resposta_inserir_paciente = neonat_pb2.RegistrarPacientesResposta() #Função resposta de registrar pacientes
        resposta_inserir_paciente.resposta = inserirPacientes(request.pacientes.idPaciente, request.pacientes.nomeRN, 
        request.pacientes.maeRN, request.pacientes.dataHoraNasc, request.pacientes.peso, request.pacientes.sexo, 
        request.pacientes.cidadeNasc, request.pacientes.idadeGestacional, 
        request.pacientes.dataDiagnostico, request.pacientes.tipoParto, request.pacientes.descricaoUTI, 
        request.pacientes.descricaoStatus, request.pacientes.medico.CRM)

        with open(log_name, 'a') as log:
            log.write(f'''InserirPacientes, {request.pacientes.idPaciente}, {request.pacientes.nomeRN}, {request.pacientes.maeRN}, \
{request.pacientes.dataHoraNasc}, {request.pacientes.peso}, {request.pacientes.sexo}, \
{request.pacientes.cidadeNasc}, {request.pacientes.idadeGestacional}, {request.pacientes.dataDiagnostico}, \
{request.pacientes.tipoParto}, {request.pacientes.descricaoUTI}, {request.pacientes.descricaoStatus}, \
{request.pacientes.medico.CRM}\n''')

        servidor = getServidor(request.pacientes.medico.CRM, 'CRM')
      
        if servidor:
           
            self.enviarDados(servidor)

        if request.pacientes.medico.CRM in [*dados['Medico'].keys()]:
            #ENVIAR HASH DO NOVO DADO PARA OUTROS SERVIDORES
            enviarDados = neonat_pb2.NovoDadoPaciente(nome_servidor = server_name,
                pacientes = neonat_pb2.Pacientes(idPaciente = request.pacientes.idPaciente), comando = 'InserirPaciente')
            
            for i in ports_perm:
                if i != myport:
                        if is_port_in_use(int(i)):
                            channel = grpc.insecure_channel(ip + ':' +  i)
                            stub = neonat_pb2_grpc.NeoNatStub(channel)
                            respostaenviarDados = stub.EnviarNovoPaciente(enviarDados)
                            print(respostaenviarDados.resposta)

        return resposta_inserir_paciente
    
    def EditarPacientes(self, request, context): #Nome do serviço
        resposta_atualizar_paciente = neonat_pb2.AtualizarPacientesResposta() #Função resposta de registrar pacientes
        resposta_atualizar_paciente.resposta = atualizarPacientes(request.pacientes.idPaciente, request.pacientes.nomeRN, request.pacientes.maeRN,
        request.pacientes.dataHoraNasc, request.pacientes.peso, request.pacientes.sexo, request.pacientes.cidadeNasc, request.pacientes.idadeGestacional, 
        request.pacientes.dataDiagnostico, request.pacientes.tipoParto, request.pacientes.descricaoUTI, request.pacientes.descricaoStatus,
        request.pacientes.medico.CRM)

        with open(log_name, 'a') as log:
            log.write(f'''EditarPacientes, {request.pacientes.idPaciente}, {request.pacientes.nomeRN}, {request.pacientes.maeRN}, \
{request.pacientes.dataHoraNasc}, {request.pacientes.peso}, {request.pacientes.sexo}, \
{request.pacientes.cidadeNasc}, {request.pacientes.idadeGestacional}, {request.pacientes.dataDiagnostico}, \
{request.pacientes.tipoParto}, {request.pacientes.descricaoUTI}, {request.pacientes.descricaoStatus}, \
{request.pacientes.medico.CRM}\n''')

        servidor = getServidor(request.pacientes.idPaciente, 'idPaciente')
        if servidor is not None:
            self.enviarDados(servidor)
        

        return resposta_atualizar_paciente

    def ExcluirPacientes(self, request, context):
        resposta_excluir_paciente = neonat_pb2.DeletarPacientesResposta()

        servidor = getServidor(request.idPaciente, 'idPaciente')
        if servidor is not None:
            self.enviarDados(servidor)

        if request.idPaciente in [*dados['Pacientes'].keys()]:
            #ENVIAR HASH DO NOVO DADO PARA OUTROS SERVIDORES
            enviarDados = neonat_pb2.NovoDadoPaciente(nome_servidor = server_name,
                pacientes = neonat_pb2.Pacientes(idPaciente = request.idPaciente), comando = 'ExcluirPaciente')
            
            for i in ports_perm:
                if i != myport:
                        if is_port_in_use(int(i)):
                            channel = grpc.insecure_channel(ip + ':' + i)
                            stub = neonat_pb2_grpc.NeoNatStub(channel)
                            respostaenviarDados = stub.EnviarNovoPaciente(enviarDados)
                            print(respostaenviarDados.resposta)

        resposta_excluir_paciente.resposta = deletarPaciente(request.idPaciente)

        with open(log_name, 'a') as log:
            log.write(f'ExcluirPacientes {request.idPaciente}\n')
        

        return resposta_excluir_paciente
    
    def PesquisarPacientes(self, request, context):
        result = pesquisarPaciente(request.idPaciente)

        return neonat_pb2.ConsultarPacientesResposta(pacientes = neonat_pb2.Pacientes(
            nomeRN = result[0], maeRN = result[1], dataHoraNasc=result[2], peso=result[3], 
            sexo=result[4], cidadeNasc=result[5], idadeGestacional=result[6], 
            dataDiagnostico=result[7], 
            tipoParto=result[8], 
            descricaoUTI=result[9], 
            descricaoStatus=result[10],
            medico=neonat_pb2.Medicos(CRM=result[11])))


    def ListarPacientes(self, request, context):
        pacientes = listarTodosPacientes(request.nome_servidor)
        

        todospacientes = neonat_pb2.TodosPacientesResposta()
        
        for paciente in pacientes:
            p = todospacientes.pacientes.add()
            p.idPaciente = paciente[0]
            p.nomeRN = paciente[1]
            p.maeRN = paciente[2]
            p.dataHoraNasc=paciente[3]
            p.peso=float(paciente[4]) 
            p.sexo=int(paciente[5])
            p.cidadeNasc=paciente[6]
            p.idadeGestacional=int(paciente[7]) 
            p.dataDiagnostico=paciente[8] 
            p.tipoParto=int(paciente[9]) 
            p.descricaoUTI=paciente[10] 
            p.descricaoStatus=paciente[11]
            p.medico.CRM=paciente[12]

        return todospacientes


    def InserirProcedimentos(self, request, context):
        resposta_inserir_Procedimentos = neonat_pb2.RegistrarProcedimentosResposta()
        resposta_inserir_Procedimentos.resposta = inserirProcedimentos(request.procedimentos.idProcedimento, request.procedimentos.descricaoProcedimento, 
        request.procedimentos.idPaciente, request.procedimentos.data)

        try:
            with open(log_name, 'a') as log:
                log.write(f'''InserirProcedimentos, {request.procedimentos.idProcedimento}, {request.procedimentos.descricaoProcedimento}, {request.procedimentos.idPaciente}, {request.procedimentos.data}\n''')
        except Exception as e:
            print(f'{e}')

        servidor = getServidor(request.procedimentos.idPaciente, 'idPaciente')
        if servidor is not None:
            self.enviarDados(servidor)

        
        if request.procedimentos.idPaciente in [*dados['Pacientes'].keys()]: 
            #ENVIAR HASH DO NOVO DADO PARA OUTROS SERVIDORES
            enviarDados = neonat_pb2.NovoDadoProcedimento(nome_servidor = server_name,
                procedimentos = neonat_pb2.Procedimentos(idProcedimento = request.procedimentos.idProcedimento,
                idPaciente=request.procedimentos.idPaciente), 
                comando = 'InserirProcedimento')
            
            for i in ports_perm:
                if i != myport:
                        if is_port_in_use(int(i)):
                            channel = grpc.insecure_channel(ip + ':' + i)
                            stub = neonat_pb2_grpc.NeoNatStub(channel)
                            respostaenviarDados = stub.EnviarNovoProcedimento(enviarDados)
                            print(respostaenviarDados.resposta)
                            
        return resposta_inserir_Procedimentos
    
    def EditarProcedimentos(self, request, context):
        resposta_atualizar_Procedimentos = neonat_pb2.AtualizarProcedimentosResposta()
        resposta_atualizar_Procedimentos.resposta = atualizarProcedimentos(request.procedimentos.idProcedimento,
        request.procedimentos.idPaciente, request.procedimentos.descricaoProcedimento, 
        request.procedimentos.data)

        try:
            with open(log_name, 'a') as log:
                log.write(f'''EditarProcedimentos, {request.procedimentos.idProcedimento}, {request.procedimentos.descricaoProcedimento}, {request.procedimentos.idPaciente}, {request.procedimentos.data}\n''')
        except Exception as e:
            print(f'{e}')

        servidor = getServidor(request.procedimentos.idPaciente, 'idPaciente')
        if servidor is not None:
            self.enviarDados(servidor)


        return resposta_atualizar_Procedimentos

    def ExcluirProcedimentos(self, request, context):
        resposta_excluir_Procedimentos = neonat_pb2.DeletarProcedimentosResposta()
        resposta_excluir_Procedimentos.resposta = excluirProcedimentos(request.idProcedimento, request.idPaciente)
        
        with open(log_name, 'a') as log:
           log.write(f'ExcluirProcedimentos, {request.idProcedimento}, {request.idPaciente}\n')

        servidor = getServidor(request.idPaciente, 'idPaciente')
        if servidor is not None:
            self.enviarDados(servidor)


        if request.idPaciente in [*dados['Pacientes'].keys()]: 
            #ENVIAR HASH DO NOVO DADO PARA OUTROS SERVIDORES
            enviarDados = neonat_pb2.NovoDadoProcedimento(nome_servidor = server_name,
                procedimentos = neonat_pb2.Procedimentos(idProcedimento = request.idProcedimento,
                idPaciente=request.idPaciente), 
                comando = 'ExcluirProcedimento')
            
            for i in ports_perm:
                if i != myport:
                        if is_port_in_use(int(i)):
                            channel = grpc.insecure_channel(ip + ':' + i)
                            stub = neonat_pb2_grpc.NeoNatStub(channel)
                            respostaenviarDados = stub.EnviarNovoProcedimento(enviarDados)
                            print(respostaenviarDados.resposta)

        return resposta_excluir_Procedimentos

    def PesquisarProcedimentos(self, request, context):

        result = pesquisarProcedimentos(request.idPaciente, request.idProcedimento)
        return neonat_pb2.ConsultarProcedimentosResposta(procedimentos = neonat_pb2.Procedimentos(
            descricaoProcedimento=result[0],
            data=result[1]
        ))
    
    def ListarProcedimentos(self, request, context):
        
        resposta_todos_procedimentos = neonat_pb2.TodosProcedimentosPacienteResposta()
        procedimentos, nomeRN, dataNasc = listarProcedimentos(request.idPaciente)

        if nomeRN is None:
             resposta_todos_procedimentos.nomeRN = ''
        else:
            resposta_todos_procedimentos.nomeRN = nomeRN

        if dataNasc is None:
             resposta_todos_procedimentos.dataHoraNasc = ''
        else:
            resposta_todos_procedimentos.dataHoraNasc = dataNasc
       
        for procedimento in procedimentos:
            p = resposta_todos_procedimentos.procedimentos.add()
            p.idProcedimento = procedimento[0]
            p.descricaoProcedimento = procedimento[1]
            p.idPaciente = procedimento[2]
            p.data = procedimento[3]

        return resposta_todos_procedimentos
            

    def InserirMedico(self, request, context):
        resposta_inserir_Medico = neonat_pb2.RegistrarMedicoResposta()
        resposta_inserir_Medico.resposta = inserirMedico(request.medico.CRM, request.medico.nome,
        request.medico.dataNasc)

        with open(log_name, 'a') as log:
           log.write(f'InserirMedico, {request.medico.CRM}, {request.medico.nome}, {request.medico.dataNasc}\n')

        #ENVIAR HASH DO NOVO DADO PARA OUTROS SERVIDORES
        enviarDados = neonat_pb2.NovoDadoMedico(nome_servidor = server_name,
            medicos = neonat_pb2.Medicos(CRM = request.medico.CRM), comando = 'InserirMedico')
        
        for i in ports_perm:
            if i != myport:
                    if is_port_in_use(int(i)):
                        channel = grpc.insecure_channel(ip + ':' + i)
                        stub = neonat_pb2_grpc.NeoNatStub(channel)
                        respostaenviarDados = stub.EnviarNovoMedico(enviarDados)
                        print(respostaenviarDados.resposta)

        return resposta_inserir_Medico
    

    def ListarMedicos(self, request, context):
        medicos = listarTodosMedicos(request.nome_servidor)
        

        todosMedicos = neonat_pb2.TodosMedicosResposta()
        
        for medico in medicos:
            m = todosMedicos.medicos.add()
            m.CRM = medico[0]
            m.nome = medico[1]
            m.dataNasc = medico[2]

        return todosMedicos

    def PesquisarPacientesMedico(self, request, context):
        pacientes = listarPacientesMedico(request.CRM)

        todosPacientesMedico = neonat_pb2.TodosPacientesMedicoResposta()
        for paciente in pacientes:
            p = todosPacientesMedico.pacientes.add()
            p.idPaciente = paciente[0]
            p.nomeRN = paciente[1]
            p.dataHoraNasc = paciente[2]


        return todosPacientesMedico

    def EnviarInformacoes(self, request, context):
        global server_name

        procedimentos = []
        pacientes = []
        medicos = []

        if 'Dados a enviar' in [*dados.keys()]:
            if request.nome_servidor in [*dados['Dados a enviar'].keys()]:
                threading.Thread(target=self.enviarDados, args=(request.nome_servidor,)).start()

        for paciente, procedimento in zip(request.idPacientes, request.idProcedimentos):
            procedimentos.append({'idProcedimento': procedimento, "idPaciente": paciente})

        for paciente in request.pacientes:
            pacientes.append(paciente)

        for medico in request.medicos:
            medicos.append(medico)

        hashs_servidores[request.nome_servidor] = {
                    'IDs Pacientes': list(set(pacientes)),
                    'IDs Procedimentos': list(map(dict, set(tuple(d.items()) for d in procedimentos))),
                    'IDs Medicos': list(set(medicos))
                }
        

        pacientes, procedimentos, medicos = getHashs()
        respostaEnviarInformacoes = neonat_pb2.NovoServidorReposta()
        respostaEnviarInformacoes.nome_servidor = server_name

        
        for i in pacientes:
            p = respostaEnviarInformacoes.pacientes.add()
            p.idPaciente = i

        for pac, proc in procedimentos:
            pr = respostaEnviarInformacoes.procedimentos.add()
            pr.idProcedimento = proc
            pr.idPaciente = pac
        
        for i in medicos:
            m = respostaEnviarInformacoes.medicos.add()
            m.CRM = i

        return respostaEnviarInformacoes
    
    def EnviarNovoPaciente(self, request, context):
        resposta = neonat_pb2.NovoDadoPacienteResposta()
        if request.comando == 'InserirPaciente':
            hashs_servidores[request.nome_servidor]['IDs Pacientes'].append(request.pacientes.idPaciente)
            hashs_servidores[request.nome_servidor]\
                ['IDs Pacientes'] = list(set(hashs_servidores[request.nome_servidor]\
                    ['IDs Pacientes']))
            
            resposta.resposta = 'Hash novo paciente recebido'
            return resposta
        elif request.comando == 'ExcluirPaciente':
            hashs_servidores[request.nome_servidor]['IDs Pacientes'].remove(request.pacientes.idPaciente)
            resposta.resposta = 'Hash paciente excluido'
            return resposta
        

    
    def EnviarNovoMedico(self, request, context):
        resposta = neonat_pb2.NovoDadoMedicoResposta()
        if request.comando == 'InserirMedico':
            hashs_servidores[request.nome_servidor]['IDs Medicos'].append(request.medicos.CRM)
            
            hashs_servidores[request.nome_servidor]\
                ['IDs Medicos'] = list(set(hashs_servidores[request.nome_servidor]\
                    ['IDs Medicos']))
            
            resposta.resposta = 'Hash novo medico recebido'
            return resposta

        elif request.comando == 'ExcluirMedico':
            hashs_servidores[request.nome_servidor]['IDs Medicos'].remove(request.medicos.CRM)
            resposta.resposta = 'Hash medico excluido'
            return resposta

    def EnviarNovoProcedimento(self, request, context):
        resposta = neonat_pb2.NovoDadoProcedimentoResposta()
        if request.comando == 'InserirProcedimento':
            hashs_servidores[request.nome_servidor]\
                ['IDs Procedimentos'].append(
                    {'idProcedimento':request.procedimentos.idProcedimento,
                    'idPaciente': request.procedimentos.idPaciente})

            hashs_servidores[request.nome_servidor]\
                ['IDs Procedimentos'] = list(map(dict, set(tuple(d.items()) 
                for d in hashs_servidores[request.nome_servidor]\
                ['IDs Procedimentos'])))
            
            resposta.resposta = 'Hash novo procedimento recebido'
            return resposta
        elif request.comando == 'ExcluirProcedimento':
            hashs_servidores[request.nome_servidor]\
            ['IDs Procedimentos']  = [{'idProcedimento': i['idProcedimento'], 'idPaciente': i['idPaciente']}
                    for i in hashs_servidores[request.nome_servidor]\
                    ['IDs Procedimentos'] if (i['idProcedimento'] != request.procedimentos.idProcedimento)
                    and (i['idPaciente'] == request.procedimentos.idPaciente)]
        
            resposta.resposta = 'Hash procedimento excluído'
            return resposta


    def enviarDados(self, nome_servidor):
        port = '5005' + nome_servidor.split('SRV0')[1]
     
        keys_excluir = []
        if is_port_in_use(int(port)):
         
            for key, value in dados['Dados a enviar'][nome_servidor]['Procedimentos'].items():
                if value['comando'] == 'InserirProcedimento':
                    idProcedimento = value['idProcedimento']
                    idPaciente = value['idPaciente']
                    descricaoProcedimento = value['descricaoProcedimento']
                    data = value['Data']
                    inserirProcedimentos = neonat_pb2.RegistrarProcedimentos(procedimentos = neonat_pb2.Procedimentos(idProcedimento=idProcedimento, 
                    descricaoProcedimento=descricaoProcedimento, idPaciente=idPaciente, data=data)) 

                    if is_port_in_use(int(port)):
                        channel = grpc.insecure_channel(ip + ':' + port)
                        stub = neonat_pb2_grpc.NeoNatStub(channel)
                      
                        respostaInserirProcedimentos = stub.InserirProcedimentos(inserirProcedimentos)
                   
                        print(respostaInserirProcedimentos.resposta)
                        keys_excluir.append(key)
                    

                elif value['comando'] == 'AtualizarProcedimento':
                    idProcedimento = value['idProcedimento']
                    idPaciente = value['idPaciente']
                    descricaoProcedimento = value['descricaoProcedimento']
                    data = value['Data']

                    atualizarProcedimentos = neonat_pb2.AtualizarProcedimentos(procedimentos = neonat_pb2.Procedimentos(
                    idProcedimento = idProcedimento, descricaoProcedimento=descricaoProcedimento, 
                    idPaciente=idPaciente, data=data))

                    if is_port_in_use(int(port)):
                        channel = grpc.insecure_channel(ip + ':' + port)
                        stub = neonat_pb2_grpc.NeoNatStub(channel)
                        #CRIAR SERVIÇO EnviarNovoProcedimento
                        respostaAtualizarProcedimentos = stub.EditarProcedimentos(atualizarProcedimentos)
                        print(respostaAtualizarProcedimentos.resposta)
                        keys_excluir.append(key)

                elif value['comando'] == 'ExcluirProcedimento':
                    idProcedimento = value['idProcedimento']
                    idPaciente = value['idPaciente']

                    deletarProcedimentos = neonat_pb2.DeletarProcedimentos(idProcedimento=idProcedimento, 
                    idPaciente=idPaciente)

                    if is_port_in_use(int(port)):
                        channel = grpc.insecure_channel(ip + ':' + port)
                        stub = neonat_pb2_grpc.NeoNatStub(channel)
                        respostaDeletarProcedimentos = stub.ExcluirProcedimentos(deletarProcedimentos)
                        print(respostaDeletarProcedimentos.resposta)
                        keys_excluir.append(key)

                    
            for key in keys_excluir:
                del dados['Dados a enviar'][nome_servidor]['Procedimentos'][key]
            del keys_excluir[:]

            for key, value in dados['Dados a enviar'][nome_servidor]['Pacientes'].items():
                if value['comando'] == 'InserirPaciente':
                    idPaciente = key
                    nomeRN = value['NomeRN']
                    maeRN = value['NomeMae']
                    dataHoraNasc = value['DataNascimento']
                    peso = value['Peso']
                    sexo = value['Sexo']
                    cidadeNasc = value['CidadeNascimento']
                    idadeGestacional = value['IdadeGestacional']
                    dataDiagnostico = value['DataDiagnostico']
                    tipoParto = value['TipoParto']
                    descricaoUTI = value['descricaoUTI']
                    descricaoStatus = value['descricaoStatus']
                    CRM = value['Medico']

                    inserirPaciente = neonat_pb2.RegistrarPacientes(pacientes = neonat_pb2.Pacientes(idPaciente=idPaciente, 
                    nomeRN=nomeRN, maeRN=maeRN,
                    dataHoraNasc=dataHoraNasc, peso=float(peso), sexo=sexo, 
                    cidadeNasc = cidadeNasc, idadeGestacional=int(idadeGestacional), dataDiagnostico=dataDiagnostico,
                    tipoParto=tipoParto, descricaoUTI=descricaoUTI, descricaoStatus=descricaoStatus,
                    medico=neonat_pb2.Medicos(CRM=CRM)))

                    if is_port_in_use(int(port)):
                        channel = grpc.insecure_channel(ip + ':' + port)
                        stub = neonat_pb2_grpc.NeoNatStub(channel)
                        respostaInserirPaciente = stub.InserirPacientes(inserirPaciente)
                        print(respostaInserirPaciente.resposta)
                        keys_excluir.append(key)
                
                elif value['comando'] == 'AtualizarPaciente':
                    idPaciente = key
                    nomeRN = value['NomeRN']
                    maeRN = value['NomeMae']
                    dataHoraNasc = value['DataNascimento']
                    peso = value['Peso']
                    sexo = value['Sexo']
                    cidadeNasc = value['CidadeNascimento']
                    idadeGestacional = value['IdadeGestacional']
                    dataDiagnostico = value['DataDiagnostico']
                    tipoParto = value['TipoParto']
                    descricaoUTI = value['descricaoUTI']
                    descricaoStatus = value['descricaoStatus']
                    CRM = value['Medico']

                    atualizarPaciente = neonat_pb2.AtualizarPacientes(pacientes = neonat_pb2.Pacientes(idPaciente=idPaciente, nomeRN=nomeRN, maeRN=maeRN,
                    dataHoraNasc=dataHoraNasc, peso=float(peso), sexo=sexo, 
                    cidadeNasc = cidadeNasc, idadeGestacional=int(idadeGestacional), dataDiagnostico=dataDiagnostico,
                    tipoParto=tipoParto, descricaoUTI=descricaoUTI, 
                    descricaoStatus=descricaoStatus, medico=neonat_pb2.Medicos(CRM=CRM)))

                    if is_port_in_use(int(port)):
                        channel = grpc.insecure_channel(ip + ':' + port)
                        stub = neonat_pb2_grpc.NeoNatStub(channel)
                        respostaAtualizarPaciente = stub.EditarPacientes(atualizarPaciente)
                        print(respostaAtualizarPaciente.resposta)
                        keys_excluir.append(key)

                elif value['comando'] == 'ExcluirPaciente':
                    idPaciente = key

                    deletarPaciente = neonat_pb2.DeletarPacientes(idPaciente=idPaciente)

                    if is_port_in_use(int(port)):
                        channel = grpc.insecure_channel(ip + ':' + port)
                        stub = neonat_pb2_grpc.NeoNatStub(channel)
                        respostaDeletarPaciente = stub.ExcluirPacientes(deletarPaciente)
                        print(respostaDeletarPaciente.resposta)
                        keys_excluir.append(key)


            for key in keys_excluir:
                del dados['Dados a enviar'][nome_servidor]['Pacientes'][key]
            del keys_excluir[:]

    def NovaConexao(self):
        aux_hashs = []
        global myport, stub, succesor_port, m, channel, ports_perm, dados, server_name, hashs

        pacientes, procedimentos, medicos = getHashs()

        enviarDados = neonat_pb2.NovoServidor(nome_servidor = server_name, pacientes=pacientes, 
        idProcedimentos = [procedimento[1] for procedimento in procedimentos],
        idPacientes = [pacinte[0] for pacinte in procedimentos],
        medicos=medicos)
        
        count = 0
        for i in ports_perm:
            if i != myport:
                    if is_port_in_use(int(i)):
                        if 'Dados a enviar' in [*dados.keys()]:
                            servidor = 'SRV0' + i.split('5005')[1]
                            if servidor in [*dados['Dados a enviar'].keys()]:
                                threading.Thread(target=self.enviarDados, args=(servidor,)).start()

                        succesor_port = i
                        channel = grpc.insecure_channel('localhost:' + succesor_port)
                        stub = neonat_pb2_grpc.NeoNatStub(channel)
                        respostaenviarDados = stub.EnviarInformacoes(enviarDados)
                        aux_hashs.append(respostaenviarDados)
                    else:
                        count += 1
        if count == (m - 1):
            print('Sou o primeiro')
        else:
            for hash_ in aux_hashs:
                pacientes = []
                procedimentos = []
                medicos = []

                for paciente in hash_.pacientes:
                    pacientes.append(paciente.idPaciente)

                for procedimento in hash_.procedimentos:
                    procedimentos.append({'idProcedimento': procedimento.idProcedimento, "idPaciente": procedimento.idPaciente})
                # for procedimento in hash_.procedimentos:
                #     procedimentos.append({procedimento})

                for medico in hash_.medicos:
                    medicos.append(medico.CRM)

                hashs_servidores[hash_.nome_servidor] = {
                    'IDs Pacientes': list(set(pacientes)),
                    'IDs Procedimentos': list(map(dict, set(tuple(d.items()) for d in procedimentos))),
                    'IDs Medicos': list(set(medicos))
                }

    def UltimoSnapshotLog(self):
        global server_name

        if not os.path.isdir(os.getcwd() + '/' + server_name):
            os.mkdir(os.getcwd() + '/' + server_name)
            

        logs_lista = []
        snapshot_lista = []
        path_to_folder = os.getcwd()
        logs = glob.glob(path_to_folder+f"/{server_name}/*log*")
        snapshots = glob.glob(path_to_folder+f"/{server_name}/*snapshot*")

        if (len(snapshots) == 0) and (len(logs) == 0):
            return 0, 0

        for log in logs:
            l = log.split('.txt')[0]
            l = l.split('log_')[1]
            logs_lista.append(int(l))

        for snapshot in snapshots:
            s = snapshot.split('.txt')[0]
            s = s.split('snapshot_')[1]
            snapshot_lista.append(int(s))

        return max(logs_lista), max(snapshot_lista)


    def CriarSnapshot(self):
        global snapshot_name, log_name 
        while True:
            tempo_atual = time.time()
            log_number, snapshot_number = self.UltimoSnapshotLog()
            while True:
                if time.time() - tempo_atual > 10:
                    with open(f'{server_name}/snapshot_{snapshot_number + 1}.txt', 'w') as f:
                        json.dump(dados, f)

                    snapshot_name = f'{server_name}/snapshot_{snapshot_number + 1}.txt'
                    log_name = f'{server_name}/log_{log_number + 1}.txt'

                   
                    open(log_name, 'a').close()

                    with open(f'{server_name}/hashs.json', 'w+') as f:
                        json.dump(hashs_servidores, f)
            
                    try:
                        os.unlink(f'{os.getcwd()}/{server_name}/log_{log_number - 1}.txt')
                        os.unlink(f'{os.getcwd()}/{server_name}/snapshot_{snapshot_number - 1}.txt')
                    except:
                        pass

                    break

    def RecuperarEstadoServidor(self):
        global dados, countProcedimentos, hashs_servidores, log_name, snapshot_name

        log_number, snapshot_number = self.UltimoSnapshotLog()

        log_name = f'{server_name}/log_{log_number}.txt'
        snapshot_name = f'{server_name}/snapshot_{snapshot_number}.txt'

        if os.path.isfile(f'{server_name}/hashs.json'):
            with open(f'{server_name}/hashs.json', 'r') as f:
                hashs_servidores = json.load(f)


        if os.path.isfile(snapshot_name):
            with open(snapshot_name) as f:
                dados = json.load(f)

            with open(log_name,'r') as f:
                logs_comando = f.readlines()
            
            if len(logs_comando) > 0:
                for line in logs_comando:
                    line = line.strip()

                    line = line.split(', ')

                    #PACIENTES
                    if line[0] ==  'InserirPacientes':
                        inserirPacientes(*line[1::])
                    elif line[0] ==  'EditarPacientes':
                        atualizarPacientes(*line[1::])
                    elif line[0] == 'ExcluirPacientes':
                        deletarPaciente(*line[1::])
                    
                    #PROCEDIMENTOS
                    elif line[0] ==  'InserirProcedimentos':
                        inserirProcedimentos(*line[1::])
                    elif line[0] ==  'EditarProcedimentos':
                        atualizarProcedimentos(*line[1::])
                    elif line[0] == 'ExcluirProcedimentos':
                        excluirProcedimentos(*line[1::])

                    #MEDICOS
                    elif line[0] ==  'InserirMedico':
                        inserirMedico(*line[1::])
                

            keysProcedimentos = [*dados['Procedimentos'].keys()]
            #countProcedimentos = max([int(x.split(server_name + 'P')[1]) for x in keysProcedimentos]) + 1
           

            try:
                countProcedimentos = max([int(x.split(server_name + 'P')[1]) for x in keysProcedimentos]) + 1
            except:
                pass  
        
        threading.Thread(target=self.CriarSnapshot).start()
        
        #QUANDO UM NOVO SERVIDOR SE CONECTA
        NeonatServer().NovaConexao()


def is_port_in_use(port):
    global ip
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((ip, port)) == 0

def run_server():
    #gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),
    options=(('grpc.so_reuseport', 1),))

    neonat_pb2_grpc.add_NeoNatServicer_to_server(
            NeonatServer(), server)
    

    global ports, myport, ports_perm, server_name, countProcedimentos 
    global log_name, snapshot_name, dados


    count = 0
    
    #Encontrar um endereço livre para se conectar
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

        #THREAD PARA RECUPERAR O ESTADO DO SERVIDOR. ESSA THREAD CHAMA OUTRA THREAD PARA CRIAR OS SNAPSHOTS
        threading.Thread(target=NeonatServer().RecuperarEstadoServidor).start()
        
    
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