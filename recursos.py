class GerenciadorRecursos(object):
    ''' Gerenciador de Recursos.'''
    
    def __init__(self):
        self.scanner = None
        self.printer = [None]*2
        self.modem = None
        self.disco = [None]*2

    def aloca(self, processo):
        ''' Atribui um ou mais recursos para um processo.'''
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
        ''' Libera todos os recursos alocados a um processo.'''
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
