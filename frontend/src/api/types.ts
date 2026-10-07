export interface Edition {
  id: string;
  year: number;
  slug_es: string;
  slug_en: string;
  title_es: string;
  title_en: string;
  starts_on: string | null;
  ends_on: string | null;
  summary_es: string;
  summary_en: string;
}

export interface Day {
  id: string;
  edition: string;
  date: string;
  slug_es: string;
  slug_en: string;
  label_es: string;
  label_en: string;
}

export interface Venue {
  id: string;
  name_es: string;
  name_en: string;
  address: string;
  city: string;
  latitude: string | null;
  longitude: string | null;
  capacity: number | null;
}

export interface Event {
  id: string;
  day: string;
  venue: string | null;
  starts_at: string | null;
  ends_at: string | null;
  title_es: string;
  title_en: string;
  description_es: string;
  description_en: string;
  sort_order: number;
  source_url: string;
}

export interface MediaAsset {
  id: string;
  edition: string | null;
  title_es: string;
  title_en: string;
  description_es: string;
  description_en: string;
  year_approx: number | null;
  author: string;
  source_ref: string;
  license: string;
  citation_text: string;
  featured: boolean;
}

export interface NewsItem {
  id: string;
  headline: string;
  url: string;
  outlet: string;
  published_on: string | null;
  summary_es: string;
  summary_en: string;
}

export interface SearchEvent {
  id: string;
  title_es: string;
  title_en: string;
}

export interface SearchNews {
  id: string;
  headline: string;
}

export interface SearchResponse {
  query: string;
  events: SearchEvent[];
  news: SearchNews[];
}

export type SubmissionKind = "image" | "video_link";

export interface SubmissionCreated {
  token: string;
  status: string;
}

export interface SubmissionStatus {
  status: string;
  rejection_reason: string;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
