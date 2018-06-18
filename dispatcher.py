
class Processo(object):
    
    def __init__(self):
        self.pid = None
        self.t_inicial = None
        self.prioridade = None
        self.t_CPU = None
        self.bloco_inicio = None
        self.blocos_mem = None
        self.cod_impressora = None
        self.scanner = None
        self.modem = None
        self.cod_disco = None


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
            return False
        else:
            if processo.prioridade == 0:
                # O arquivo existe, o processo tem permissao e 
                # é preciso excluí-lo do disco.
                # TODO: Incluir operação no log.
                self.qtd_segmentos -= 1
                self.arquivos.remove(arq)
                return True

            elif processo.prioridade > 0 and processo.pid == arq.criador:
                self.qtd_segmentos -= 1
                self.arquivos.remove(arq)
                return True

            else:
                return False


    def cria_arquivo(self, processo, nome_arquivo, tamanho):
        
        if self.procura_arquivo(nome_arquivo) is not None:
            return False

        inicio = self.procura_espaco_livre(tamanho)
        if inicio == -1:
            return False

        arq = Arquivo(nome_arquivo, inicio, tamanho, processo.pid)
        self.arquivos.append(arq)
        self.qtd_segmentos += 1
        # TODO: incluir operação no log

        return True

        

    def procura_arquivo(self, nome_arquivo):
        ''' Procura arquivo no disco dado o nome, ou retorna None
        '''
        return next((arq for arq in self.arquivos if arq.nome == nome_arquivo), None)


    def procura_espaco_livre(self, tamanho):
        
        disco = ''.join(self.alocacao())
        return disco.find('0'*tamanho)
        
        

    def __str__(self):
        return ''.join(self.alocacao())



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
            a.blocos_mem = int(line[3])
            a.cod_impressora = int(line[4])
            a.scanner = int(line[5])
            a.modem = int(line[6])
            a.cod_disco = int(line[7])

            tabela.lista.append(a)

    return tabela

    # with open(arq_processos, 'r') as f:
    #     lines = f.read().splitlines()
    #     for line in lines:
    #         for s in line.split(','):
    #             print(s)

    # with open(arq_processos, 'r') as f:
    #     for line in f:
    #         print(line, end='')


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

    for b in tbl_processos.lista:
        print(b)

    for b in sistema_arquivos.__dict__.values():
        print(b)

    print(sistema_arquivos)

if __name__ == '__main__':
    main()