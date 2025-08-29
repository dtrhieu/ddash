import { HTTPError, ApiProblem } from "./errors";

export type ClientOptions = {
  baseUrl?: string;
  headers?: Record<string, string>;
  credentials?: RequestCredentials;
};

const DEFAULT_BASE = import.meta.env.VITE_API_BASE || "/api";

export class ApiClient {
  baseUrl: string;
  defaultHeaders: Record<string, string>;
  credentials: RequestCredentials | undefined;

  constructor(opts: ClientOptions = {}) {
    this.baseUrl = (opts.baseUrl || DEFAULT_BASE).replace(/\/$/, "");
    this.defaultHeaders = {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...opts.headers,
    };
    this.credentials = opts.credentials;
  }

  private buildUrl(path: string) {
    if (path.startsWith("http")) return path;
    const p = path.startsWith("/") ? path : `/${path}`;
    return `${this.baseUrl}${p}`;
  }

  async request<T>(path: string, init: RequestInit = {}): Promise<T> {
    const url = this.buildUrl(path);
    const res = await fetch(url, {
      ...init,
      headers: {
        ...this.defaultHeaders,
        ...(init.headers || {}),
      },
      credentials: this.credentials ?? init.credentials,
    });

    const contentType = res.headers.get("content-type") || "";
    const isJson = contentType.includes("application/json");
    let data: unknown = null;
    try {
      data = isJson ? await res.json() : await res.text();
    } catch {
      data = null;
    }

    if (!res.ok) {
      const problem: ApiProblem | undefined = isJson && data && typeof data === "object" ? data as ApiProblem : undefined;
      throw new HTTPError({
        status: res.status,
        statusText: res.statusText,
        url,
        problem,
      });
    }

    return data as T;
  }

  get<T>(path: string, init?: RequestInit) {
    return this.request<T>(path, { ...init, method: "GET" });
  }
  post<T>(path: string, body?: unknown, init?: RequestInit) {
    return this.request<T>(path, { ...init, method: "POST", body: body !== undefined ? JSON.stringify(body) : undefined });
  }
  put<T>(path: string, body?: unknown, init?: RequestInit) {
    return this.request<T>(path, { ...init, method: "PUT", body: body !== undefined ? JSON.stringify(body) : undefined });
  }
  patch<T>(path: string, body?: unknown, init?: RequestInit) {
    return this.request<T>(path, { ...init, method: "PATCH", body: body !== undefined ? JSON.stringify(body) : undefined });
  }
  delete<T>(path: string, init?: RequestInit) {
    return this.request<T>(path, { ...init, method: "DELETE" });
  }
}

// Singleton default client for convenience
export const api = new ApiClient();
