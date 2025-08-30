import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import {
    Briefcase,
    Search,
    Download,
    Trash2,
    Eye,
    Save,
    RefreshCw,
    BarChart3,
    Clock,
    CheckCircle,
    XCircle,
    Link as LinkIcon
} from 'lucide-react';
import toast from 'react-hot-toast';
import api from "../api";

const Dashboard = () => {
    const { user, logout } = useAuth();
    const [keyword, setKeyword] = useState('');
    const [targetPosts, setTargetPosts] = useState(50);
    const [isLoading, setIsLoading] = useState(false);
    const [results, setResults] = useState({});
    const [savedJobs, setSavedJobs] = useState([]);
    const [stats, setStats] = useState({
        totalScrapes: 0,
        totalJobs: 0,
        savedJobs: 0,
        activeScrapingTasks: 0
    });

    // Load saved jobs from localStorage
    useEffect(() => {
        const saved = localStorage.getItem('eazyjobs_saved');
        if (saved) {
            setSavedJobs(JSON.parse(saved));
        }
        loadResults();
        loadStats();
    }, []);

    const loadResults = async () => {
        try {
            const response = await api.get('/results');
            setResults(response.data.results || {});
        } catch (error) {
            console.error('Failed to load results:', error);
        }
    };

    const loadStats = async () => {
        try {
            const response = await api.get('/health');
            const allResults = await api.get('/results');

            const totalJobs = Object.values(allResults.data.results || {})
                .reduce((sum, result) => sum + (result.total_posts || 0), 0);

            setStats({
                totalScrapes: Object.keys(allResults.data.results || {}).length,
                totalJobs,
                savedJobs: savedJobs.length,
                activeScrapingTasks: response.data.active_scraping_tasks || 0
            });
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    };

    const handleScrape = async (e) => {
        e.preventDefault();

        if (!keyword.trim()) {
            toast.error('Please enter a keyword');
            return;
        }

        setIsLoading(true);

        try {
            const response = await api.post('/scrape', {
                input_keyword: keyword,
                target_posts: targetPosts,
                headless: true
            });

            if (response.data.success) {
                toast.success(`Scraping started for "${keyword}"`);

                // Poll for results
                const pollInterval = setInterval(async () => {
                    try {
                        const statusResponse = await api.get(`/status/${keyword.toLowerCase()}`);

                        if (statusResponse.data.status === 'completed') {
                            clearInterval(pollInterval);
                            toast.success(`Scraping completed for "${keyword}"`);
                            loadResults();
                            loadStats();
                        } else if (statusResponse.data.status === 'failed') {
                            clearInterval(pollInterval);
                            toast.error(`Scraping failed for "${keyword}"`);
                        }
                    } catch (error) {
                        clearInterval(pollInterval);
                        console.error('Polling error:', error);
                    }
                }, 3000);

                // Clear polling after 5 minutes
                setTimeout(() => {
                    clearInterval(pollInterval);
                }, 300000);

                setKeyword('');
                loadStats();
            } else {
                toast.error(response.data.message || 'Failed to start scraping');
            }
        } catch (error) {
            toast.error('Failed to start scraping');
            console.error('Scraping error:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const viewResults = async (keyword) => {
        try {
            const response = await api.get(`/results/${keyword.toLowerCase()}`);
            const result = response.data;

            toast.success(`Found ${result.total_posts} jobs for "${keyword}"`);

            // Show results in a simple alert for now - you can enhance this with a modal
            alert(`Results for "${keyword}":\n\nTotal Posts: ${result.total_posts}\nTimestamp: ${new Date(result.timestamp).toLocaleString()}\n\nFirst 5 links:\n${result.links.slice(0, 5).join('\n')}`);
        } catch (error) {
            toast.error('Failed to load results');
            console.error('View results error:', error);
        }
    };

    const saveJobLinks = (keyword) => {
        const result = results[keyword.toLowerCase()];
        if (result && result.links) {
            const newSavedJobs = result.links.map(link => ({
                id: Date.now() + Math.random(),
                url: link,
                keyword,
                savedAt: new Date().toISOString()
            }));

            const updatedSavedJobs = [...savedJobs, ...newSavedJobs];
            setSavedJobs(updatedSavedJobs);
            localStorage.setItem('eazyjobs_saved', JSON.stringify(updatedSavedJobs));

            toast.success(`Saved ${result.links.length} job links`);
            loadStats();
        }
    };

    const deleteResults = async (keyword) => {
        try {
            await api.delete(`/results/${keyword.toLowerCase()}`);
            toast.success(`Deleted results for "${keyword}"`);
            loadResults();
            loadStats();
        } catch (error) {
            toast.error('Failed to delete results');
            console.error('Delete error:', error);
        }
    };

    const deleteSavedJob = (jobId) => {
        const updatedSavedJobs = savedJobs.filter(job => job.id !== jobId);
        setSavedJobs(updatedSavedJobs);
        localStorage.setItem('eazyjobs_saved', JSON.stringify(updatedSavedJobs));
        toast.success('Job link removed');
        loadStats();
    };

    const getStatusIcon = (keyword) => {
        const result = results[keyword.toLowerCase()];
        if (!result) return <Clock className="status-icon" size={16} />;

        if (result.success) {
            return <CheckCircle className="status-icon" size={16} />;
        } else {
            return <XCircle className="status-icon" size={16} />;
        }
    };

    const getStatusBadge = (keyword) => {
        const result = results[keyword.toLowerCase()];
        if (!result) return <span className="status-badge status-progress">In Progress</span>;

        if (result.success) {
            return <span className="status-badge status-completed">Completed</span>;
        } else {
            return <span className="status-badge status-failed">Failed</span>;
        }
    };

    return (
        <div className="dashboard">
            {/* Header */}
            <div className="dashboard-header">
                <div className="dashboard-title">
                    <Briefcase size={28} />
                    <h1>EazyJobs Dashboard</h1>
                </div>
                <div className="user-section">
                    <div className="user-info">
                        <div className="user-name">{user?.name}</div>
                        <div className="user-role">{user?.role}</div>
                    </div>
                    <button onClick={logout} className="logout-btn">
                        Logout
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <div className="dashboard-content">
                {/* Stats Grid */}
                <div className="stats-grid">
                    <div className="stat-card">
                        <div className="stat-icon blue">
                            <BarChart3 size={24} />
                        </div>
                        <div className="stat-info">
                            <h3>{stats.totalScrapes}</h3>
                            <p>Total Scrapes</p>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-icon green">
                            <Briefcase size={24} />
                        </div>
                        <div className="stat-info">
                            <h3>{stats.totalJobs}</h3>
                            <p>Jobs Found</p>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-icon orange">
                            <Save size={24} />
                        </div>
                        <div className="stat-info">
                            <h3>{stats.savedJobs}</h3>
                            <p>Saved Jobs</p>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-icon purple">
                            <Clock size={24} />
                        </div>
                        <div className="stat-info">
                            <h3>{stats.activeScrapingTasks}</h3>
                            <p>Active Tasks</p>
                        </div>
                    </div>
                </div>

                {/* Scrape Section */}
                <div className="action-section">
                    <h2 className="section-title">
                        <Search size={20} />
                        Start New Job Scrape
                    </h2>

                    <form onSubmit={handleScrape} className="scrape-form">
                        <div className="input-group">
                            <label htmlFor="keyword">Job Keyword</label>
                            <input
                                type="text"
                                id="keyword"
                                value={keyword}
                                onChange={(e) => setKeyword(e.target.value)}
                                placeholder="e.g., software engineer, marketing"
                                required
                            />
                        </div>

                        <div className="input-group">
                            <label htmlFor="targetPosts">Target Posts</label>
                            <input
                                type="number"
                                id="targetPosts"
                                value={targetPosts}
                                onChange={(e) => setTargetPosts(Number(e.target.value))}
                                min="1"
                                max="200"
                                required
                            />
                        </div>

                        <button type="submit" className="scrape-btn" disabled={isLoading}>
                            {isLoading ? (
                                <>
                                    <span className="loading"></span>
                                    Scraping...
                                </>
                            ) : (
                                <>
                                    <Search size={16} style={{ marginRight: '8px' }} />
                                    Start Scraping
                                </>
                            )}
                        </button>
                    </form>
                </div>

                {/* Results Section */}
                <div className="results-section">
                    <div className="results-header">
                        <h2 className="section-title">
                            <BarChart3 size={20} />
                            Scraping Results
                        </h2>
                        <div className="results-actions">
                            <button onClick={loadResults} className="btn-secondary">
                                <RefreshCw size={16} style={{ marginRight: '8px' }} />
                                Refresh
                            </button>
                        </div>
                    </div>

                    <div className="results-grid">
                        {Object.keys(results).length === 0 ? (
                            <div className="empty-state">
                                <h3>No results yet</h3>
                                <p>Start scraping to see your results here</p>
                            </div>
                        ) : (
                            Object.entries(results).map(([keyword, result]) => (
                                <div key={keyword} className="result-item">
                                    <div className="result-info">
                                        <div className="result-keyword">
                                            {getStatusIcon(keyword)}
                                            {result.keyword || keyword}
                                        </div>
                                        <div className="result-meta">
                                            {result.success ? (
                                                <>
                                                    {result.total_posts} jobs found • {new Date(result.timestamp).toLocaleDateString()}
                                                </>
                                            ) : (
                                                <>
                                                    Failed • {new Date(result.timestamp).toLocaleDateString()}
                                                </>
                                            )}
                                        </div>
                                    </div>

                                    <div className="result-actions">
                                        {getStatusBadge(keyword)}
                                        {result.success && (
                                            <>
                                                <button
                                                    onClick={() => viewResults(keyword)}
                                                    className="btn-small btn-view"
                                                >
                                                    <Eye size={14} style={{ marginRight: '4px' }} />
                                                    View
                                                </button>
                                                <button
                                                    onClick={() => saveJobLinks(keyword)}
                                                    className="btn-small btn-save"
                                                >
                                                    <Save size={14} style={{ marginRight: '4px' }} />
                                                    Save Links
                                                </button>
                                            </>
                                        )}
                                        <button
                                            onClick={() => deleteResults(keyword)}
                                            className="btn-small btn-delete"
                                        >
                                            <Trash2 size={14} style={{ marginRight: '4px' }} />
                                            Delete
                                        </button>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Saved Jobs Section */}
                <div className="saved-jobs-section">
                    <h2 className="section-title">
                        <LinkIcon size={20} />
                        Saved Job Links ({savedJobs.length})
                    </h2>

                    {savedJobs.length === 0 ? (
                        <div className="empty-state">
                            <h3>No saved jobs yet</h3>
                            <p>Save job links from your scraping results to access them later</p>
                        </div>
                    ) : (
                        <div className="results-grid">
                            {savedJobs.map((job) => (
                                <div key={job.id} className="job-link">
                                    <a
                                        href={job.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="job-url"
                                    >
                                        {job.url}
                                    </a>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                        <span style={{ fontSize: '0.75rem', color: '#666' }}>
                                            {job.keyword} • {new Date(job.savedAt).toLocaleDateString()}
                                        </span>
                                        <button
                                            onClick={() => deleteSavedJob(job.id)}
                                            className="btn-small btn-delete"
                                        >
                                            <Trash2 size={12} />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;