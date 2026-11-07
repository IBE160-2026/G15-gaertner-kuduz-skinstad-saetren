# Til sensor: innlogging (utkast)

> **Status:** utkast 2026-11-07, skrevet av Claude Code for Johannes W. Gaertner. Ikke
> godkjent av gruppa. Teksten er ment for innleveringen, ved siden av README, og bør
> leses mot README rett før fristen. Lenkene peker til avsnitt i README.

---

Turnushjelperen krever innlogging. Det finnes én bruker, turnusansvarlig Kari Vestby,
med brukernavnet **`kari.vestby`**. Brukeren opprettes av testdatakommandoen i
[README, steg 2](../../README.md#2-last-testdata-og-noter-passordet). Det står ikke noe
passord i repoet eller i denne teksten. Du velger det selv:

1. Følg [steg 1 i README](../../README.md#1-installer-backend) for å installere backend.
2. I steg 2 velger du **variant A, personlig passord**. Kommandoen ber deg skrive et
   passord som ikke vises på skjermen. Den siste linjen i utskriften skal være
   `Passord: personlig, fra TURNUSHJELPEREN_PASSORD`.
3. Start backend (steg 3) og frontend i en egen terminal (steg 4). Åpne
   http://localhost:5173 og logg inn som `kari.vestby` med passordet du valgte.

Vil du heller ha et passord laget for deg, bruker du **variant B** i steg 2. Da skrives et
tilfeldig passord på siste linje i utskriften. Det gjelder til kommandoen kjøres neste
gang.

Nyttig å vite:

- **Innloggingskortet viser hvilken variant som gjelder**, men aldri selve passordet:
  «Personlig passord», «Testpassord» eller «Ingen bruker». «Ingen bruker» betyr at steg 2
  ikke er kjørt.
- **Alle logges ut når backend starter på nytt.** Nøkkelen som signerer innloggingen, lages
  ved hver oppstart og lagres ingen steder. Det er et bevisst valg (OP-10 i
  [avklaringspunktene](../beslutninger/avklaringspunkter.md)). Logg inn på nytt med samme
  passord.
- **Stopper `npm` med `UnauthorizedAccess` i PowerShell**, bruk `npm.cmd install` og
  `npm.cmd run dev`, som README-steg 4 beskriver.
- Appen er testet på Windows. Den er skrevet for å virke på macOS og Linux også, og README
  har egne bash-kommandoer for det.
