import axios from "axios";

const api = axios.create({
  baseURL: "http://13.49.74.167:8000/api",
});

// ── Request interceptor: attach JWT from localStorage ──────────────────────────
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("khetiq_token");
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ── Response interceptor: on 401 clear session and go to landing ───────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.clear();
      window.location.href = "/";
    }
    return Promise.reject(error);
  }
);

export default api;
