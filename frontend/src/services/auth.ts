// Servicio de autenticación con JWT
import { LoginResponse, UserResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';
const TOKEN_EXPIRY_KEY = 'auth_token_expiry';

export interface AuthState {
  token: string | null;
  user: UserResponse | null;
  isAuthenticated: boolean;
}

/**
 * Guarda el token y usuario en localStorage
 */
export function saveAuth(loginResponse: LoginResponse): void {
  localStorage.setItem(TOKEN_KEY, loginResponse.access_token);
  localStorage.setItem(USER_KEY, JSON.stringify(loginResponse.user));

  // Calcular expiración (30 min por defecto)
  const expiryTime = Date.now() + 30 * 60 * 1000;
  localStorage.setItem(TOKEN_EXPIRY_KEY, expiryTime.toString());
}

/**
 * Obtiene el token actual
 */
export function getToken(): string | null {
  const token = localStorage.getItem(TOKEN_KEY);
  const expiry = localStorage.getItem(TOKEN_EXPIRY_KEY);

  if (!token || !expiry) {
    return null;
  }

  // Verificar si el token ha expirado
  if (Date.now() > parseInt(expiry, 10)) {
    clearAuth();
    return null;
  }

  return token;
}

/**
 * Obtiene el usuario actual
 */
export function getUser(): UserResponse | null {
  const userStr = localStorage.getItem(USER_KEY);
  if (!userStr) return null;

  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
}

/**
 * Verifica si el usuario está autenticado
 */
export function isAuthenticated(): boolean {
  return getToken() !== null;
}

/**
 * Limpia la autenticación
 */
export function clearAuth(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  localStorage.removeItem(TOKEN_EXPIRY_KEY);
}

/**
 * Obtiene el estado de autenticación completo
 */
export function getAuthState(): AuthState {
  const token = getToken();
  const user = getUser();

  return {
    token,
    user,
    isAuthenticated: token !== null
  };
}

/**
 * Login
 */
export async function login(username: string, password: string): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error de autenticación');
  }

  const data: LoginResponse = await response.json();
  saveAuth(data);
  return data;
}

/**
 * Logout
 */
export async function logout(): Promise<void> {
  const token = getToken();

  if (token) {
    try {
      await fetch(`${API_BASE_URL}/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
    } catch (e) {
      // Ignorar errores de logout en el servidor
    }
  }

  clearAuth();
}

/**
 * Verifica el token actual con el servidor
 */
export async function verifyToken(): Promise<UserResponse | null> {
  const token = getToken();

  if (!token) return null;

  try {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      clearAuth();
      return null;
    }

    return response.json();
  } catch {
    clearAuth();
    return null;
  }
}

/**
 * Helper para hacer fetch autenticado
 */
export async function authFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const token = getToken();

  if (!token) {
    throw new Error('No autenticado');
  }

  const headers = new Headers(options.headers);
  headers.set('Authorization', `Bearer ${token}`);

  return fetch(url, {
    ...options,
    headers,
  });
}
