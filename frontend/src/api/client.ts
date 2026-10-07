import type { Paginated } from "./types";

const API_BASE: string = import.meta.env.VITE_API_BASE ?? "/api";

export async function getJson<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    signal,
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}`);
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
