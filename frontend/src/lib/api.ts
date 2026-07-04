import axios from "axios";

const TOKEN_KEY = "aegis_token";

export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (t: string) => localStorage.setItem(TOKEN_KEY, t);
export const clearToken = () => localStorage.removeItem(TOKEN_KEY);

export const api = axios.create({ baseURL: "/api/v1" });

// Injecte le jeton JWT sur chaque requête.
api.interceptors.request.use((config) => {
  const t = getToken();
  if (t) config.headers.Authorization = `Bearer ${t}`;
  return config;
});

// Sur 401, on purge le jeton et on renvoie vers la connexion.
api.interceptors.response.use(
  (r) => r,
  (error) => {
    if (error?.response?.status === 401 && !location.pathname.startsWith("/login")) {
      clearToken();
      location.href = "/login";
    }
    return Promise.reject(error);
  }
);
