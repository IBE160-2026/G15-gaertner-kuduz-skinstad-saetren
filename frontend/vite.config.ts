import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Proxyen gir samme opphav for frontend og API, så sesjonscookien kan ha
// SameSite=Strict og det trengs ingen CORS (OP-10, story 1.3).
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },
});
