import axios, { AxiosInstance, AxiosError } from "axios";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

// ---- Token storage (in-memory + localStorage on client) ----
export const tokenStore = {
  get access() {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("access_token");
  },
  get refresh() {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("refresh_token");
  },
  set(access: string, refresh: string) {
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);
  },
  clear() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  },
};

// ---- Axios instance ----
const client: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

client.interceptors.request.use((config) => {
  const token = tokenStore.access;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auto-refresh on 401
client.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const original = error.config as any;
    if (error.response?.status === 401 && !original._retry && tokenStore.refresh) {
      original._retry = true;
      try {
        const { data } = await axios.post(
          `${API_URL}/auth/refresh`,
          {},
          { headers: { Authorization: `Bearer ${tokenStore.refresh}` } }
        );
        tokenStore.set(data.access_token, data.refresh_token);
        original.headers.Authorization = `Bearer ${data.access_token}`;
        return client(original);
      } catch {
        tokenStore.clear();
        if (typeof window !== "undefined") window.location.href = "/auth/login";
      }
    }
    return Promise.reject(error);
  }
);

// ---- Types ----
export interface Tender {
  id: string;
  file_name: string;
  status: "pending" | "processing" | "completed" | "failed";
  created_at: string;
}

export interface TenderScore {
  win_probability: number;
  eligibility_score: number;
  fit_score: number;
  risk_level: string;
  competition_intensity: string;
  recommendation: string;
  reasoning: string[];
}

export interface TenderAnalysis {
  tender_id: string;
  summary: string | null;
  tender_value: number | null;
  bid_deadline: string | null;
  sector: string | null;
  location: string | null;
  eligibility_criteria: Record<string, unknown>;
  required_documents: string[];
}

export interface QAResponse {
  answer: string;
  sources: Array<{ page: number; preview: string; score: number }>;
  confidence: number;
}

// ---- API methods ----
export const api = {
  // Auth
  register: (email: string, password: string, organization_name: string) =>
    client.post("/auth/register", { email, password, organization_name }),
  login: (email: string, password: string) =>
    client.post("/auth/login", { email, password }),
  me: () => client.get("/auth/me"),

  // Tenders
  uploadTender: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return client.post("/tenders/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  listTenders: () => client.get<Tender[]>("/tenders"),
  getTender: (id: string) => client.get<Tender>(`/tenders/${id}`),
  getTenderStatus: (id: string) => client.get(`/tenders/${id}/status`),
  getAnalysis: (id: string) => client.get<TenderAnalysis>(`/tenders/${id}/analysis`),
  askTender: (id: string, question: string) =>
    client.post<QAResponse>(`/tenders/${id}/ask`, { question, top_k: 5 }),
  deleteTender: (id: string) => client.delete(`/tenders/${id}`),

  // Scoring
  computeScore: (id: string) => client.post<TenderScore>(`/tenders/${id}/score`),
  getScore: (id: string) => client.get<TenderScore>(`/tenders/${id}/score`),

  // Company
  getProfile: () => client.get("/company/profile"),
  saveProfile: (data: Record<string, unknown>) =>
    client.post("/company/profile", data),

  // Billing
  getUsage: () => client.get("/billing/usage"),
  subscribe: (tier: string) => client.post(`/billing/subscribe?tier=${tier}`),

  // Jobs
  getJobStatus: (jobId: string) => client.get(`/jobs/${jobId}/status`),
};

export default client;
