import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// Le proxy renvoie les appels /api vers le backend FastAPI en développement,
// évitant tout problème de CORS et gardant une seule origine côté navigateur.
export default defineConfig({
  plugins: [react()],
  resolve: { alias: { "@": path.resolve(__dirname, "src") } },
  server: {
    port: 5173,
    proxy: {
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true },
    },
  },
});
