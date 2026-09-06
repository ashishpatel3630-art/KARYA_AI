const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const ACCESS_TOKEN_KEY = "karya_access_token";
const REFRESH_TOKEN_KEY = "karya_refresh_token";

function formatApiError(payload, fallback = "Request failed.") {
  const detail = payload?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => item?.msg || item?.message)
      .filter(Boolean)
      .join(" ") || fallback;
  }
  if (detail && typeof detail === "object") {
    return detail.message || detail.msg || fallback;
  }
  return payload?.message || fallback;
}

export function getStoredAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY) || "";
}

export function getStoredRefreshToken() {
  return localStorage.getItem(REFRESH_TOKEN_KEY) || "";
}

export function setStoredTokens({ access_token, refresh_token }) {
  if (access_token) {
    localStorage.setItem(ACCESS_TOKEN_KEY, access_token);
  }
  if (refresh_token) {
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh_token);
  }
}

export function clearStoredTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

async function refreshTokenIfNeeded() {
  const refreshToken = getStoredRefreshToken();
  if (!refreshToken) {
    return false;
  }

  try {
    const response = await fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      clearStoredTokens();
      return false;
    }

    const payload = await response.json();
    setStoredTokens({
      access_token: payload.access_token,
      refresh_token: payload.refresh_token,
    });

    return true;
  } catch {
    clearStoredTokens();
    return false;
  }
}

export async function apiRequest(path, options = {}) {
  const requestOptions = { ...options };
  const headers = {
    Accept: "application/json",
    ...(requestOptions.headers || {}),
  };

  const accessToken = getStoredAccessToken();
  if (accessToken && !(requestOptions.body instanceof FormData)) {
    headers.Authorization = `Bearer ${accessToken}`;
  }

  if (!(requestOptions.body instanceof FormData) && requestOptions.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  requestOptions.headers = headers;

  let response = await fetch(`${API_URL}${path}`, requestOptions);

  if (response.status === 401 && !requestOptions.__retry && path !== "/auth/refresh") {
    const refreshed = await refreshTokenIfNeeded();
    if (refreshed) {
      return apiRequest(path, { ...requestOptions, __retry: true });
    }

    throw new Error("Your session has expired. Please sign in again.");
  }

  if (response.status === 204) {
    return null;
  }

  const payloadText = await response.text();
  let payload = {};
  try {
    payload = payloadText ? JSON.parse(payloadText) : {};
  } catch {
    payload = { message: payloadText };
  }

  if (!response.ok) {
    throw new Error(formatApiError(payload));
  }

  return payload;
}

export { API_URL };
