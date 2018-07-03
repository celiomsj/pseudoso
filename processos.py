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
