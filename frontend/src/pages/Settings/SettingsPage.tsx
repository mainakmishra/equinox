import React, { useEffect, useState } from 'react';
import './SettingsPage.css';
import SignedInNavbar from '../../components/Navbar/SignedInNavbar';
import { fetchUserProfileByEmail } from '../../api/profileApi';

export default function SettingsPage() {
    const handleSignOut = () => {
        localStorage.removeItem('signedIn');
        window.location.href = '/';
    };
    const [googleConnected, setGoogleConnected] = useState(true);
    const [outlookConnected, setOutlookConnected] = useState(false);
    const [stravaConnected, setStravaConnected] = useState(false);

    // Profile state
    const [profile, setProfile] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        // Get email from localStorage
        const email = localStorage.getItem('user_email');
        if (email) {
            fetchUserProfileByEmail(email)
                .then(setProfile)
                .catch(() => setError("Could not load profile"))
                .finally(() => setLoading(false));
        } else {
            setError('No user email found. Please sign in.');
            setLoading(false);
        }
    }, []);

    return (
        <>
            <SignedInNavbar onSignOut={handleSignOut} />
            <div className="settingspage">
                <div className="settingspage-content">
                    <h1 className="settingspage-title">Profile</h1>
                    {loading && <p>Loading profile...</p>}
                    {error && <p style={{ color: "red" }}>{error}</p>}
                    {profile && (
                        <div className="profile-section">
                            {profile.avatar_url && (
                                <img src={profile.avatar_url} alt="avatar" className="profile-avatar" />
                            )}
                            <p><strong>Name:</strong> {profile.name}</p>
                            <p><strong>Email:</strong> {profile.email}</p>
                            {/* Add more fields as needed */}
                        </div>
                    )}
                </div>
                <div className="settingspage-content">
                    <h1 className="settingspage-title">Apps Connected</h1>
                    <div className="apps-list">
                        <div className="app-toggle">
                            <span className="app-name">Google</span>
                            <label className="switch">
                                <input
                                    type="checkbox"
                                    checked={googleConnected}
                                    onChange={() => setGoogleConnected(!googleConnected)}
                                />
                                <span className="slider"></span>
                            </label>
                        </div>
                        <div className="app-toggle">
                            <span className="app-name">Outlook</span>
                            <label className="switch">
                                <input
                                    type="checkbox"
                                    checked={outlookConnected}
                                    onChange={() => setOutlookConnected(!outlookConnected)}
                                />
                                <span className="slider"></span>
                            </label>
                        </div>
                        <div className="app-toggle">
                            <span className="app-name">Strava</span>
                            <label className="switch">
                                <input
                                    type="checkbox"
                                    checked={stravaConnected}
                                    onChange={() => setStravaConnected(!stravaConnected)}
                                />
                                <span className="slider"></span>
                            </label>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
}
