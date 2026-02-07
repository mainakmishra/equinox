import { useEffect, useState } from 'react';
import './SettingsPage.css';
import SignedInNavbar from '../../components/Navbar/SignedInNavbar';
import { fetchUserProfileByEmail } from '../../api/profileApi';
import { getUserEmail, clearAuth } from '../../utils/authUtils';

export default function SettingsPage() {
    const userEmail = getUserEmail(); // Get email directly from localStorage

    const handleSignOut = () => {
        clearAuth();
        window.location.href = '/';
    };

    const [googleConnected, setGoogleConnected] = useState(true);
    const [outlookConnected, setOutlookConnected] = useState(false);
    const [stravaConnected, setStravaConnected] = useState(false);

    // Profile state
    const [profile, setProfile] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (userEmail) {
            fetchUserProfileByEmail(userEmail)
                .then(setProfile)
                .catch((err) => {
                    console.error('Profile fetch error:', err);
                    // Don't set error - we'll use localStorage email as fallback
                })
                .finally(() => setLoading(false));
        } else {
            setLoading(false);
        }
    }, [userEmail]);

    // Extract name from email (before @) as fallback
    const displayName = profile?.name || userEmail?.split('@')[0] || 'User';
    const displayEmail = profile?.email || userEmail || 'Not available';

    return (
        <>
            <SignedInNavbar onSignOut={handleSignOut} />
            <div className="settingspage">
                <div className="settingspage-content">
                    <h1 className="settingspage-title">Profile</h1>
                    {loading ? (
                        <div className="profile-skeleton">
                            <div className="skeleton-avatar"></div>
                            <div className="skeleton-text"></div>
                            <div className="skeleton-text short"></div>
                        </div>
                    ) : (
                        <div className="profile-section">
                            {profile?.avatar_url && (
                                <img src={profile.avatar_url} alt="avatar" className="profile-avatar" />
                            )}
                            <div className="profile-info">
                                <div className="profile-row">
                                    <span className="profile-label">Name</span>
                                    <span className="profile-value">{displayName}</span>
                                </div>
                                <div className="profile-row">
                                    <span className="profile-label">Email</span>
                                    <span className="profile-value">{displayEmail}</span>
                                </div>
                            </div>
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
