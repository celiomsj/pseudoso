class Processo(object):
    ''' Estrutura de dados de representação de um processo.'''
    
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
    ''' Tabela de Processos.'''
    def __init__(self):
        self.lista = []


class Escalonador(object):
    ''' Escalonador de processos. Faz o gerenciamento das filas de prioridades.'''
    def __init__(self):
        self.max = 1000
        self.tabela_processos = None
        self.fila_global = []
        self.fila_tr = []
        self.fila_p1 = []
        self.fila_p2 = []
        self.fila_p3 = []

    def escolher(self):
        ''' Seleciona um processo para ser executado.'''        
        if len(self.fila_tr) > 0:
            return self.fila_tr.pop(0)

        if len(self.fila_p1) > 0:
            return self.fila_p1.pop(0)

        if len(self.fila_p2) > 0:
            return self.fila_p2.pop(0)

        if len(self.fila_p3) > 0:
            return self.fila_p3.pop(0)

        return None
