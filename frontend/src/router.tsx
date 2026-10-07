import { createBrowserRouter, Navigate } from "react-router-dom";

import { App } from "./App";
import { GalleryPage } from "./pages/GalleryPage";
import { NewsPage } from "./pages/NewsPage";
import { ProgrammePage } from "./pages/ProgrammePage";
import { SearchPage } from "./pages/SearchPage";
import { redirectTarget } from "./lib/locale";

/** The unprefixed root redirects to the negotiated locale (FR-H-04). */
function RootRedirect() {
  return (
    <Navigate to={redirectTarget(window.location.pathname, document.cookie)} replace />
  );
}

export const router = createBrowserRouter([
  { path: "/", element: <RootRedirect /> },
  {
    path: "/:locale",
    element: <App />,
    children: [
      { index: true, element: <ProgrammePage /> },
      { path: "news", element: <NewsPage /> },
      { path: "gallery", element: <GalleryPage /> },
      { path: "search", element: <SearchPage /> },
    ],
  },
]);
