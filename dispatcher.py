import sys
import time
from memoria import *
from arquivos import *
from processos import *
from recursos import *


class Dispatcher(object):
    '''
    Classe que realiza o gerenciamento de execução dos processos
    e aciona os demais módulos.
    '''

    def __init__(self, tabela_processos, disco):
        self.cpu = None
        self.tempo = 0
        self.quantum = 1
        self.prox_id = 1
        self.ultima_execucao = None
        self.g_memoria = Memoria()
        self.g_recursos = GerenciadorRecursos()
        self.tabela_processos = tabela_processos
        self.g_filas = Escalonador()
        self.g_disco = disco
    
    def cria_processo(self, processo):
        ''' Cria processo, caso exista memória disponível.'''
        if processo.pid is None:
            # É necessário checar se há memória disponível antes de
            # criar o processo.
            if (self.g_memoria.aloca(processo)):
                processo.pid = self.prox_id
                self.prox_id += 1
                
                print("Processo {} criado".format(processo.pid))
                return True

        # ELSE Erro. Não ha espaco na memoria.
        return False
    
    def novos_processos(self):
        ''' Verifica novos processos que precisam ser criados.'''
        novos = [p for p in self.tabela_processos.lista if p.t_inicial == self.tempo]
        for processo in novos:
            if (self.cria_processo(processo)):
                if processo.prioridade > 0:
                    processo.estado = 1  # Suspenso
                else:  # Prioridade 0
                    processo.estado = 2  # Pronto

                # Insere processo em uma fila do escalonador.
                print("Inserindo processo {} na fila.".format(processo.pid))
                self.insere(processo)

        return

    def insere(self, processo):
        ''' Insere um processo em sua respectiva fila de prioridade.'''
        if processo.prioridade == 0:
            self.g_filas.fila_tr.append(processo)
            return

        else:
            if self.g_recursos.aloca:
                processo.estado = 2  # Pronto
                
                if processo.prioridade == 1:
                    self.g_filas.fila_p1.append(processo)
                elif processo.prioridade == 2:
                    self.g_filas.fila_p2.append(processo)
                elif processo.prioridade == 3:
                    self.g_filas.fila_p3.append(processo)

            else:
                processo.estado = 1  # Suspenso
        
        return        

    def executa(self):
        ''' Loop principal de execução do dispatcher.'''
        while True:
            # Processa se novos processos chegaram neste instante.
            self.novos_processos()
            
            # Se há um processo de tempo real na cpu, ele deve continuar sua execução
            if self.cpu is not None:
                self.executaProcesso(self.cpu)
            # Caso contrário, o dispatcher deve acionar o escalonador e
            # executar outro processo.
            else:
                p_atual = self.g_filas.escolher()
                if p_atual is not None:
                    print("\ndispatcher =>")
                    print("\tPID:\t{}".format(p_atual.pid))
                    print("\toffset:\t{}".format(p_atual.bloco_inicio))
                    print("\tblocks:\t{}".format(p_atual.blocos_mem))
                    print("\tpriority:\t{}".format(p_atual.prioridade))
                    print("\ttime:\t{}".format(p_atual.t_CPU))
                    print("\tprinters:\t{}".format(p_atual.cod_impressora))
                    print("\tscanners:\t{}".format(p_atual.scanner))
                    print("\tmodems:\t{}".format(p_atual.modem))
                    print("\tdrives:\t{}".format(p_atual.cod_disco))
                    
                    self.executaProcesso(p_atual)
                    self.atualiza_processo(p_atual)
                else:
                    self.executaProcesso(p_atual)  # O método trata o caso que p_atual é None

            # Verifica se todos os processos já foram concluídos.
            if self.acabou():
                break  # Sai do loop

        return

    def acabou(self):
        ''' Verifica se todos os processos foram concluídos. '''
        return all([p.estado == 5 for p in self.tabela_processos.lista])

    def executaProcesso(self, processo):
        '''
        Executa uma instrução do processo na CPU. Incrementa o clock
        e imprime informações da execução na tela.
        '''
        if processo is None:
            self.tempo += self.quantum  # Clock tick
            time.sleep(0.1)
            print("Não há processo a ser executado.")
            return
        
        if not(self.ultima_execucao == processo):
            print("\nprocess {} =>".format(processo.pid))

        if processo.prioridade == 0:
            if processo.t_utilizado == 0:
                print("P{} STARTED".format(processo.pid))
        else:
            if processo.t_utilizado == 0:
                print("P{} STARTED".format(processo.pid))
            else:
                print("P{} RESUMED".format(processo.pid))

        self.tempo += self.quantum  # Clock tick
        time.sleep(0.1)

        processo.t_CPU -= self.quantum
        processo.t_utilizado += self.quantum
        self.cpu = processo
        print("P{} instruction {}".format(processo.pid, processo.t_utilizado))
        self.ultima_execucao = processo

        # Caso o processo tenha concluído, liberar os recursos.
        if processo.t_CPU == 0:
            processo.estado = 5  # Completo
            self.g_memoria.libera(processo)
            self.g_recursos.desaloca(processo)
            self.cpu = None
            print("P{} return SIGINT".format(processo.pid))
        else:
            # Se o processo não é de tempo real, é interrompido
            if processo.prioridade > 0:
                self.cpu = None
        
        return

    def atualiza_processo(self, processo):
        '''
        Atualiza o processo nas fila.
        Incrementa a prioridade de processso de usuario.
        '''
        # Se a prioridade for 0, não é necessário fazer nada.
        if processo.prioridade == 1:
            processo.prioridade = 2
            self.g_filas.fila_p2.append(processo)
        elif processo.prioridade == 2:
            processo.prioridade = 3
            self.g_filas.fila_p3.append(processo)
        elif processo.prioridade == 3:
            self.g_filas.fila_p3.append(processo)
   
    def executa_operacoesSA(self):
        '''
        Executa todas as operações especificadas para o
        sistema de arquivos.
        '''
        print("\nSistema de arquivos =>")
        self.g_disco.executa_operacoes(self.tabela_processos)

        # Imprime mapa de bits
        print("Mapa de bits do disco:")
        print(self.g_disco)

def le_processos(arq_processos='processes.txt'):
    '''
    Carrega as informações do arquivo de processos e retorna uma TabelaProcessos.
    '''
    tabela = TabelaProcessos()
    
    with open(arq_processos, 'r') as f:
        lines = f.read().splitlines()
        for line in lines:
            line = line.split(', ')
            p = Processo()
            p.t_inicial = int(line[0])
            p.prioridade = int(line[1])
            p.t_CPU = int(line[2])
            p.t_utilizado = 0
            p.blocos_mem = int(line[3])
            p.cod_impressora = int(line[4])
            p.scanner = int(line[5])
            p.modem = int(line[6])
            p.cod_disco = int(line[7])
            p.estado = 0  # Shay states

            tabela.lista.append(p)

    return tabela


def main():
    '''
    Carrega os arquivos de entrada e executa o dispatcher, realizando
    o gerenciamento dos processos e as operações no sistema de arquivos.
    '''
    if len(sys.argv) > 2:
        arq_processos = sys.argv[1]
        arq_disco = sys.argv[2]
    else:
        arq_processos = 'processes.txt'
        arq_disco = 'files.txt'

    # Carrega as informações dos arquivos nas estruturas de dados
    tbl_processos = le_processos(arq_processos)
    sistema_arquivos = le_disco(arq_disco)

    dispatcher = Dispatcher(tbl_processos, sistema_arquivos)
    dispatcher.executa()

    # Executa as operações no sistema de arquivos. Utiliza a lista de
    # processos criados anteriormente.
    dispatcher.executa_operacoesSA()


if __name__ == '__main__':
    main()
