import type { Innlogget } from "../api";
import { TEKSTER } from "../tekster";

type Props = {
  // `undefined` mens appen ikke vet om noen er innlogget, `null` når ingen er det.
  bruker: Innlogget | null | undefined;
};

export default function Appbar({ bruker }: Props) {
  return (
    <header className="appbar">
      <span className="appbar-brand">{TEKSTER.merkevare}</span>
      <span className="appbar-hoyre">
        {bruker === undefined
          ? null
          : bruker === null
            ? TEKSTER.ikkeInnlogget
            : TEKSTER.innlogget(bruker.navn, bruker.avdeling)}
      </span>
    </header>
  );
}
