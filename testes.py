import unittest
from dispatcher import *

class TesteDisco(unittest.TestCase):

    def setUp(self):
        pass

    def test_procura_arquivo(self):

        sa = le_disco()

        self.assertIsNone(sa.procura_arquivo('A'))
        self.assertTrue(sa.procura_arquivo('X').tamanho == 2)

    def test_deleta_arquivo(self):

        sa = le_disco()
        p1 = Processo()
        p1.prioridade = 0

        self.assertTrue(sa.deleta_arquivo(p1, 'X'))
        self.assertEqual(''.join(sa.alocacao()), '000Y0Z0000')

        self.assertFalse(sa.deleta_arquivo(p1, 'X'))
        self.assertFalse(sa.deleta_arquivo(p1, 'A'))

    def test_procura_escapo(self):

        sa = le_disco()

        self.assertEqual(sa.procura_espaco_livre(6), -1)
        self.assertEqual(sa.procura_espaco_livre(1), 2)
        self.assertEqual(sa.procura_espaco_livre(3), 6)

    def test_cria_arquivo(self):

        sa = le_disco()
        p1 = Processo()
        p1.pid = 1

        self.assertFalse(sa.cria_arquivo(p1, 'X', 2))
        self.assertFalse(sa.cria_arquivo(p1, 'A', 6))
        self.assertTrue(sa.cria_arquivo(p1, 'A', 3))
        self.assertEqual(''.join(sa.alocacao()), 'XX0Y0ZAAA0')

    def test_aloca_memoria(self):

        m = Memoria()
        p1 = Processo()
        p1.pid = 1
        p1.prioridade = 0
        p1.blocos_mem = 50
        p2 = Processo()
        p2.pid = 2
        p2.prioridade = 0
        p2.blocos_mem = 50

        self.assertTrue(m.aloca(p1))
        self.assertFalse(m.aloca(p2))
        p2.prioridade = 10
        self.assertTrue(m.aloca(p2))

    def test_libera_memoria(self):

        m = Memoria()
        p1 = Processo()
        p1.pid = 1
        p1.prioridade = 1
        p1.blocos_mem = 100
        
        m.aloca(p1)
        self.assertEqual(p1.bloco_inicio, 64)
        self.assertTrue(m.libera(p1))
        self.assertIsNone(p1.bloco_inicio)


    def test_aloca_recurso(self):

        p1 = Processo()
        p1.pid = 1
        p1.prioridade = 0

        ges = GerenciadorRecursos()

        self.assertTrue(ges.aloca(p1))

        p1.prioridade = 1
        p1.scanner = True

        self.assertTrue(ges.aloca(p1))
        self.assertEqual(ges.scanner, p1.pid)

        p2 = Processo()
        p2.pid = 2
        p2.prioridade = 1
        p2.scanner = True
        self.assertFalse(ges.aloca(p2))

        p2.scanner = None
        p2.cod_disco = 1
        p2.cod_impressora = 0
        self.assertTrue(ges.aloca(p2))
        self.assertEqual(ges.disco[1], p2.pid)

        ges.desaloca(p2)
        self.assertIsNone(ges.disco[1])




if __name__ == '__main__':
    unittest.main()
    