import { createContext, useState, type ReactNode } from "react";
import { hentAvveining, type Avveiningssvar } from "./api";
import { gyldigAvveining } from "./kandidater";

export type Panelresultat = Extract<Avveiningssvar, { status: "ok" }> | "reserve";

async function lastKontrollert(vakt: number, id: number, merke: string): Promise<Panelresultat | null> {
  try {
    const svar = await hentAvveining(vakt, id);
    if (gyldigAvveining(svar, vakt, id, merke)) return svar;
    if (svar?.status === "avveining_feilet" && svar.vaktnummer === vakt &&
        svar.kandidat_id === id && svar.grunnlagsmerke === merke) return "reserve";
    return null;
  } catch {
    return null;
  }
}

export const Avveiningsoppslag = createContext(lastKontrollert);

// App monterer denne på nytt for hver vakt og sesjon. Begge flatene får
// samme løfte også når brukeren velger kandidaten før svaret kommer.
export function AvveiningerForVakt({ children }: { children: ReactNode }) {
  const [oppslag] = useState(() => {
    const forespørsler = new Map<string, ReturnType<typeof lastKontrollert>>();
    return (vakt: number, id: number, merke: string) => {
      const nøkkel = `${vakt}/${id}/${merke}`;
      const eksisterende = forespørsler.get(nøkkel);
      if (eksisterende) return eksisterende;
      const forespørsel = lastKontrollert(vakt, id, merke).then(resultat => {
        if (resultat === null) forespørsler.delete(nøkkel);
        return resultat;
      });
      forespørsler.set(nøkkel, forespørsel);
      return forespørsel;
    };
  });
  return <Avveiningsoppslag.Provider value={oppslag}>{children}</Avveiningsoppslag.Provider>;
}
