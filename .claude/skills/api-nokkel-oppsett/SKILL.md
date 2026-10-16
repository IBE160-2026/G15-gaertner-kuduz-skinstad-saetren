---
name: api-nokkel-oppsett
description: 'Gir et gruppemedlem tilgang til live-kall mot GPT-6 Luna via OpenRouter: oppretter .env, forklarer hvor nøkkelen ligger og hva som ikke er lov. Use when a group member asks how to add the API key, set up .env, get access to OpenRouter or run live calls against Luna, or gets "Mangler gyldig format på OPENROUTER_API_KEY".'
---

# Oppsett av OpenRouter-nøkkel for live Luna-kall

Formålet er at alle i gruppa får samme instruks, slik at det ikke oppstår
misforståelser. Følg stegene i rekkefølge og gjengi instruksen i steg 4 uten å
forkorte bort forbudene.

## Harde regler for deg som agent

- **Les aldri `.env`.** Ikke `cat`, `Read`, `type`, `Get-Content` eller lignende på
  filen, og ikke skriv ut `OPENROUTER_API_KEY` fra miljøet. Nøkkelen skal aldri inn
  i konteksten din.
- **Skriv aldri nøkkelen selv.** Medlemmet limer den inn i editoren. Du lager bare
  filen med tomt nøkkelfelt.
- **Overskriv aldri en eksisterende `.env`.**
- Limer medlemmet likevel inn noe som ligner en nøkkel (`sk-or-…`) i chatten: ikke
  gjenta den, ikke bruk den, og følg «Hvis nøkkelen lekker» under.

## Steg 1: Sjekk om `.env` finnes

Fra repo-roten: `test -f .env && echo finnes || echo mangler`
(PowerShell: `Test-Path .env`).

Finnes den, sjekk bare modell-linjen, som ikke er hemmelig:
`grep '^OPENROUTER_MODEL' .env`. Er den tom eller mangler, be medlemmet selv sette
`OPENROUTER_MODEL=openai/gpt-6-luna` i filen.

## Steg 2: Opprett `.env` hvis den mangler

Kopier eksempelfilen og sett modellen. Nøkkelfeltet forblir tomt:

```bash
cp .env.example .env
sed -i 's|^OPENROUTER_MODEL=$|OPENROUTER_MODEL=openai/gpt-6-luna|' .env
```

`.env` inneholder ingen kode, bare to variabler. Koden som kobler opp mot
OpenRouter ligger i `scripts/modelltest_openrouter.py` (`configuration()`). Modellen
må settes eksplisitt, fordi det skriptet ellers faller tilbake til Haiku.
`modelltest_robusthet.py` og `modelltest_prd_fasit.py` bruker Luna uansett.

## Steg 3: Bekreft at `.env` holdes utenfor Git

```bash
git check-ignore -v .env              # skal vise .gitignore-regelen
git ls-files --error-unmatch .env     # skal feile: filen er ikke sporet
```

Gir den første ingen treff, eller den andre ikke feiler: stopp og si fra til
medlemmet og Johannes før nøkkelen legges inn.

## Steg 4: Gi medlemmet instruksen

Gjengi dette, tilpasset om `.env` ble opprettet nå eller fantes fra før:

> **Slik legger du inn nøkkelen**
>
> 1. Nøkkelen ligger pinnet i **Teams-gruppechatten for Turnushjelperen**. Kopier
>    den derfra.
> 2. Åpne `.env` i roten av repoet i editoren din. Lim nøkkelen inn rett etter
>    `OPENROUTER_API_KEY=`, uten mellomrom og uten anførselstegn. Den skal starte
>    med `sk-or-`. Lagre filen.
> 3. Linjen `OPENROUTER_MODEL=openai/gpt-6-luna` skal stå som den er.
> 4. Si fra her når du har lagret, så sjekker jeg at oppsettet virker uten å se
>    nøkkelen.
>
> **Ikke gjør dette**
>
> - **Ikke lim nøkkelen inn i Claude, Codex eller noen annen KI-chat**, heller ikke
>   for å «få hjelp med feilen». Gruppa logger prompter i `docs/ki-logg/`, som
>   committes, så en nøkkel i en KI-chat kan havne i repoet den veien. Regelen står
>   i `docs/modelltest-openrouter.md`: nøkkelen skal ikke i chatten, Git eller
>   dokumentasjonen.
> - **Ikke legg nøkkelen i kode, dokumentasjon, KI-loggen, commit-meldinger,
>   issues eller PR-er**, og ikke del den andre steder enn Teams-gruppechatten.
> - **Ikke commit `.env`.** Den er gitignorert, men `git add -f` eller å endre
>   `.gitignore` overstyrer det. Sensorveiledningen teller API-nøkler eller
>   `.env`-filer i repoet eller historikken som et kjennetegn på svak besvarelse
>   (`docs/emne/sensorveiledning-del-1.md`, kriterium 7 «Ryddighet i repoet»).
>
> **Greit å vite**
>
> - Live-kall koster penger på Johannes' OpenRouter-konto. Kjør tørrkjøring
>   (uten `--live`) først, og les `docs/modelltest-openrouter.md` før live.
> - Kontoen tåler 20 Luna-kall per minutt. Kjør aldri to live-tester samtidig,
>   heller ikke på tvers av gruppemedlemmer. Avtal i Teams hvis flere skal kjøre.
> - Har du en `OPENROUTER_API_KEY` satt som miljøvariabel på maskinen, har den
>   forrang over `.env`. Fjern den hvis riktig nøkkel ikke blir brukt.

## Steg 5: Verifiser uten å se nøkkelen

Når medlemmet sier at nøkkelen er lagt inn, kjør fra repo-roten:

```bash
python -c "import sys; sys.path.insert(0, 'scripts'); import modelltest_openrouter as m; _, model = m.configuration(); print('OK: OPENROUTER_API_KEY har riktig format. Modell:', model)"
```

Utskriften inneholder aldri nøkkelen. Forventet: `OK: … Modell: openai/gpt-6-luna`.
Feilmeldingen «Mangler gyldig format på OPENROUTER_API_KEY» betyr tomt felt, feil
prefiks eller en miljøvariabel som overstyrer. Gå tilbake til steg 4, punkt 2.
Sjekken bekrefter formatet, ikke at nøkkelen er gyldig hos OpenRouter. Det viser
første live-kjøring.

## Hvis nøkkelen lekker

Gjelder om den er limt inn i en KI-chat, committet, pushet eller delt utenfor
Teams-gruppechatten:

1. Si fra til **Johannes**, som eier OpenRouter-kontoen, med en gang. Han trekker
   nøkkelen tilbake og legger en ny pinnet i Teams-gruppechatten.
2. Er den committet, holder det ikke å slette den i en ny commit. Den ligger
   fortsatt i historikken, så nøkkelen må byttes uansett.
3. Ikke prøv å skjule lekkasjen. Ved innlevering er en håndtert lekkasje bedre enn
   en uhåndtert («ekte hemmeligheter som ikke er håndtert» er F-nivå for
   kriterium 7).
