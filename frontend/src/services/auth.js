import { apiRequest, clearStoredTokens, setStoredTokens } from "./api";

export async function loginUser(email, password) {
  const payload = await apiRequest("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });

  setStoredTokens({
    access_token: payload.access_token,
    refresh_token: payload.refresh_token,
  });

  return payload;
}

export async function registerUser({ name, email, password, secret_key, role }) {
  const payload = await apiRequest("/auth/register", {
    method: "POST",
    body: JSON.stringify({ name, email, password, secret_key, role }),
  });

  return payload;
}

export async function logoutUser() {
  const refreshToken = localStorage.getItem("karya_refresh_token");

  try {
    if (refreshToken) {
      await apiRequest("/auth/logout", {
        method: "POST",
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
    }
  } finally {
    clearStoredTokens();
  }
}

export async function getCurrentUser() {
  return apiRequest("/users/me", { method: "GET" });
}
