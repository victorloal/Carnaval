import type {
  Paginated,
  SearchResponse,
  SubmissionCreated,
  SubmissionStatus,
} from "./types";

const API_BASE: string = import.meta.env.VITE_API_BASE ?? "/api";

/** An error carrying the status and the server's own `detail`, when it has one. */
export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function errorDetail(response: Response): Promise<string> {
  try {
    const body: unknown = await response.json();
    if (
      body &&
      typeof body === "object" &&
      "detail" in body &&
      typeof (body as { detail: unknown }).detail === "string"
    ) {
      return (body as { detail: string }).detail;
    }
  } catch {
    // A non-JSON error body is not worth surfacing.
  }
  return `API request failed with status ${response.status}`;
}

export async function getJson<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    signal,
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new ApiError(response.status, await errorDetail(response));
  }
  return (await response.json()) as T;
}

export async function getAllPages<T>(
  path: string,
  signal?: AbortSignal,
): Promise<T[]> {
  const page = await getJson<Paginated<T>>(path, signal);
  return page.results;
}

/** Full-text search over published events and news (FR-I-01). */
export async function search(
  query: string,
  signal?: AbortSignal,
): Promise<SearchResponse> {
  return getJson<SearchResponse>(
    `/search/?q=${encodeURIComponent(query)}`,
    signal,
  );
}

/** Submit an image or a video link; the response is the status token (FR-F-01/02). */
export async function submitSubmission(
  data: FormData,
  signal?: AbortSignal,
): Promise<SubmissionCreated> {
  const response = await fetch(`${API_BASE}/submissions/`, {
    method: "POST",
    body: data,
    signal,
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new ApiError(response.status, await errorDetail(response));
  }
  return (await response.json()) as SubmissionCreated;
}

/** Look up a submission by its unguessable token (FR-F-18). */
export async function getSubmissionStatus(
  token: string,
  signal?: AbortSignal,
): Promise<SubmissionStatus> {
  return getJson<SubmissionStatus>(
    `/submissions/${encodeURIComponent(token)}/`,
    signal,
  );
}
