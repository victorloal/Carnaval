import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// Vitest runs without `globals: true`, so React Testing Library cannot register
// its own auto-cleanup. Without this, a second `render` in a file leaves the
// first tree mounted and `getBy*` matches duplicates.
afterEach(() => {
  cleanup();
});
