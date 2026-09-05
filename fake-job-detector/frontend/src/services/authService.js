import apiClient from './api';

export const authService = {
  async login(email, password) {
    try {
      const response = await apiClient.post('/auth/login', { email, password });
      const { token, user } = response.data;
      localStorage.setItem('sentinel_auth_token', token);
      localStorage.setItem('sentinel_user', JSON.stringify(user));
      return { token, user };
    } catch (err) {
      const errMsg = err.response?.data?.detail || err.message || 'Authentication failed';
      throw new Error(errMsg);
    }
  },

  async register(fullName, email, password) {
    try {
      const response = await apiClient.post('/auth/register', { full_name: fullName, email, password });
      const { token, user } = response.data;
      localStorage.setItem('sentinel_auth_token', token);
      localStorage.setItem('sentinel_user', JSON.stringify(user));
      return { token, user };
    } catch (err) {
      const errMsg = err.response?.data?.detail || err.message || 'Registration failed';
      throw new Error(errMsg);
    }
  },

  async loginWithGoogle(idToken) {
    if (!idToken) {
      throw new Error('Google ID token is required for authentication');
    }

    try {
      const response = await apiClient.post('/auth/google', { id_token: idToken });
      const { token, user } = response.data;
      localStorage.setItem('sentinel_auth_token', token);
      localStorage.setItem('sentinel_user', JSON.stringify(user));
      return { token, user };
    } catch (err) {
      const errMsg = err.response?.data?.detail || err.message || 'Google OAuth authentication failed';
      throw new Error(errMsg);
    }
  },

  async getMe() {
    try {
      const response = await apiClient.get('/auth/me');
      if (response.data) {
        localStorage.setItem('sentinel_user', JSON.stringify(response.data));
        return response.data;
      }
    } catch (err) {
      console.error('Session verification failed:', err);
    }

    const stored = localStorage.getItem('sentinel_user');
    if (stored) {
      try {
        return JSON.parse(stored);
      } catch (e) {
        // ignore parse error
      }
    }
    return null;
  },

  logout() {
    localStorage.removeItem('sentinel_auth_token');
    localStorage.removeItem('sentinel_user');
  },

  isAuthenticated() {
    return !!localStorage.getItem('sentinel_auth_token');
  },
};

export default authService;
