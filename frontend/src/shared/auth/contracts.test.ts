import { ApiContractError } from "@/shared/api/contracts";
import { parseAccessTokenResponse, parseAuthenticatedUser } from "@/shared/auth/contracts";

describe("auth contracts", () => {
  it("parses authenticated user payload", () => {
    expect(
      parseAuthenticatedUser({
        id: 1,
        email: "admin",
        first_name: "Test",
        middle_name: null,
        last_name: "User",
        display_name: "Test User",
        firm_name: "Test Legal",
        disabled: false,
        permissions: ["users:manage"],
      }),
    ).toEqual({
      id: 1,
      email: "admin",
      first_name: "Test",
      middle_name: null,
      last_name: "User",
      display_name: "Test User",
      firm_name: "Test Legal",
      disabled: false,
      permissions: ["users:manage"],
    });
  });

  it("rejects invalid authenticated user payload", () => {
    expect(() =>
      parseAuthenticatedUser({
        id: "1",
        email: "admin",
        first_name: "Test",
        middle_name: null,
        last_name: "User",
        display_name: "Test User",
        firm_name: "Test Legal",
        disabled: false,
        permissions: ["users:manage"],
      }),
    ).toThrow(ApiContractError);
  });

  it("rejects authenticated user payload when permissions are missing", () => {
    expect(() =>
      parseAuthenticatedUser({
        id: 1,
        email: "admin",
        first_name: "Test",
        middle_name: null,
        last_name: "User",
        display_name: "Test User",
        firm_name: "Test Legal",
        disabled: false,
      }),
    ).toThrow(ApiContractError);
  });

  it("parses access token payload", () => {
    expect(
      parseAccessTokenResponse({
        access_token: "token",
        token_type: "bearer",
      }),
    ).toEqual({
      access_token: "token",
      token_type: "bearer",
    });
  });

  it("rejects invalid token type", () => {
    expect(() =>
      parseAccessTokenResponse({
        access_token: "token",
        token_type: "Bearer",
      }),
    ).toThrow(ApiContractError);
  });
});
