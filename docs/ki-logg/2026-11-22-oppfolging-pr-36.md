# Oppfølging av lekkasjetesten i PR #36

## Oppgave og prompt

Kim ba Codex (GPT-6) følge opp tre funn fra gjennomgangen av story 5.6. «Gjør disse endringene etter dine anbefallinger og kjør tester på nytt før vi eventuelt godkjenner». En ekstra modellmelding, en endret preferansetekst og en nestet kandidat-ID i et detaljsvar hadde alle gått gjennom kontrollene. [Gjennomgang av PR #36](../../.logs/kimsk81/963-2026-11-22-00-11-29-gjennomgang-pr-36.md) · [Opprinnelig KI-logg](2026-11-21-lekkasjeinvariant.md)

## Hva ble prøvd

En implementeringsagent fikk i oppdrag å lage negative kontroller for de tre funnene og først kjøre dem mot de gamle kontrollene. Den prøvde også lovlig preferansetekst som inneholder ordet «kandidat», og manglende eller ekstra forekomster når flere ansatte har lik preferansetekst.

I første kjøring feilet 26 av 27 nye tilfeller. I 25 tilfeller godtok kontrollen et avvik. I ett tilfelle avviste den en korrekt gjengitt preferansetekst. Det eneste tilfellet som allerede bestod, var at en endret systemtekst for preferansetolkning ble avvist. Utgangspunktet var `e59adf4` for testmodulen, med `main` innlemmet før den endelige verifiseringen.

## Hva ble rettet

- Testen kontrollerer de to meldingene, rollene, systemteksten, svarskjemaet og tillatte felt i forespørselen. For forklaringen sammenligner den kandidaten og referansen med de registrerte portkallene, og sjekker feltene i hver tillatte påstand. Fasiten for de utelukkede gir en egen kontroll av kandidat-ID-ene.
- For alle de 19 preferansetekstene sammenligner testen originaltekst og antall forekomster med både portkallene og HTTP-meldingene. I forsøket med ordet «kandidat» følger teksten hele veien fra testdatabasen til transporten.
- Listesvaret utenom Ekskludert-boksen, godkjenningsgrunnlaget og avveiningssvaret undersøkes rekursivt for `id`, `kandidat_id` og `referanse_id`. ID-ene skal være heltall. Live-forklaringens tekst sjekkes mot de tillatte påstandene for kandidatparet, slik at poengsummer fortsatt kan inneholde de samme sifrene som en utelukket ID.

Etter første retting bestod de 27 tilfellene. En uavhengig gjennomgang etterprøvde også ID som tekst i et strukturert felt, ekstra opplysninger i svarskjemaet og en eksplisitt ID i en forklaringssetning. Disse tilfellene fikk egne regresjonstester. Den endelige gruppen på 38 nye testtilfeller bestod på Windows. De isolerte endringene av meldinger og svar bruker egne kopier fra én registrert API-flyt. [Testmodulen](../../backend/tester/api/test_lekkasjeinvariant.py)

## Sluttkontroll

Fra `backend/` bestod `.venv\Scripts\python.exe -m pytest -q` med 792 av 792 tester på Windows, inkludert de 59 i lekkasjemodulen og import-linter-kontrakten. To gjennomgangsagenter kontrollerte sluttversjonen. Én kjørte flyten for #4127 mot en egen minnedatabase og bekreftet at ID 11 ble avvist i en ekstra modellmelding, i endret preferansetekst og i hvert av de to detaljsvarene ved separate forsøk. Testene brukte falsk transport.
