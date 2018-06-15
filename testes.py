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


if __name__ == '__main__':
    unittest.main()