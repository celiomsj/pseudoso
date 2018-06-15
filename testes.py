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


if __name__ == '__main__':
    unittest.main()