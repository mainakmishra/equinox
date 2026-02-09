import { Link, useLocation } from 'react-router-dom';
import { ThemeToggle } from '../ThemeToggle/ThemeToggle';
import './SignedNavbar.css';

export default function SignedInNavbar({ onSignOut }: { onSignOut?: () => void }) {
    const location = useLocation();

    const isActive = (path: string) => location.pathname === path;

    return (
        <nav className="signed-navbar">
            <div className="signed-navbar__inner">
                {/* Logo */}
                <Link to="/" className="signed-navbar__logo">
                    Equinox
                </Link>

                {/* Navigation Links */}
                <div className="signed-navbar__links">
                    <Link
                        className={`signed-navbar__link ${isActive('/chat') ? 'active' : ''}`}
                        to="/chat"
                    >
                        Chat
                    </Link>
                    <Link
                        className={`signed-navbar__link ${isActive('/agents') ? 'active' : ''}`}
                        to="/agents"
                    >
                        Agents
                    </Link>
                    <Link
                        className={`signed-navbar__link ${isActive('/wellness') ? 'active' : ''}`}
                        to="/wellness"
                    >
                        Wellness
                    </Link>
                    <Link
                        className={`signed-navbar__link ${isActive('/briefing') ? 'active' : ''}`}
                        to="/briefing"
                    >
                        Briefing
                    </Link>
                    <Link
                        className={`signed-navbar__link ${isActive('/notes') ? 'active' : ''}`}
                        to="/notes"
                    >
                        Notes
                    </Link>
                    <Link
                        className={`signed-navbar__link ${isActive('/todos') ? 'active' : ''}`}
                        to="/todos"
                    >
                        Todos
                    </Link>
                    <Link
                        className={`signed-navbar__link ${isActive('/settings') ? 'active' : ''}`}
                        to="/settings"
                    >
                        Settings
                    </Link>
                </div>

                {/* Actions */}
                <div className="signed-navbar__actions">
                    <ThemeToggle />
                    <button className="signed-navbar__signout" onClick={onSignOut}>
                        Sign Out
                    </button>
                </div>
            </div>
        </nav>
    );
}
