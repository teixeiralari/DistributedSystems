# ***Reverse Shell***

## Descrição do projeto e suas funções

### Objetivo

- O objetivo deste trabalho consiste em implementar um *reserve shell* utilizando *sockets* em python. 
- *Sockets* são usados para enviar dados através da rede.

### O que é um ***Reverse Shell***?

- Um *reverse shell* (shell reverso), força uma conexão de volta ao computador
de ataque. Nesse caso, em nosso computador de ataque, abrimos uma porta local e ficamos ouvindo à espera de uma conexão feita a partir de nosso alvo porque é mais provável que essa conexão reversa consiga passar por um firewall **(WEIDMAN, Georgia – 2014, p. 138)**.
Em outras palavras, a máquina do invasor (que tem um IP público e pode ser acessado pela Internet) age como um servidor. Ele abre um canal de comunicação em uma porta e aguarda por conexões de entrada. A máquina da vítima atua como um cliente e inicia uma conexão com o servidor de escuta do invasor.
- O servidor ganha acesso à máquina invadida e consegue executar comandos no *shell* (terminal, prompt).

### O lado servidor

- O servidor estará esperando por conexões o tempo inteiro e roda em um IP
público.
- Serão utilizadas duas ***threads***:
    - ***Thread* 1**: Responsável por ouvir e aceitar conexões.
    - ***Thread* 2**: Enviar comandos para o cliente e lidar com clientes existentes.
- Além dos comandos existentes no *shell*, como o servidor estará conectado com múltiplos clientes, dois comandos para o servidor serão adicionados:
    - *list*: Lista todos os clientes (vítimas) que estão atualmente conectados ao servidor.
    - *select*: Seleciona o cliente que será atacado.

### O lado cliente

- Conecta ao servidor e espera os comandos.
- Múltiplos clientes acessando ao mesmo tempo.
- O cliente não saberá que está sendo atacado.
- Todos os dados existentes no computador do cliente atacado poderão ser acessados.

## Testes que serão executados

- Para realizar os testes, o servidor estará sendo executado em uma máquina
virtual instanciada na nuvem utilizando *AWS - Cloud Computing Services* ou
*Digital Ocean*.
- Múltiplos clientes serão conectados para testar o acesso simultâneo ao serviço descrito.
- Será feito um script para o servidor, se necessário, ficar mandando comandos aleatóriamente para testar qualquer tipo de erro que possa acontecer e evitar que o sistema caia.

## Bibliografia

- http://voudarumjeito.blogspot.com/2014/08/se-protegendo-contra-um-shell-reverso.html
- https://tiagosouza.com/reverse-shell-cheat-sheet-bind-shell/

