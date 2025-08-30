import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { User, Lock, Briefcase } from 'lucide-react';
import toast from 'react-hot-toast';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!email || !password) {
            toast.error('Please fill in all fields');
            return;
        }

        setIsLoading(true);

        try {
            // Simulate API call delay
            await new Promise(resolve => setTimeout(resolve, 1000));

            const success = login(email, password);

            if (success) {
                toast.success('Welcome to EazyJobs!');
                navigate('/dashboard');
            } else {
                toast.error('Invalid credentials');
            }
        } catch (error) {
            toast.error('Login failed. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-card">
                <div className="logo">
                    <Briefcase size={32} style={{ display: 'inline', marginRight: '10px' }} />
                    EazyJobs
                </div>
                <p className="login-subtitle">Find your dream job with ease</p>

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="email">
                            <User size={16} style={{ display: 'inline', marginRight: '8px' }} />
                            Email Address
                        </label>
                        <input
                            type="email"
                            id="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="Enter your email"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">
                            <Lock size={16} style={{ display: 'inline', marginRight: '8px' }} />
                            Password
                        </label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter your password"
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        className="login-btn"
                        disabled={isLoading}
                    >
                        {isLoading ? (
                            <>
                                <span className="loading"></span>
                                Signing In...
                            </>
                        ) : (
                            'Sign In'
                        )}
                    </button>
                </form>

                <div style={{ marginTop: '20px', fontSize: '0.875rem', color: '#666' }}>
                    Demo credentials: Any email and password will work
                </div>
            </div>
        </div>
    );
};

export default Login;