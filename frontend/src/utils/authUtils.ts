// Auth utility functions for consistent session management

export const isAuthenticated = (): boolean => {
    return localStorage.getItem('signedIn') === 'true';
};

export const getUserEmail = (): string => {
    return localStorage.getItem('user_email') || '';
};

export const setAuth = (email: string): void => {
    localStorage.setItem('signedIn', 'true');
    localStorage.setItem('user_email', email);
};

export const clearAuth = (): void => {
    localStorage.removeItem('signedIn');
    localStorage.removeItem('user_email');
};
