import time


class Processo(object):
    
    def __init__(self):
        self.pid = None
        self.t_inicial = None
        self.prioridade = None
        self.t_CPU = None
        self.t_utilizado = None
        self.bloco_inicio = None
        self.blocos_mem = None
        self.cod_impressora = None
        self.scanner = None
        self.modem = None
        self.cod_disco = None
        self.estado = None


    def __str__(self):
        # return "Processo: Tempo inicial={}".format(self.t_inicial)
        return "Processo: {}".format(', '.join([str(x) for x in self.__dict__.values()]))


class TabelaProcessos(object):
    
    def __init__(self):
        self.lista = []


class Memoria(object):

    def __init__(self, mem_total = 1024, mem_tempo_real = 64):
        self.memoria = [None]*mem_total
        self.mem_reservada = mem_tempo_real

    def aloca(self, processo):
        
        inicio = 0
        fim = len(self.memoria)
        vazios = 0

        if processo.bloco_inicio is not None:
            return False

        if processo.prioridade == 0:
            fim = self.mem_reservada
        elif processo.prioridade > 0:
            inicio = self.mem_reservada
        
        for i in range(inicio, fim):
            if self.memoria[i] == None:
                vazios += 1
                if vazios == processo.blocos_mem:
                    processo.bloco_inicio = i - vazios + 1
                    self.memoria[i-vazios+1:i] = processo.blocos_mem * [processo.pid]
                    return True
            
            else:
                vazios = 0
            
        return False


    def libera(self, processo):
        self.memoria[processo.bloco_inicio:processo.bloco_inicio + processo.blocos_mem] = [None]*processo.blocos_mem
        processo.bloco_inicio = None
        return True


    def __str__(self):
        def f(x):
            if x is None:
                return str(0)
            else:
                return str(x)
        return ''.join(list(map(f, self.memoria)))


class GerenciadorRecursos(object):
    
    def __init__(self):
        self.scanner = None
        self.printer = [None]*2
        self.modem = None
        self.disco = [None]*2


    def aloca(self, processo):

        if processo.prioridade == 0:
            return True

        estado = self.__dict__.copy()
        sucesso = True

        if processo.scanner is not None:
            if self.scanner is not None:
                sucesso = False
            else:
                self.scanner = processo.pid
        
        if processo.modem is not None:
            if self.modem is not None:
                sucesso = False
            else:
                self.modem = processo.pid

        if processo.cod_impressora is not None:
            if self.printer[processo.cod_impressora] is not None:
                sucesso = False
            else:
                self.printer[processo.cod_impressora] = processo.pid
        
        if processo.cod_disco is not None:
            if self.disco[processo.cod_disco] is not None:
                sucesso = False
            else:
                self.disco[processo.cod_disco] = processo.pid

        if sucesso:
            return True
        else:
            self.__dict__.update(estado)
            return False

    def desaloca(self, processo):

        if processo.prioridade == 0:
            return

        if processo.scanner and self.scanner == processo.pid:
            self.scanner = None
        
        if processo.modem and self.modem == processo.pid:
            self.modem = None

        if processo.cod_impressora and self.printer[processo.cod_impressora] == processo.pid:
            self.printer[processo.cod_impressora] = None

        if processo.cod_disco and self.disco[processo.cod_disco] == processo.pid:
            self.disco[processo.cod_disco] = None
        
        return


class Arquivo(object):

    def __init__(self, nome, inicio, tamanho, criador=None):
        self.nome = nome
        self.inicio = inicio
        self.tamanho = tamanho
        self.criador = criador

    def __str__(self):
        return "Arquivo: {}".format(', '.join([str(x) for x in self.__dict__.values()]))

    __repr__ = __str__

class OperacoesSA(object):

    def __init__(self, pid, cod_operacao, nome_arquivo, tamanho=None):
        self.pid = pid
        self.cod_operacao = cod_operacao
        self.nome_arquivo = nome_arquivo
        self.tamanho = tamanho

    def __str__(self):
        return "Operacao:{}".format(', '.join([str(x) for x in self.__dict__.values()]))

    __repr__ = __str__


class Disco(object):

    def __init__(self):
        self.qtd_blocos = None
        self.qtd_segmentos = None
        self.arquivos = None
        self.operacoes = None
        self.contador = 0
    
    def alocacao(self):
        mapa = ['0']*self.qtd_blocos
        arqs = sorted(self.arquivos, key=lambda x: x.inicio)
        for arq in arqs:
            mapa[arq.inicio:arq.inicio+arq.tamanho] = arq.nome * arq.tamanho
        
        return mapa

    def deleta_arquivo(self, processo, nome_arquivo):
        
        arq = self.procura_arquivo(nome_arquivo)
        if arq is None:
            # arquivo não existe
            print("Operação {} => Falha".format(self.contador))
            print("O arquivo {} não existe.\n".format(nome_arquivo))
            return False
        else:
            if processo.prioridade == 0:
                # O arquivo existe, o processo tem permissao e 
                # é preciso excluí-lo do disco.
                self.qtd_segmentos -= 1
                self.arquivos.remove(arq)
                print("Operação {} => Sucesso".format(self.contador))
                print("O processo {} deletou o arquivo {}.\n".format(processo.pid, nome_arquivo))
                return True

            elif processo.prioridade > 0 and processo.pid == arq.criador:
                self.qtd_segmentos -= 1
                self.arquivos.remove(arq)
                print("Operação {} => Sucesso".format(self.contador))
                print("O processo {} deletou o arquivo {}.\n".format(processo.pid, nome_arquivo))
                return True

            else:
                print("Operação {} => Falha".format(self.contador))
                print("O processo {} não pode deletar o arquivo {}.\n".format(processo.pid, nome_arquivo))
                return False


    def cria_arquivo(self, processo, nome_arquivo, tamanho):
        
        if self.procura_arquivo(nome_arquivo) is not None:
            print("Operação {} => Falha".format(self.contador))
            print("Arquivo {} já existe.\n".format(nome_arquivo))
            return False

        inicio = self.procura_espaco_livre(tamanho)
        if inicio == -1:
            print("Operação {} => Falha".format(self.contador))
            print("O processo {} não pode criar o arquivo {} (falta de espaço).\n".format(processo.pid, nome_arquivo))
            return False

        arq = Arquivo(nome_arquivo, inicio, tamanho, processo.pid)
        self.arquivos.append(arq)
        self.qtd_segmentos += 1
        print("Operação {} => Sucesso".format(self.contador))
        print("O processo {} criou o arquivo {} (inicio {}, tamanho {}).\n".format(processo.pid, nome_arquivo, inicio, tamanho))

        return True

        

    def procura_arquivo(self, nome_arquivo):
        ''' Procura arquivo no disco dado o nome, ou retorna None
        '''
        return next((arq for arq in self.arquivos if arq.nome == nome_arquivo), None)


    def procura_espaco_livre(self, tamanho):
        
        disco = ''.join(self.alocacao())
        return disco.find('0'*tamanho)


    def executa_operacoes(self, tabela_processos):
        
        for op in self.operacoes:
            self.contador += 1
            # Procura processo na tabela de processos.
            processo = next((p for p in tabela_processos.lista if p.pid == op.pid), None)
            if processo == None:
                print("Operação {} => Falha".format(self.contador))
                print("Não existe o processo.\n")
            else:
                if op.cod_operacao == 0:
                    self.cria_arquivo(processo, op.nome_arquivo, op.tamanho)
                elif op.cod_operacao == 1:
                    self.deleta_arquivo(processo, op.nome_arquivo)


    
    def __str__(self):
        return ''.join(self.alocacao())


class Escalonador(object):

    def __init__(self):
        self.max = 1000
        self.tabela_processos = None
        self.fila_global = []
        self.fila_tr = []
        self.fila_p1 = []
        self.fila_p2 = []
        self.fila_p3 = []

    def escolher(self):
        
        if len(self.fila_tr) > 0:
            return self.fila_tr.pop(0)

        if len(self.fila_p1) > 0:
            return self.fila_p1.pop(0)

        if len(self.fila_p2) > 0:
            return self.fila_p2.pop(0)

        if len(self.fila_p3) > 0:
            return self.fila_p3.pop(0)

        return None



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




def le_disco(arq_disco='files.txt'):
    
    disco = Disco()

    with open(arq_disco, 'r') as f:
        lines = f.read().splitlines()
        disco.qtd_blocos = int(lines.pop(0))
        disco.qtd_segmentos = int(lines.pop(0))
        
        arqs = lines[:disco.qtd_segmentos]
        disco.arquivos = []
        for arq in arqs:
            arq = arq.split(', ')
            disco.arquivos.append(Arquivo(arq[0], int(arq[1]), int(arq[2])))
            
        operacoes = lines[disco.qtd_segmentos:]
        disco.operacoes = []
        for operacao in operacoes:
            operacao = operacao.split(', ')
            if int(operacao[1]) == 0:
                op = OperacoesSA(int(operacao[0]), int(operacao[1]), operacao[2], int(operacao[3]))
            else:
                op = OperacoesSA(int(operacao[0]), int(operacao[1]), operacao[2])
            disco.operacoes.append(op)

    return disco



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