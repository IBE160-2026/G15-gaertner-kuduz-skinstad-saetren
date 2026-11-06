# Automatisk kontroll av at skillene er speilet

Dato: 2026-11-06. Branch: `ci-skills-speiling`. Agent: Claude Code (Claude Opus 5.5).
Utført for Johannes W. Gaertner.

Dette er agentens egenrapportering. Et gruppemedlem må lese den gjennom og korrigere.

## Oppgaven

`.agents/skills` (Codex) og `.claude/skills` (Claude Code) skal ha samme innhold.
Kravet sto bare som en skriftlig regel i AGENTS.md, og ingenting fanget opp avvik.
Ønsket var en kontroll som er enkel, automatisk og ikke bruker ressurser ved senere
arbeid. I samme økt ba brukeren om en vurdering av AV-08, og senere om en ny regel
for branch og PR. Begge er tekstendringer, ikke kode, og er beskrevet i §11 i
`docs/beslutninger/avklaringspunkter.md`.

## Prompten

Johannes W. Gaertner, ordrett, i rekkefølge:

> Har det oppstått forskjeller mellom .agents og .claude? Er mekanismen for å ivareta at begge disse oppdateres likt ved utvikling av repoet fortsatt intakt?

> Hvordan vi testen foregå? vil dette spise av ressursene ved fremtidig arbeid? Hensikt: gjør det enkelt, og automatisk.

> Det kan være fornuftig å endre AV-08, vurder om det er hensiktsmessig. Deretter iverksetter vi implementeringen

## Hva modellen leverte

- `scripts/test_skills_speiling.py` har tre `unittest`-tester og bruker bare standardbiblioteket.
  - Begge mappene har de samme sporede filene (`git ls-files`).
  - Innholdet er likt, med CRLF ignorert. Filene i `POINTERS` er unntatt.
  - Unntaket `sesjonslogg/SKILL.md` i `.agents` har samme `name` som Claude-filen og henviser fortsatt til den.
- `.github/workflows/skills-speiling.yml` kjører testen med `python3` på `ubuntu-latest` ved hver push. Den har bare lesetilgang (`contents: read`).
- AGENTS.md:
  - TODO-en om CI er erstattet med en beskrivelse av hva CI kjører.
  - Det utdaterte tallet «214» er fjernet.
  - Speilingsregelen viser til testen og til `POINTERS`.

## Hva som ble rettet, og hvorfor

Ingenting i koden måtte rettes etter første kjøring. Noen valg ble tatt underveis, før koden ble skrevet:

- **Sporede filer i stedet for filsystemet.** Den første prototypen brukte `rglob` og ville tatt med lokale filer som `__pycache__` og `.DS_Store`. Gruppa har både Windows og macOS, så det ville gitt feil som ikke er reelle. `git ls-files` tar bare med det som faktisk deles.
- **Bare `push`, ikke `push` og `pull_request`.** For en branch i samme repo ville begge ha kjørt for samme commit. PR-en viser resultatet fra push-kjøringen uansett.
- **Ingen `setup-python`.** Testen trenger bare standardbiblioteket, og `ubuntu-latest` har Python 3. Det gir ett steg og én avhengighet mindre.
- **Henvisningen sjekkes for seg.** Unntaket kunne ellers ha endret seg ubemerket, for eksempel ved feil `name` eller en død henvisning.

## Kvalitetssikring

- **Lokalt:** De 3 testene ga OK på 0,12 s, og hele `scripts/` ga 67 tester OK.
- **Feiler når den skal.** Hvert brudd under ble laget midlertidig og fjernet igjen etterpå:
  - Innhold endret bare i `.claude/skills/bmad-help/SKILL.md`: fanget av `test_same_content_except_pointers`.
  - Ny sporet fil bare i `.claude` (`git add -N`): fanget av `test_same_files_in_both_folders`.
  - Henvisningen i `.agents/skills/sesjonslogg/SKILL.md` erstattet: fanget av `test_pointer_keeps_name_and_links_the_claude_skill`.
- **Ressurser:** Testen bruker ingen nettverkskall, modellkall eller tokens. Repoet er offentlig, og for offentlige repoer er GitHub Actions gratis.
- **CI på GitHub:** Ikke kjørt ennå. Pushen ble avvist fordi `gh`-tokenet manglet tilgangen `workflow`. Resultatet føres i PR-en.
- **Ikke testet:** Workflow-filen er ikke validert lokalt. Den blir kontrollert av det første kjøret på GitHub.
