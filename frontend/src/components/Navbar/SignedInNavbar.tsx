
import { Link } from 'react-router-dom';
import './SignedNavbar.css';

export default function SignedInNavbar({ onSignOut }: { onSignOut?: () => void }) {
    return (
        <nav className="navbar">
            <div className="navbar-links">
                <Link className="navbar-link" to="/chat">Chat</Link>
                <Link className="navbar-link" to="/agents">Agents</Link>
                <Link className="navbar-link" to="/wellness">Wellness</Link>
                <Link className="navbar-link" to="/settings">Settings</Link>
                <Link className="navbar-link" to="/notes">Notes</Link>
                <button className="signout-btn" onClick={onSignOut}>Sign Out</button>
            </div>
        </nav>
    );
}
