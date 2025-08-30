import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import { AuthProvider, useAuth } from './context/AuthContext';
import './App.css';

function App() {
    return (
        <AuthProvider>
            <Router>
                <div className="App">
                    <Toaster position="top-right" />
                    <Routes>
                        <Route path="/login" element={<Login />} />
                        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
                        <Route path="/" element={<Navigate to="/login" />} />
                    </Routes>
                </div>
            </Router>
        </AuthProvider>
    );
}

function ProtectedRoute({ children }) {
    const { isAuthenticated } = useAuth();
    return isAuthenticated ? children : <Navigate to="/login" />;
}

export default App;