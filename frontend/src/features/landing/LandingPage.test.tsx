import { QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { RouterProvider, createMemoryRouter } from "react-router-dom";

import { createQueryClient } from "@/app/query-client";
import { SESSION_QUERY_KEY } from "@/shared/auth/session";
import { t } from "@/shared/i18n/ui-text";
import { LandingPage } from "@/features/landing/LandingPage";

describe("LandingPage", () => {
  it("renders the public product landing with BYOK and legal messaging", () => {
    const queryClient = createQueryClient();
    queryClient.setQueryData(SESSION_QUERY_KEY, null);
    const router = createMemoryRouter(
      [
        {
          path: "/",
          element: <LandingPage />,
        },
      ],
      { initialEntries: ["/"] }
    );

    render(
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>
    );

    expect(screen.getByRole("heading", { name: t("landing.title") })).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: t("landing.cta.login") })[0]).toHaveAttribute(
      "href",
      "/login",
    );
    expect(screen.getAllByRole("link", { name: t("landing.cta.register") })[0]).toHaveAttribute(
      "href",
      "/register",
    );
    expect(screen.getByText(t("landing.byok.title"))).toBeInTheDocument();
    expect(screen.getByText(t("landing.legal.title"))).toBeInTheDocument();
    expect(screen.getByText(t("landing.legal.body"))).toBeVisible();
    expect(screen.getByRole("heading", { name: t("landing.modules.title") })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: t("landing.modules.clients.title") })).toBeInTheDocument();
    expect(screen.getByLabelText(t("landing.preview.label"))).toBeInTheDocument();
  });
});
