import grpc
import numpy as np
# import the generated classes
import neonat_pb2 
import neonat_pb2_grpc

#Número de servidores
m = 3

#VARIÁVEIS GLOBAIS
ports = [str(50051 + i) for i in range(m)]
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

        # channel2 = grpc.insecure_channel('10.246.88.139:50052')
        # create a stub (client)
        stub = neonat_pb2_grpc.NeoNatStub(channel)
        break
print(i)

class Client():
    def menu(self):
        print('================= MENU =================\n')
        print('======= PACIENTES =======')
        print('1: Registrar Paciente.')
        print('2: Atualizar Paciente.')
        print('3: Excluir Paciente.')
        print('4: Consultar um Paciente.')
        print('5: Listar todos os Pacientes.\n')
        print('======= PROCEDIMENTOS =======')
        print('6: Registrar Procedimentos.')
        print('7: Atualizar Procedimentos.')
        print('8: Excluir Procedimentos.')
        print('9: Consultar Procedimento de um Paciente.')
        print('10: Listar todos os Procedimentos de um Paciente.\n')
        print('======= MÉDICOS =======')
        print('11: Registrar Médico.')
        print('12: Listar todos os médicos.')
        print('13: Listar todos os pacientes de um médico.')
        print('========== OUTROS ==========')
        print('0: Sair')
        print('menu: Mostrar o menu novamente')

    def RegistrarPaciente(self, usuario):
        try:
            print("================= CADASTRAR PACIENTE =================\n")
            idPaciente = input('ID Paciente: ')
            nomeRN = input('Nome Paciente: ')
            maeRN = input('Nome da mãe: ')
            dataHoraNasc = input('Data de nascimento (DD-MM-YYYY): ')
            peso = input('Peso do paciente: ')
            sexo = input('Sexo do paciente (Feminino/Masculino): ')
            cidadeNasc = input('Cidade natal do paciente: ')
            idadeGestacional = input('Idade Gestacional: ')
            dataDiagnostico = input('Data do diagnóstico (DD-MM-YYYY): ')
            tipoParto = input('Tipo de parto (Cesaria/Normal): ')
            descricaoUTI = input('Descrição UTI: ')
            descricaoStatus = input('Descrição Status: ')
            print('------------ INFORMAÇÕES DO MÉDICO ------------')
            CRM = input('CRM (xxxxx-UF): ')

            if((len(dataHoraNasc.split('-')) != 3) or (len(dataDiagnostico.split('-')) != 3)):
                print('Datas inseridas no formato incorreto.')
                self.RegistrarPaciente(usuario)

            inserirPaciente = neonat_pb2.RegistrarPacientes(pacientes = neonat_pb2.Pacientes(idPaciente=idPaciente, 
            nomeRN=nomeRN, maeRN=maeRN,
            dataHoraNasc=dataHoraNasc, peso=float(peso), sexo=neonat_pb2.Pacientes.Sexo.Value(sexo.upper()), 
            cidadeNasc = cidadeNasc, idadeGestacional=int(idadeGestacional), dataDiagnostico=dataDiagnostico,
            tipoParto=neonat_pb2.Pacientes.Parto.Value(tipoParto.upper()), descricaoUTI=descricaoUTI, descricaoStatus=descricaoStatus,
            medico=neonat_pb2.Medicos(CRM=CRM)), 
            usuario = neonat_pb2.Usuario(usuario=usuario))

            respostaInserirPaciente = stub.InserirPacientes(inserirPaciente)
            print(respostaInserirPaciente.resposta)
            print("===================================================\n")

        except Exception as e:
            print(f'Erro: {e}')
    
    def AtualizarPaciente(self, usuario):
        try:
            idPaciente = self.ConsultarPaciente(usuario)

            print("================= INSIRA OS NOVOS DADOS =================\n")
            nomeRN = input('Nome Paciente: ')
            maeRN = input('Nome da mãe: ')
            dataHoraNasc = input('Data de nascimento (DD-MM-YYYY): ')
            peso = input('Peso do paciente: ')
            sexo = input('Sexo do paciente (Feminino/Masculino): ')
            cidadeNasc = input('Cidade natal do paciente: ')
            idadeGestacional = input('Idade Gestacional: ')
            dataDiagnostico = input('Data do diagnóstico (DD-MM-YYYY): ')
            tipoParto = input('Tipo de parto (Cesaria/Normal): ')
            descricaoUTI = input('Descricao UTI: ')
            descricaoStatus = input('Descricao Status: ')
            print('------------ INFORMAÇÕES DO MÉDICO ------------')
            CRM = input('CRM: ')

            if((len(dataHoraNasc.split('-')) != 3) or (len(dataDiagnostico.split('-')) != 3) or 
            (len(dataHoraNasc) != 10) or (len(dataHoraNasc) != 10)):
                print('Datas inseridas no formato incorreto.')
                self.AtualizarPaciente(usuario)

            atualizarPaciente = neonat_pb2.AtualizarPacientes(pacientes = neonat_pb2.Pacientes(idPaciente=idPaciente, nomeRN=nomeRN, maeRN=maeRN,
                dataHoraNasc=dataHoraNasc, peso=float(peso), sexo=neonat_pb2.Pacientes.Sexo.Value(sexo.upper()), 
                cidadeNasc = cidadeNasc, idadeGestacional=int(idadeGestacional), dataDiagnostico=dataDiagnostico,
                tipoParto=neonat_pb2.Pacientes.Parto.Value(tipoParto.upper()), descricaoUTI=descricaoUTI, 
                descricaoStatus=descricaoStatus, medico=neonat_pb2.Medicos(CRM=CRM)), 
                usuario = neonat_pb2.Usuario(usuario=usuario))

            respostaAtualizarPaciente = stub.EditarPacientes(atualizarPaciente)
            print(respostaAtualizarPaciente.resposta)
            print("===================================================\n")

        except Exception as e:
            print(f'Erro: {e}')
        
    def DeletarPaciente(self, usuario):
        print("================= DELETAR UM PACIENTE =================")
        idPaciente = input('Informe o ID do paciente que deseja excluir: ')
        deletarPaciente = neonat_pb2.DeletarPacientes(idPaciente=idPaciente, usuario = neonat_pb2.Usuario(usuario=usuario))
        respostaDeletarPaciente = stub.ExcluirPacientes(deletarPaciente)
        print(respostaDeletarPaciente.resposta)
        print("===================================================\n")


    def ConsultarPaciente(self, usuario):
        print("================= CONSULTAR PACIENTE =================\n")
        idPaciente = input('Insira o ID do Paciente: ')
        if idPaciente == '':
            self.ConsultarPaciente(usuario)

        consultarPaciente = neonat_pb2.ConsultarPacientes(idPaciente=idPaciente, usuario = neonat_pb2.Usuario(usuario=usuario))

        respostaconsultarPaciente = stub.PesquisarPacientes(consultarPaciente)
        if respostaconsultarPaciente.pacientes.nomeRN == '':
            print('Paciente não encontrado.')
        else:
            if respostaconsultarPaciente.pacientes.sexo == 0:
                sexo = 'Sexo desconhecido'
            elif respostaconsultarPaciente.pacientes.sexo == 1:
                sexo = 'Feminino'
            elif respostaconsultarPaciente.pacientes.sexo == 2:
                sexo = 'Masculino'
            else:
                sexo = ''
            
            if respostaconsultarPaciente.pacientes.tipoParto == 0:
                parto = 'Parto desconhecido'
            elif respostaconsultarPaciente.pacientes.tipoParto == 1:
                parto = 'Cesária'
            elif respostaconsultarPaciente.pacientes.tipoParto == 2:
                parto = 'Normal'

            print(f'Nome do paciente: {respostaconsultarPaciente.pacientes.nomeRN}')
            print(f'Nome da mãe: {respostaconsultarPaciente.pacientes.maeRN}')
            print(f'Data de Nascimento: {respostaconsultarPaciente.pacientes.dataHoraNasc}')
            print(f'Peso: {respostaconsultarPaciente.pacientes.peso}')
            print(f'Sexo: {sexo}')
            print(f'Idade Gestacional: {respostaconsultarPaciente.pacientes.idadeGestacional}')
            print(f'Data Diagnostico: {respostaconsultarPaciente.pacientes.dataDiagnostico}')
            print(f'Tipo do parto: {parto}')
            print(f'Descricao UTI: {respostaconsultarPaciente.pacientes.descricaoUTI}')
            print(f'Descricao Status: {respostaconsultarPaciente.pacientes.descricaoStatus}')
            print('------------ INFORMAÇÕES DO MÉDICO ------------')
            print(f'CRM: {respostaconsultarPaciente.pacientes.medico.CRM}')
        print("===================================================\n")
        return idPaciente
    
    def ListarPacientes(self, usuario):
        listarPacientes = neonat_pb2.TodosPacientes(usuario = neonat_pb2.Usuario(usuario=usuario))
        respostaListarPacientes = stub.ListarPacientes(listarPacientes)
       
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

    def RegistrarProcedimentos(self, usuario):
        try:
            print("================= CADASTRAR PROCEDIMENTO UTILIZADO =================\n")
            idProcedimento = input('ID Procedimento: ')
            descricaoProcedimento = input('Descrição do Procedimento: ')
            idPaciente = input('ID Paciente: ')
            data = input('Data (DD-MM-YYY): ')
            
            if(len(data.split('-')) != 3):
                print('Data inserida no formato incorreto.')
                self.RegistrarProcedimentos(usuario)

            inserirProcedimentos = neonat_pb2.RegistrarProcedimentos(procedimentos = neonat_pb2.Procedimentos(idProcedimento=idProcedimento, 
            descricaoProcedimento=descricaoProcedimento, idPaciente=idPaciente, data=data), 
            usuario = neonat_pb2.Usuario(usuario=usuario))

            respostaInserirProcedimentos = stub.InserirProcedimentos(inserirProcedimentos)
            print(respostaInserirProcedimentos.resposta)
            print("===================================================\n")

        except Exception as e:
            print(f'Erro: {e}')
    
    def AtualizarProcedimentos(self, usuario):
        try:
            idPaciente, idProcedimento = self.ConsultarProcedimentos(usuario)

            print("================= INSIRA OS NOVOS DADOS =================\n")
            descricaoProcedimento = input('descricao do Procedimento : ')
            data = input('Data (DD-MM-YYY): ')

            if(len(data.split('-')) != 3):
                print('Data inserida no formato incorreto.')
                self.AtualizarProcedimentos(usuario)
            

            atualizarProcedimentos = neonat_pb2.AtualizarProcedimentos(procedimentos = neonat_pb2.Procedimentos(
            idProcedimento = idProcedimento, descricaoProcedimento=descricaoProcedimento, 
            idPaciente=idPaciente, data=data),
            usuario = neonat_pb2.Usuario(usuario=usuario))

            respostaAtualizarProcedimentos = stub.EditarProcedimentos(atualizarProcedimentos)
            print(respostaAtualizarProcedimentos.resposta)
            print("===================================================\n")

        except Exception as e:
            print(f'Erro: {e}')
        
    def DeletarProcedimentos(self, usuario):
        print("================= DELETAR UM PROCEDIMENTO  =================")
        idProcedimento = input('Informe o ID do Procedimento que deseja excluir: ')
        idPaciente = input('Informe o ID do Paciente: ')
        deletarProcedimentos = neonat_pb2.DeletarProcedimentos(idProcedimento=idProcedimento, idPaciente=idPaciente,
        usuario = neonat_pb2.Usuario(usuario=usuario))
        respostaDeletarProcedimentos = stub.ExcluirProcedimentos(deletarProcedimentos)
        print(respostaDeletarProcedimentos.resposta)
        print("===================================================\n")


    def ConsultarProcedimentos(self, usuario):
        print("================= CONSULTAR PROCEDIMENTOS DE UM PACIENTE =================\n")
        idPaciente = input('Insira o ID do Paciente: ')
        idProcedimento = input('Insira o ID do Procedimento: ')
        if idPaciente == '' or idProcedimento == '':
            self.ConsultarProcedimentos(usuario)

        consultarProcedimentos = neonat_pb2.ConsultarProcedimentos(idPaciente=idPaciente, idProcedimento=idProcedimento,
        usuario = neonat_pb2.Usuario(usuario=usuario))

        respostaConsultarProcedimentos = stub.PesquisarProcedimentos(consultarProcedimentos)
        if respostaConsultarProcedimentos.procedimentos.descricaoProcedimento:
            print(f'Nome Procedimento: {respostaConsultarProcedimentos.procedimentos.descricaoProcedimento}')
            print(f'Data: {respostaConsultarProcedimentos.procedimentos.data}')
        else:
            print('Procedimento não cadastrado.')
        print("===================================================\n")
        return idPaciente, idProcedimento

    def ListarProcedimentos(self, usuario):
        print('============== LISTAR PROCEDIMENTOS DE UM PACIENTE =============\n')
        idPaciente = input('Informe o ID do Paciente: ')
        listarProcedimentos = neonat_pb2.TodosProcedimentosPaciente(idPaciente=idPaciente, 
        usuario = neonat_pb2.Usuario(usuario=usuario))
        respostaListarProcedimentos = stub.ListarProcedimentos(listarProcedimentos)
        if len(respostaListarProcedimentos.nomeRN) > 0:
            print('---------------------------------------------------')
            print(f'ID Paciente: {idPaciente} Nome: {respostaListarProcedimentos.nomeRN} Data de Nascimento: {respostaListarProcedimentos.dataHoraNasc}')
            print('---------------------------------------------------')
            for procedimentos in respostaListarProcedimentos.procedimentos:
                print('---------------------------------------------------')
                print(f"ID Procedimentos: {procedimentos.idProcedimento}")
                print(f'Descrição do Procedimentos: {procedimentos.descricaoProcedimento}')
                print(f'Data: {procedimentos.data}')
            print('---------------------------------------------------')
        else:
            print('Paciente não encontrado.')

    def RegistrarMedico(self, usuario):
        print('============== CADASTRAR MÉDICO =============\n')
        CRM = input('CRM (xxxxx-UF): ')
        nome = input('Nome do médico: ')
        dataNasc = input('Data de nascimento (DD-MM-YYYY): ')

        registrarMedico = neonat_pb2.RegistrarMedico(medico=neonat_pb2.Medicos(CRM=CRM,
        nome=nome, dataNasc=dataNasc), usuario= neonat_pb2.Usuario(usuario=usuario))

        respostaregistrarMedico = stub.InserirMedico(registrarMedico)
        print(respostaregistrarMedico.resposta)

    def ListarMedicos(self, usuario):
        listarMedicos = neonat_pb2.TodosMedicos(usuario = neonat_pb2.Usuario(usuario=usuario))
        respostaListarMedicos = stub.ListarMedicos(listarMedicos)
        print("============== MÉDICOS CADASTRADOS ==============\n")
        for medico in respostaListarMedicos.medicos:
            print('---------------------------------------------------')
            print(f'CRM: {medico.CRM}')
            print(f'Nome do médico: {medico.nome}')
            print(f'Data de nascimento: {medico.dataNasc}')
            print('---------------------------------------------------')

    def PesquisarPacientesMedico(self, usuario):
        print("============== PESQUISAR PACIENTES DE UM MÉDICO ==============\n")
        CRM = input('Insira o CRM do médico: ')
        listarPacientesMedico = neonat_pb2.TodosPacientesMedico(CRM=CRM, 
        usuario = neonat_pb2.Usuario(usuario=usuario))

        respostalistarPacientesMedico = stub.PesquisarPacientesMedico(listarPacientesMedico)
        if len(respostalistarPacientesMedico.pacientes) == 0:
            print('Nenhum paciente encontrado para este médico.')
        else:
            for paciente in respostalistarPacientesMedico.pacientes:
                if paciente.idPaciente == "Médico não encontrado":
                    print('Médico não encontrado')
                else:
                    print('---------------------------------------------------')
                    print(f'ID Paciente: {paciente.idPaciente}')
                    print(f'Nome paciente: {paciente.nomeRN}')
                    print(f'Data de Nascimento: {paciente.dataHoraNasc}')
                    print('---------------------------------------------------')

               
def run_client():

    print("================= LOGIN NO SISTEMA =================\n")
    usuario = input('Usuário: ')
    if usuario == '':
        run_client()

    cliente = Client()
    cliente.menu()

    while True:
        try:
            print('\n')
            comando = input('Digite a opção desejada: ')
            print('\n\n')
            if comando == '0':
                break
            elif comando == 'menu':
                cliente.menu()
            elif comando == '1':
                cliente.RegistrarPaciente(usuario)
            elif comando == '2':
                cliente.AtualizarPaciente(usuario)
            elif comando == '3':
                cliente.DeletarPaciente(usuario)
            elif comando == '4':
                cliente.ConsultarPaciente(usuario)
            elif comando == '5':
                cliente.ListarPacientes(usuario)

            elif comando == '6':
                cliente.RegistrarProcedimentos(usuario)
            elif comando == '7':
                cliente.AtualizarProcedimentos(usuario)
            elif comando == '8':
                cliente.DeletarProcedimentos(usuario)
            elif comando == '9':
                cliente.ConsultarProcedimentos(usuario)
            elif comando == '10':
                cliente.ListarProcedimentos(usuario)

            elif comando == '11':
                cliente.RegistrarMedico(usuario)
            elif comando == '12':
                cliente.ListarMedicos(usuario)
            elif comando == '13':
                cliente.PesquisarPacientesMedico(usuario)
            else:
                print('Comando não válido.')
                pass
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f'{e}')
            print('Erro. Tente novamente')
            pass
        

if __name__ == "__main__":
    run_client()