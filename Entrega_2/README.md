# ***Sistema Neonat***
## Membros
- Henrique Morais Jacob Medeiros 
- Larissa Roberta Teixeira
- Murillo Henrique Pessoa de Lima
- Tawane Paula Menezes

## Descrição do projeto
### Objetivo

O objetivo deste trabalho consiste em implementar um sistema de cadastro de médicos, seus respectivos pacientes, e seus procedimentos realizados na UTI Neonatal, armazenando os dados em múltiplos servidores. A comunicação entre cliente e servidores é feita utilizando gRPC em python. 

## Funcionamento
#### O Cliente
Um cliente pode inserir, alterar ou consultar os dados armazenados nos servidores. O servidor fica responsável por reconhecer os comandos solicitados e devolver uma resposta ao cliente conforme a ação solicitada.
Neste sistema são implementados os seguintes comandos para o cliente:

Comandos referente aos pacientes:

- 1: Registrar Paciente.
- 2: Atualizar Paciente.
- 3: Excluir Paciente.
- 4: Consultar um Paciente.
- 5: Listar todos os Pacientes.

Comandos referente aos procedimentos:

- 6: Registrar Procedimentos.
- 7: Atualizar Procedimentos.
- 8: Excluir Procedimentos.
- 9: Consultar Procedimento de um Paciente.
- 10: Listar todos os Procedimentos de um Paciente.

Comandos referente aos médicos:

- 11: Registrar Médico.
- 12: Listar todos os médicos.
- 13: Listar todos os pacientes de um médico.

Comandos Gerais:

- 0: Sair do sistema
- menu: Mostrar o menu novamente

#### O Servidor
- São definidos n servidores que irão atender as requisições dos clientes. 
- Os servidores ficam responsáveis por entender todos os comandos enviados pelo cliente, armazenar e enviar os dados solicitados. 
- Cada servidor é responsável por uma parte dos dados. Caso um dado não seja de responsabilidade do servidor que atendeu a requisição do cliente, este fica responsável por enviar os dados ao servidor correto. 
- Cada servidor armazenam as *hashs* que os outros servidores possuem. Quando um novo servidor se conecta ao anel, ele envia as *hashs* dos pacientes, procedimentos e médicos que possui para os servidores que estão ativos. Os servidores ativos respondem com as *hashs* que possuem.
- Quando um novo arquivo é adicionado ou deletado, o servidor que atendeu a requisição fica responsável por enviar o comando e a *hash* para os outros servidores. Os outros servidores adicionam ou deletam a *hash* de acordo com o comando recebido.  

O servidor possui arquivos de *logs* e *snapshots* que funciona da seguinte forma:
- **Adicionar dados ao arquivo de log**: A cada requisição do cliente que altera o banco de dados (insert, delete e update), é salvo em um arquivo nomeado como **log.txt**, qual a requisição que foi executada e todos os argumentos recebidos.
- **Criar Snapshots e logs**: A cada 10 segundos, é criado um novo arquivo *snapshot.json* e um novo arquivo *log.txt*.
- **Recuperar último estado do servidor**: Quando um novo servidor se conecta, ele lê o último arquivo *snapshot.json* e executa todos os comandos do último arquivo *log.txt*.

##### Threads

O servidor possui algumas threads:
- ***Thread principal***: Responsável por executar o servidor como um todo.
- ***Thread 1***: Responsável por criar os snapshots e logs a cada 10 segundos.
- ***Thread 2***: Responsável por recuperar o último estado do servidor
- ***Thread 3***: Responsável por enviar os dados para o servidor responsável.


## Testes executados

- Múltiplos clientes foram conectados para testar o acesso simultâneo ao serviço descrito;
- O estado do servidor é mantido devido aos arquivos de logs e snapshots implementado;
- Script simulando vários clientes mandando requisições aos servidores;

## Instalações e execução do *Sistema Neonat*

1. Instalação do python: Estes passos são somente para quem usa Linux. Caso use Windows/MAC OS consulte o site do [Python Downloads](https://www.python.org/downloads/). Abra o terminal de comando e siga os passos abaixo:
    - Instalar os pacotes necessários para instalar o python:
        ```
        $ sudo apt update
        $ sudo apt install software-properties-common
        ```
    - Adicionar o deadsnakes PPA ao *source list*:
        ```
        $ sudo add-apt-repository ppa:deadsnakes/ppa
        ```
    - Aperte *ENTER* para continuar:
        ```
        Output
        Press [ENTER] to continue or Ctrl-c to cancel adding it.
        ```
    - Instalar o python 3.7:
        ```
        $ sudo apt install python3.7
        ```
2. Instalação da biblioteca *pandas* utilizada neste projeto:
    - Digite no terminal o seguinte comando:
        ```
        $ python3 -m pip install numpy
        $ python3 -m pip install pandas
        ```
3. Antes de clonar o projeto, entre na pasta, pelo terminal, onde deseja clonar este projeto, depois digite o comando abaixo:
    ```
    $ git clone https://github.com/teixeiralari/DistributedSystems.git
    ```
    
    - Para executar o servidor, digite:
        ```
        $ cd Entrega_2/
        $ python server.py
        ```
    - Antes de executar o cliente, no arquivo *client.py*, substitua a variável *host* pelo endereço IP do servidor. Após iniciado o servidor, utilize o comando para a execução do cliente:
        ```
        $ python client.py
        ``` 
    


## Referências
Instalação do python:
- https://linuxize.com/post/how-to-install-python-3-7-on-ubuntu-18-04/
