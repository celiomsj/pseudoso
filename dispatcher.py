import time
from memoria import *
from arquivos import *
from processos import *


class Dispatcher(object):

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
        novos = [p for p in self.tabela_processos.lista if p.t_inicial == self.tempo]
        for processo in novos:
            if (self.cria_processo(processo)):
                # self.tabela_processos.lista.remove(processo)
                if processo.prioridade > 0:
                    processo.estado = 1  # Suspenso
                else:  # prioridade 0
                    processo.estado = 2  # Pronto

                # Envia para o escalonador
                print("Inserindo processo {} na fila.".format(processo.pid))
                self.insere(processo)

        return


    def insere(self, processo):
        
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

        while True:

            self.novos_processos()
            #self.g_filas.escalonar()
            
            if self.cpu is not None:
                self.executaProcesso(self.cpu)
            else:
                p_atual = self.g_filas.escolher()
                if p_atual is not None:
                    print("Dispatcher =>")
                    print("\tPID:\t{}".format(p_atual.pid))
                    print("\toffset:\t{}".format(p_atual.bloco_inicio))
                    
                    self.executaProcesso(p_atual)
                    self.atualiza_processo(p_atual)
                else:
                    self.executaProcesso(p_atual)  # O método trata o caso que p_atual é None

                

            if self.acabou():
                break  # Sai do loop

        return


    def acabou(self):
        return all([p.estado == 5 for p in self.tabela_processos.lista])


    def executaProcesso(self, processo):

        if processo is None:
            self.tempo += self.quantum  # Clock tick
            time.sleep(0.1)
            print("Não há processo a ser executado.")
            return
        

        if not(self.ultima_execucao == processo):
            print("Process {} =>".format(processo.pid))

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


        if processo.t_CPU == 0:
            processo.estado = 5  # Completo
            self.g_memoria.libera(processo)
            self.g_recursos.desaloca(processo)
            self.cpu = None
            print("P{} return SIGINT".format(processo.pid))
        else:
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

        print("Sistema de arquivos =>")

        self.g_disco.executa_operacoes(self.tabela_processos)

        # Imprime mapa de bits
        print("Mapa de bits do disco:")
        print(self.g_disco)



def le_processos(arq_processos='processes.txt'):

    tabela = TabelaProcessos()
    
    with open(arq_processos, 'r') as f:
        lines = f.read().splitlines()
        for line in lines:
            line = line.split(', ')
            a = Processo()
            a.t_inicial = int(line[0])
            a.prioridade = int(line[1])
            a.t_CPU = int(line[2])
            a.t_utilizado = 0
            a.blocos_mem = int(line[3])
            a.cod_impressora = int(line[4])
            a.scanner = int(line[5])
            a.modem = int(line[6])
            a.cod_disco = int(line[7])
            a.estado = 0  # Shay states

            tabela.lista.append(a)

    return tabela








def main():
    
    tbl_processos = le_processos()

    sistema_arquivos = le_disco()

    # for b in tbl_processos.lista:
    #     print(b)

    # for b in sistema_arquivos.__dict__.values():
    #     print(b)

    # print(sistema_arquivos)

    dispatcher = Dispatcher(tbl_processos, sistema_arquivos)
    dispatcher.executa()

    dispatcher.executa_operacoesSA()


if __name__ == '__main__':
    main()