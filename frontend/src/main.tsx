import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./stil/tokens.css";
import "./stil/app.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
