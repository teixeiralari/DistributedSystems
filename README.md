# ***Chat one-to-one***
## Membros
- Henrique Morais Jacob Medeiros 
- Larissa Roberta Teixeira
- Murillo Henrique Pessoa de Lima
- Tawane Paula Menezes

## Descrição do projeto
### Objetivo

O objetivo deste trabalho consiste em implementar um chat, utilizando *sockets* em python. 
*Sockets* são usados para enviar dados através da rede.

## Funcionamento
#### O Cliente
Um cliente pode receber e mandar mensagens para vários clientes, mas essas mensagens são privadas, ou seja, de cliente para cliente. O servidor é o intermediário, fica responsável por encaminhar as mensagens do remetente ao destinatário.
Neste chat são implementados três comandos para o cliente:
- *list*: Quando o cliente digita este comando, o servidor fica responsável por enviar ao cliente uma lista de todos os clientes conectados naquele momento;
- *send*: Este comando serve para o cliente enviar alguma mensagem a um outro cliente. O cliente precisa digitar o email de destino e a mensagem que deseja enviar. O servidor fica responsável por enviar a mensagem;
- *quit*: O cliente se desconecta do chat;
- *history*: Ver histórico de mensagens enviadas e recebidas;
- *menu*: Mostrar o menu novamente;

#### O Servidor
O servidor fica responsável por entender todos os comandos enviados pelo cliente.
O servidor possui um arquivo de log, nomeado como ***log.txt***. Neste arquivo é gravada todas a mensagens enviadas, independentes de terem sido entregues ou não. Nele contém quatro campos:
- ***sender***: Cliente remetente;
- ***receiver***: Cliente destinatário;
- ***message***: Mensagem que será enviada do cliente remetente ao cliente destinatário;
- ***status***: 
    - *status = "OK"*: Se a mensagem foi enviada com sucesso do cliente remetente ao cliente destinatário;
    - *status = "Pending"*: Se a tentativa de enviar a mensagem falhou;

Quando o remetente tenta enviar uma mensagem para o destinatário, existem três possibilidades:
1. O destinatário está online, então a mensagem será entregue com sucesso, a mensagem será gravada no arquivo de log com o status *OK*;
2. O destinatario está offline, então a mensagem ficará gravada no arquivo de log com o status *Pending*. Quando o destinatário se conectar, a mensagem será enviada e o status mudará para *OK*;
3. O destinatário não existe, então a mensagem nunca será enviada, ou seja, o status no arquivo de log ficará *Pending* para sempre;

### O lado servidor

O servidor estará esperando por conexões o tempo inteiro e roda em um IP
público.
- São utilizadas três ***threads***:
    - 1. ***Thread* 1**: Responsável por ouvir, aceitar conexões e enviar mensagens.
    - 2. ***Thread* 2**: Responsável por inserir no arquivo de log as mensagens que foram enviadas ou que ainda estão aguardando para serem enviadas
    - 3.  ***Thread* 3**: Responsável por ler e enviar as mensagens que estão pendentes no arquivo de log; 

### O lado cliente

- Conecta ao servidor e digita os comandos que deseja;
- Múltiplos clientes acessando ao mesmo tempo;
- O cliente não sabe como o servidor funciona;
- São utilizadas duas ***threads***:
    1. ***Thread* 1**: Responsável receber mensagens do teclado.
    2. ***Thread* 2**: Responsável por lidar com as novas mensagens


## Testes executados

- Múltiplos clientes foram conectados para testar o acesso simultâneo ao serviço descrito;
- O estado do servidor é mantido devido ao arquivo de log implementado;
- O tempo que uma mensagem demora para ser enviada é desprezível;
- Script simulando vários clientes conectados;

## Instalações e execução do *chat one-to-one*

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
        $ python3 -m pip install pandas
        ```
3. Antes de clonar o projeto, entre na pasta, pelo terminal, onde deseja clonar este projeto, depois digite o comando abaixo:
    ```
    $ git clone https://github.com/teixeiralari/DistributedSystems.git
    ```
    
    - Para executar o servidor, digite:
        ```
        $ cd Entrega1/
        $ python server.py
        ```
    - Antes de executar o cliente, no arquivo *client.py*, substitua a variável *host* pelo endereço IP do servidor. Após iniciado o servidor, utilize o comando para a execução do cliente:
        ```
        $ python client.py
        ``` 
    


## Referências
Para implementar este projeto, o tutorial, encontrado no *link* abaixo, foi usado como referência: 
- https://pythonprogramming.net/pickle-objects-sockets-tutorial-python-3/
- https://pythonprogramming.net/server-chatroom-sockets-tutorial-python-3/?completed=/pickle-objects-sockets-tutorial-python-3/

Instalação do python:
- https://linuxize.com/post/how-to-install-python-3-7-on-ubuntu-18-04/



