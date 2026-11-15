import unittest
from unittest.mock import patch
import tempfile
from pathlib import Path

import synkroniser_storyfigur as modul
from synkroniser_storyfigur import oppdater


def figur(*noder):
    return '<svg>' + ''.join(
        f'<g><rect class="{farge}"/><text x="1">{ident} Navn</text>'
        f'<text class="label">{tekst}</text></g>'
        for ident, farge, tekst in noder
    ) + '</svg>'


class StoryfigurTest(unittest.TestCase):
    def test_status_og_notat_er_reversibelt(self):
        sprint = 'development_status:\n  1-1-navn: done\n'
        original = figur(('1.1', 'todo', 'Etter 1.0'))
        ferdig = oppdater(sprint, original)
        self.assertIn('class="done"', ferdig)
        self.assertIn('>Etter 1.0</text>', ferdig)
        self.assertEqual(ferdig, oppdater(sprint, ferdig))
        self.assertEqual(original, oppdater(sprint.replace('done', 'review'), ferdig))

    def test_ren_statustekst(self):
        sprint = 'development_status:\n  1-1-navn: done\n'
        resultat = oppdater(sprint, figur(('1.1', 'todo', 'Gjenstår')))
        self.assertIn('>Ferdig</text>', resultat)

    def test_ukjent_status_eller_manglende_og_dupliserte_storyer_avvises(self):
        node = ('1.1', 'todo', 'Gjenstår')
        for sprint, svg in [
            ('development_status:\n  1-1-navn: feil\n', figur(node)),
            ('development_status:\n  1-1-navn: done\n', figur()),
            ('development_status:\n  1-1-navn: done\n', figur(node, node)),
            ('development_status:\n  1-1-navn: done\n  1-1-annet: done\n', figur(node)),
            ('development_status:\n  1-1-navn: done feil\n', figur(node)),
            ('development_status:\n  1-1-navn: done\n  1-1-navn: # tom\n', figur(node)),
            ('development_status:\n  1-1-navn: done\ndevelopment_status:\n  1-1-navn: review\n', figur(node)),
        ]:
            with self.subTest(sprint=sprint, svg=svg), self.assertRaises(ValueError):
                oppdater(sprint, svg)

    def test_sjekk_finner_avvik_uten_a_skrive(self):
        with tempfile.TemporaryDirectory() as mappe:
            sprint = Path(mappe) / 'sprint.yaml'
            svg = Path(mappe) / 'figur.svg'
            sprint.write_text('development_status:\n  1-1-navn: done\n', encoding='utf-8')
            gammel = figur(('1.1', 'todo', 'Gjenstår'))
            svg.write_text(gammel, encoding='utf-8')
            with patch.object(modul, 'SPRINT', sprint), patch.object(modul, 'FIGUR', svg), patch('sys.argv', ['script', '--sjekk']):
                self.assertEqual(1, modul.main())
            self.assertEqual(gammel, svg.read_text(encoding='utf-8'))
            with patch.object(modul, 'SPRINT', sprint), patch.object(modul, 'FIGUR', svg), patch('sys.argv', ['script']):
                self.assertEqual(0, modul.main())
            self.assertIn('class="done"', svg.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
