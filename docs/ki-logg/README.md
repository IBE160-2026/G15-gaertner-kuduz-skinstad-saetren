# KI-logg

Dokumentasjon av hvordan KI ble brukt i prosjektet, og hvordan koden er
kvalitetssikret. Emnet vurderer dette — se `addendum.md` punkt 5.

## Hva som logges her

Én fil per arbeidsøkt som genererer kode: `<dato>-<tema>.md`, for eksempel
`2026-10-04-regelmotor-hviletid.md`. Innhold:

- **Oppgaven** — hva som skulle løses
- **Prompten** — ordrett, ikke omskrevet i etterkant
- **Hva modellen leverte** — og om det fungerte
- **Hva som ble rettet, og hvorfor** — den viktigste delen
- **Kvalitetssikring** — hvilke tester som dekker resultatet

Loggen er skrevet av den som gjorde arbeidet. Er den skrevet av en agent, er
den egenrapportering: et gruppemedlem bør lese gjennom og korrigere. En logg
uten en eneste innvending mot KI-en er ikke en vurdering.

## Spørringer til innlevering

Alle er kjørt og verifisert mot repoet. `$EX` holder BMAD-rammeverket utenfor,
ellers drukner prosjektets egne filer i 446 rammeverksfiler.

```bash
EX=(':(exclude)_bmad/*' ':(exclude).claude/*' ':(exclude).agents/*')
```

**Hvilke filer vi stadig var tilbake i** — høy churn betyr enten sentral fil
eller beslutning som ble snudd. Les commit-meldingene for å se hvilken.

```bash
git log --format= --name-only --diff-filter=M -- . "${EX[@]}" \
  | grep . | sort | uniq -c | sort -rn
```

**Omarbeid mot nytt arbeid** — forholdet mellom commits som endrer eksisterende
filer og commits som legger til nye.

```bash
echo "endrer eksisterende: $(git log --format=%h --diff-filter=M -- . "${EX[@]}" | wc -l)"
echo "legger til nytt    : $(git log --format=%h --diff-filter=A -- . "${EX[@]}" | wc -l)"
```

**Commits der KI var involvert** — `Co-Authored-By` settes automatisk når en
agent skriver commiten, så tallet krever ingen disiplin. Forbehold: commiter et
gruppemedlem KI-generert kode manuelt, mangler linja.

```bash
echo "$(git log --format='%(trailers:key=Co-Authored-By,valueonly)' | grep -c .) av $(git log --format=%h | wc -l)"
```

**Utvikling over tid** — aktivitet per måned. Kombinert med churn viser den om
omarbeidet avtok utover i prosjektet.

```bash
git log --format='%ad' --date=format:'%Y-%m' | sort | uniq -c
```

**Commits som endret tidligere arbeid, med begrunnelse** — råmaterialet til
refleksjonsrapporten. Brødteksten skal si hvorfor vi var tilbake i fila.

```bash
git log --format='%h %ad %s%n%b' --date=short --diff-filter=M -- . "${EX[@]}"
```

## Hvorfor det ikke finnes en `KI:`-trailer

Vurdert og forkastet 2026-09-23. En etikett per commit (`generert`,
`rettet`, `manuell`) ville gitt tellbar statistikk, men nesten all kode her er
KI-generert — så etiketten ville vært tilnærmet konstant, og en konstant måler
ingenting. En etikett som anvendes inkonsekvent er dessuten verre enn ingen:
mangler den på 20 av 84 commits, er hele datasettet ubrukelig, ikke bare de 20.

Git måler allerede mengden omarbeid, som spørringene over viser. Det git ikke
kan vite, er *hvorfor* vi var tilbake i en fil. Derfor bærer brødteksten den
informasjonen i stedet — prosa tåler slurv bedre enn et format gjør.
