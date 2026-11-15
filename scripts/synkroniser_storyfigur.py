"""Synkroniser status i avhengighetsfiguren med sprint-status.yaml."""

import argparse
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
SPRINT = ROOT / "_bmad-output/implementation-artifacts/sprint-status.yaml"
FIGUR = ROOT / "docs/figurer/epics-stories-avhengigheter.svg"
STATUSER = {"backlog", "ready-for-dev", "in-progress", "review", "done"}
NODE = re.compile(r'<g><rect (?P<rect>[^>]*class=")(?P<class>done|todo)(?P<tail>"/>)<text [^>]*>(?P<id>\d+\.\d+) [^<]*</text><text [^>]*class="label">(?P<label>[^<]*)</text></g>')


def oppdater(sprint: str, figur: str) -> str:
    """Returner oppdatert SVG, eller avvis ufullstendige eller tvetydige data."""
    ET.fromstring(figur)
    seksjoner = list(re.finditer(r"(?ms)^development_status:[ \t]*\n(.*?)(?=^\S|\Z)", sprint))
    if len(seksjoner) != 1:
        raise ValueError("Sprintstatus må ha nøyaktig én development_status.")
    status = {}
    for line in seksjoner[0].group(1).splitlines():
        if re.match(r"^\s+\d+-\d+-", line):
            match = re.fullmatch(r"  (\d+)-(\d+)-[^:]+:[ \t]*([^\s#]+)[ \t]*(?:#.*)?", line)
            if not match:
                raise ValueError(f"Ugyldig storylinje: {line.strip()}")
            ident = f"{int(match[1])}.{int(match[2])}"
            if ident in status or match[3] not in STATUSER:
                raise ValueError(f"Duplikat eller ukjent status for {ident}.")
            status[ident] = match[3]
    if not status:
        raise ValueError("Fant ingen storyer i sprintstatus.")
    sett = set()

    def bytt(match: re.Match) -> str:
        ident = match['id']
        if ident in sett or ident not in status:
            raise ValueError(f"Duplikat eller ukjent story i figuren: {ident}.")
        sett.add(ident)
        ferdig = status[ident] == "done"
        label = match['label']
        if not ferdig and label.startswith('Ferdig · '):
            label = label[len('Ferdig · '):]
        elif not ferdig and label == 'Ferdig':
            label = 'Gjenstår'
        elif ferdig and label == 'Gjenstår':
            label = 'Ferdig'
        node = match[0]
        node = node.replace('class="' + match['class'] + '"', 'class="' + ('done' if ferdig else 'todo') + '"', 1)
        return node.replace('class="label">' + match['label'] + '</text>', 'class="label">' + label + '</text>', 1)

    resultat = NODE.sub(bytt, figur)
    if len(sett) != len(re.findall(r'<g>\s*<rect\b', figur)):
        raise ValueError('En story i figuren har et ukjent format eller er duplisert.')
    if sett != set(status):
        raise ValueError(f"Storyer mangler i figuren: {', '.join(sorted(set(status) - sett))}")
    return resultat


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sjekk', action='store_true', help='Kontroller uten å skrive.')
    args = parser.parse_args()
    try:
        original = FIGUR.read_text(encoding='utf-8')
        resultat = oppdater(SPRINT.read_text(encoding='utf-8'), original)
        if resultat != original:
            if args.sjekk:
                print('Figuren er utdatert. Kjør python scripts/synkroniser_storyfigur.py.', file=sys.stderr)
                return 1
            FIGUR.write_text(resultat, encoding='utf-8', newline='\n')
            print('Figuren er oppdatert.')
        else:
            print('Figuren stemmer med sprintstatus.')
        return 0
    except (ValueError, OSError, ET.ParseError) as feil:
        print(f'Kan ikke kontrollere figuren: {feil}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
