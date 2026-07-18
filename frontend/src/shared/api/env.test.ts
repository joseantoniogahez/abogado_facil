import {
  buildApiUrl,
  FrontendEnvError,
  getApiBaseUrl,
  readFrontendEnvConfig,
} from "@/shared/api/env";

describe("frontend env contracts", () => {
  it("normalizes valid API origin/base path values", () => {
    const config = readFrontendEnvConfig({
      VITE_API_ORIGIN: "https://api.example.com/",
      VITE_API_BASE_PATH: "v1/",
    });

    expect(config.apiOrigin).toBe("https://api.example.com");
    expect(config.apiBasePath).toBe("/v1");
    expect(
      getApiBaseUrl({ VITE_API_ORIGIN: "https://api.example.com/", VITE_API_BASE_PATH: "/v1/" }),
    ).toBe("https://api.example.com/v1");
  });

  it("fails fast for invalid API origin", () => {
    expect(() =>
      readFrontendEnvConfig({
        VITE_API_ORIGIN: "not-a-url",
        VITE_API_BASE_PATH: "/v1",
      }),
    ).toThrow(FrontendEnvError);
  });

  it("fails fast for invalid base path format", () => {
    expect(() =>
      readFrontendEnvConfig({
        VITE_API_ORIGIN: "https://api.example.com",
        VITE_API_BASE_PATH: "/bad path",
      }),
    ).toThrow(FrontendEnvError);
  });

  it("builds API URL from validated runtime config", () => {
    expect(
      buildApiUrl("/users/me", {
        VITE_API_ORIGIN: "https://api.example.com/",
        VITE_API_BASE_PATH: "/v1/",
      }),
    ).toBe("https://api.example.com/v1/users/me");
  });

  it("uses defaults and normalizes an empty base path", () => {
    expect(readFrontendEnvConfig({})).toEqual({
      apiOrigin: "http://localhost:8000",
      apiBasePath: "/v1",
    });
    expect(getApiBaseUrl({ VITE_API_ORIGIN: "https://api.example.com", VITE_API_BASE_PATH: " / " }))
      .toBe("https://api.example.com");
    expect(buildApiUrl("/users/me", { VITE_API_ORIGIN: "https://api.example.com", VITE_API_BASE_PATH: "/" }))
      .toBe("https://api.example.com/users/me");
  });

  it("rejects non-string, empty and unsupported origin values", () => {
    expect(() => readFrontendEnvConfig({ VITE_API_ORIGIN: 42 })).toThrow("must be a string");
    expect(() => readFrontendEnvConfig({ VITE_API_BASE_PATH: "   " })).toThrow("must not be empty");
    expect(() => readFrontendEnvConfig({ VITE_API_ORIGIN: "ftp://api.example.com" }))
      .toThrow("must use http/https protocol");
  });
});
