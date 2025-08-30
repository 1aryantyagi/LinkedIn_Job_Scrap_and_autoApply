import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [user, setUser] = useState(null);

    useEffect(() => {
        // Check if user is already logged in (from localStorage)
        const savedAuth = localStorage.getItem('eazyjobs_auth');
        if (savedAuth) {
            const authData = JSON.parse(savedAuth);
            setIsAuthenticated(true);
            setUser(authData.user);
        }
    }, []);

    const login = (email, password) => {
        // Simple authentication logic - in production, this would call your backend
        if (email && password) {
            const userData = {
                email,
                name: email.split('@')[0],
                role: 'Job Scraper'
            };

            setIsAuthenticated(true);
            setUser(userData);

            // Save to localStorage
            localStorage.setItem('eazyjobs_auth', JSON.stringify({
                isAuthenticated: true,
                user: userData
            }));

            return true;
        }
        return false;
    };

    const logout = () => {
        setIsAuthenticated(false);
        setUser(null);
        localStorage.removeItem('eazyjobs_auth');
    };

    const value = {
        isAuthenticated,
        user,
        login,
        logout
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};