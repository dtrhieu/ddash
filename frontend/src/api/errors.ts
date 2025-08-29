export type ApiProblem = {
  detail?: string;
  error?: string;
  code?: string | number;
  fields?: Record<string, string[] | string>;
  [key: string]: unknown;
};

export class HTTPError extends Error {
  status: number;
  statusText: string;
  url: string;
  problem?: ApiProblem;

  constructor(params: { message?: string; status: number; statusText: string; url: string; problem?: ApiProblem }) {
    const { message, status, statusText, url, problem } = params;
    super(message || HTTPError.defaultMessage(status, problem));
    this.name = "HTTPError";
    this.status = status;
    this.statusText = statusText;
    this.url = url;
    this.problem = problem;
  }

  static defaultMessage(status: number, problem?: ApiProblem) {
    const base = `Request failed with status ${status}`;
    const detail = problem?.detail || problem?.error;
    return detail ? `${base}: ${detail}` : base;
  }
}
