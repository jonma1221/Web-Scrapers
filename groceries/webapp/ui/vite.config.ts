import { defineConfig } from "vite";

export default defineConfig({
  server: {
    proxy: {
      // "/api": "https://web-scrapers-docker.onrender.com/",
      "/api": "http://localhost:8000",
    },
  },
  build: {
    outDir: "dist",
  },
});
