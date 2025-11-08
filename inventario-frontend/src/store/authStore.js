import { create } from 'zustand';
const decodeToken = (token) => {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64)
            .split('')
            .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
            .join(''));
        return JSON.parse(jsonPayload);
    }
    catch (error) {
        console.error('Error decoding token:', error);
        return null;
    }
};
export const useAuthStore = create((set, get) => {
    // Load from localStorage on init
    const savedToken = localStorage.getItem('auth_token');
    const savedUser = localStorage.getItem('auth_user');
    const savedRefreshToken = localStorage.getItem('auth_refresh_token');
    return {
        user: savedUser ? JSON.parse(savedUser) : null,
        token: savedToken,
        refreshToken: savedRefreshToken,
        isAuthenticated: !!savedToken,
        login: (user, token, refreshToken) => {
            localStorage.setItem('auth_token', token);
            localStorage.setItem('auth_user', JSON.stringify(user));
            if (refreshToken) {
                localStorage.setItem('auth_refresh_token', refreshToken);
            }
            set({
                user,
                token,
                refreshToken: refreshToken || null,
                isAuthenticated: true,
            });
        },
        logout: () => {
            localStorage.removeItem('auth_token');
            localStorage.removeItem('auth_user');
            localStorage.removeItem('auth_refresh_token');
            set({
                user: null,
                token: null,
                refreshToken: null,
                isAuthenticated: false,
            });
        },
        setToken: (token) => {
            localStorage.setItem('auth_token', token);
            set({ token, isAuthenticated: true });
        },
        setUser: (user) => {
            localStorage.setItem('auth_user', JSON.stringify(user));
            set({ user });
        },
        isTokenExpired: () => {
            const { token } = get();
            if (!token)
                return true;
            const payload = decodeToken(token);
            if (!payload)
                return true;
            return payload.exp * 1000 < Date.now();
        },
        getToken: () => {
            return get().token;
        },
    };
});
