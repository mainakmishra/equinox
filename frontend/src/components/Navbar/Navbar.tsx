import { useState } from "react";
import { Menu, X } from "lucide-react";
import "./Navbar.css";
import { handleGoogleSignIn } from '../../api/authApi';
import { ThemeToggle } from '../ThemeToggle/ThemeToggle';

export function Navbar() {
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    return (
        <header className="navbar">
            <nav className="navbar__inner">
                {/* Logo */}
                <a href="/" className="navbar__logo">
                    Equinox
                </a>

                {/* Desktop Navigation */}
                <div className="navbar__links">
                    <a href="#features" className="navbar__link">
                        Features
                    </a>
                    <a href="#how-it-works" className="navbar__link">
                        How It Works
                    </a>
                    <a href="#briefing" className="navbar__link">
                        Morning Briefing
                    </a>
                </div>

                {/* Desktop Actions */}
                <div className="navbar__actions">
                    <ThemeToggle />
                    <button
                        className="navbar__signin"
                        onClick={handleGoogleSignIn}
                    >
                        Sign In
                    </button>
                </div>

                {/* Mobile Menu Toggle */}
                <button
                    type="button"
                    className="navbar__mobile-toggle"
                    onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                    aria-label="Toggle menu"
                >
                    {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
                </button>
            </nav>

            {/* Mobile Navigation */}
            {mobileMenuOpen && (
                <div className="navbar__mobile-menu">
                    <div className="navbar__mobile-links">
                        <a href="#features" className="navbar__mobile-link">
                            Features
                        </a>
                        <a href="#how-it-works" className="navbar__mobile-link">
                            How It Works
                        </a>
                        <a href="#briefing" className="navbar__mobile-link">
                            Morning Briefing
                        </a>
                    </div>

                    <div className="navbar__mobile-actions">
                        <ThemeToggle />
                        <button
                            className="navbar__signin"
                            onClick={handleGoogleSignIn}
                        >
                            Sign In
                        </button>
                    </div>
                </div>
            )}
        </header>
    );
}
