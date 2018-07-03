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
