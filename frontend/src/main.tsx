import "@/app/styles.css";

import { QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

import { createQueryClient } from "@/app/query-client";
import { appRoutes } from "@/app/routes";
import { readFrontendEnvConfig } from "@/shared/api/env";
import { installGlobalRuntimeErrorHandlers } from "@/shared/observability/runtime-errors";

readFrontendEnvConfig();
installGlobalRuntimeErrorHandlers();

const router = createBrowserRouter(appRoutes);
const queryClient = createQueryClient();

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </StrictMode>,
);
