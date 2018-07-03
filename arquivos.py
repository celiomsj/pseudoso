class Arquivo(object):
    ''' Arquivo de disco.'''

    def __init__(self, nome, inicio, tamanho, criador=None):
        self.nome = nome
        self.inicio = inicio
        self.tamanho = tamanho
        self.criador = criador

    def __str__(self):
        return "Arquivo: {}".format(', '.join([str(x) for x in self.__dict__.values()]))

    __repr__ = __str__


class OperacoesSA(object):
    ''' Classe para representar operações de disco no sistema de arquivos.'''

    def __init__(self, pid, cod_operacao, nome_arquivo, tamanho=None):
        self.pid = pid
        self.cod_operacao = cod_operacao
        self.nome_arquivo = nome_arquivo
        self.tamanho = tamanho

    def __str__(self):
        return "Operacao:{}".format(', '.join([str(x) for x in self.__dict__.values()]))

    __repr__ = __str__


class Disco(object):
    '''
    Classe para representação de disco e operações de gerência
    do sistema de arquivos.
    '''

    def __init__(self):
        self.qtd_blocos = None
        self.qtd_segmentos = None
        self.arquivos = None
        self.operacoes = None
        self.contador = 0
    
    def alocacao(self):
        ''' Retorna lista representando o mapa de bits do disco.'''
        mapa = ['0']*self.qtd_blocos
        arqs = sorted(self.arquivos, key=lambda x: x.inicio)
        for arq in arqs:
            mapa[arq.inicio:arq.inicio+arq.tamanho] = arq.nome * arq.tamanho
        
        return mapa

    def deleta_arquivo(self, processo, nome_arquivo):
        ''' Deleta arquivo no disco.'''
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
        ''' Cria arquivo no disco.'''
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
        ''' Procura arquivo no disco dado o nome, ou retorna None.'''
        return next((arq for arq in self.arquivos if arq.nome == nome_arquivo), None)

    def procura_espaco_livre(self, tamanho):
        ''' Procura por espaço contíguo disponível no disco.'''
        disco = ''.join(self.alocacao())
        return disco.find('0'*tamanho)

    def executa_operacoes(self, tabela_processos):
        ''' Executa operações no sistema de arquivos.'''
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
        ''' Formato de impressão. Retorna mapa de bits do disco.'''
        return ''.join(self.alocacao())


def le_disco(arq_disco='files.txt'):
    ''' Carrega as informações do disco e as operações a serem executadas.'''
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
