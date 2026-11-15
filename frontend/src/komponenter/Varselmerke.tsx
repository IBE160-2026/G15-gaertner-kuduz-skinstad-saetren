import type { ReactNode } from "react";

/** Synlig indikator for en aktiv belastning eller overtidskostnad. */
export default function Varselmerke({ children }: { children: ReactNode }) {
  return <span className="varselmerke">
    <svg className="varselmerke-ikon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M12 3 2 21h20L12 3Z" fill="none" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" />
      <path d="M12 9v5m0 3v.1" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
    <span>{children}</span>
  </span>;
}
