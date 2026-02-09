import { useState } from 'react';
import { getUserEmail, isAuthenticated, clearAuth } from '../../utils/authUtils';
import { generateBriefing, type BriefingResponse } from '../../api/briefingApi';
import SignedInNavbar from '../../components/Navbar/SignedInNavbar';
import './BriefingPage.css';

export default function BriefingPage() {
    const [briefing, setBriefing] = useState<BriefingResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const userEmail = getUserEmail();
    const isLoggedIn = isAuthenticated();

    const handleSignOut = () => {
        clearAuth();
        window.location.href = '/';
    };

    const handleGenerateBriefing = async () => {
        if (!userEmail) {
            setError('Please sign in to generate your briefing');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const data = await generateBriefing(userEmail);
            setBriefing(data);
        } catch (err) {
            console.error('Briefing generation error:', err);
            setError('Failed to generate briefing. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <SignedInNavbar onSignOut={handleSignOut} />
            <div className="briefing-page">
                <div className="briefing-container">
                    <h1 className="briefing-page-title">Morning Briefing</h1>
                    <p className="briefing-page-subtitle">
                        Your daily summary combining wellness and productivity
                    </p>

                    {!briefing && (
                        <button
                            className="btn btn--primary btn-generate"
                            onClick={handleGenerateBriefing}
                            disabled={loading || !isLoggedIn}
                        >
                            {loading ? 'Generating...' : 'Generate Briefing'}
                        </button>
                    )}

                    {error && (
                        <div className="briefing-error">
                            <p>{error}</p>
                        </div>
                    )}

                    {briefing && (
                        <div className="briefing-card">
                            <h2 className="briefing-greeting">{briefing.greeting} 🌅</h2>

                            <div className="briefing-items">
                                {isLoggedIn && (
                                    <div className="briefing-item">
                                        <span className="briefing-icon">🌙</span>
                                        <span className="briefing-text">
                                            Sleep Score: {briefing.sleep_score}
                                        </span>
                                    </div>
                                )}

                                <div className="briefing-item">
                                    <span className="briefing-icon">📧</span>
                                    <span className="briefing-text">
                                        {briefing.critical_emails} Critical Email{briefing.critical_emails !== 1 ? 's' : ''}
                                    </span>
                                </div>

                                <div className="briefing-item">
                                    <span className="briefing-icon">✅</span>
                                    <span className="briefing-text">
                                        {briefing.schedule_updated
                                            ? `${briefing.tasks_count} Task${briefing.tasks_count !== 1 ? 's' : ''} Today`
                                            : 'No tasks scheduled'}
                                    </span>
                                </div>
                            </div>

                            {briefing.summary && (
                                <div className="briefing-summary">
                                    <p>{briefing.summary}</p>
                                </div>
                            )}

                            <button
                                className="btn btn--secondary btn-new-briefing"
                                onClick={handleGenerateBriefing}
                                disabled={loading}
                            >
                                Generate New Briefing
                            </button>
                        </div>
                    )}

                    {!isLoggedIn && !briefing && (
                        <div className="briefing-sign-in-prompt">
                            <p>Please sign in to view your daily briefing</p>
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}
