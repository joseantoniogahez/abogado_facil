import { useQuery } from "@tanstack/react-query";

import { sessionQueryPolicy } from "@/app/query-policy";
import { isUnauthorizedError } from "@/shared/api/errors";
import { apiRequest } from "@/shared/api/http";
import {
  parseAccessTokenResponse,
  parseAuthenticatedUser,
  type AccessTokenResponse,
  type AuthenticatedUser,
} from "@/shared/auth/contracts";
import { clearAccessToken, getAccessToken, setAccessToken } from "@/shared/auth/storage";

interface Credentials {
  email: string;
  password: string;
}

export interface RegisterUserInput {
  first_name: string;
  middle_name?: string;
  last_name: string;
  display_name: string;
  email: string;
  firm_name?: string;
  password: string;
}

export interface UpdateCurrentUserInput {
  first_name?: string;
  middle_name?: string;
  last_name?: string;
  display_name?: string;
  email?: string;
  firm_name?: string;
  current_password?: string;
  new_password?: string;
}

export type { AuthenticatedUser };

export const SESSION_QUERY_KEY = ["auth", "session"] as const;
export const TOKEN_ENDPOINT_PATH = "/token";
export const REGISTER_USER_ENDPOINT_PATH = "/users/register";
export const CURRENT_USER_ENDPOINT_PATH = "/users/me";

export const readCurrentUser = (): Promise<AuthenticatedUser> =>
  apiRequest<AuthenticatedUser>(CURRENT_USER_ENDPOINT_PATH, {
    parse: parseAuthenticatedUser,
  });

export const registerUser = (payload: RegisterUserInput): Promise<AuthenticatedUser> =>
  apiRequest<AuthenticatedUser>(REGISTER_USER_ENDPOINT_PATH, {
    method: "POST",
    withAuth: false,
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
    parse: parseAuthenticatedUser,
  });

export const loginWithCredentials = async ({ email, password }: Credentials): Promise<void> => {
  const body = new URLSearchParams({
    username: email,
    password,
  });

  const token = await apiRequest<AccessTokenResponse>(TOKEN_ENDPOINT_PATH, {
    method: "POST",
    body,
    withAuth: false,
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    parse: parseAccessTokenResponse,
  });

  setAccessToken(token.access_token);
};

export const updateCurrentUser = (payload: UpdateCurrentUserInput): Promise<AuthenticatedUser> =>
  apiRequest<AuthenticatedUser>(CURRENT_USER_ENDPOINT_PATH, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
    parse: parseAuthenticatedUser,
  });

export const logout = (): void => {
  clearAccessToken();
};

export const resolveSessionUser = async (): Promise<AuthenticatedUser | null> => {
  if (!getAccessToken()) {
    return null;
  }

  try {
    return await readCurrentUser();
  } catch (error) {
    if (isUnauthorizedError(error)) {
      clearAccessToken();
      return null;
    }
    throw error;
  }
};

export const sessionQueryOptions = () => ({
  queryKey: SESSION_QUERY_KEY,
  queryFn: resolveSessionUser,
  ...sessionQueryPolicy,
});

export const useSession = () => useQuery(sessionQueryOptions());
