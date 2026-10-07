import { createBrowserRouter, Navigate } from "react-router-dom";

import { App } from "./App";
import { redirectTarget } from "./lib/locale";

/** The unprefixed root redirects to the negotiated locale (FR-H-04). */
function RootRedirect() {
  return (
    <Navigate to={redirectTarget(window.location.pathname, document.cookie)} replace />
  );
}

export const router = createBrowserRouter([
  { path: "/", element: <RootRedirect /> },
  { path: "/:locale", element: <App /> },
]);
