import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '../lib/api';

interface User {
    id: string;
    email: string;
    full_name: string;
    roles: { code: string; name: string }[];
    effective_permissions: string[];
}

interface AuthContextType {
    user: User | null;
    loading: boolean;
    login: (email: string, password: string) => Promise<void>;
    logout: () => Promise<void>;
    hasPermission: (perm: string) => boolean;
    hasRole: (role: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    const fetchMe = useCallback(async () => {
        try {
            const data = await api.get<User>('/auth/me/');
            setUser(data);
        } catch {
            setUser(null);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchMe();
    }, [fetchMe]);

    const login = async (email: string, password: string) => {
        const data = await api.post<{ user: User; csrf_token: string; redirect_url: string }>('/auth/login/', {
            email,
            password,
        });
        setUser(data.user);
        document.cookie = `csrftoken=${data.csrf_token}; path=/`;
    };

    const logout = async () => {
        await api.post('/auth/logout/', {});
        setUser(null);
    };

    const hasPermission = (perm: string) => {
        if (!user) return false;
        return user.effective_permissions.includes(perm) || user.roles.some(r => r.code === 'sysadmin');
    };

    const hasRole = (role: string) => {
        if (!user) return false;
        return user.roles.some(r => r.code === role);
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout, hasPermission, hasRole }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth must be used within AuthProvider');
    return ctx;
};