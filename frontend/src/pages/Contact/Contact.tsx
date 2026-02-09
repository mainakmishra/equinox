import { Mail, Phone, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import './Contact.css';

const teamMembers = [
    {
        name: 'Deepak Kumar',
        phone: '+91 99739 87089',
        email: 'deep997398@gmail.com',
    },
    {
        name: 'Mainak Mishra',
        phone: '+91 7908272014',
        email: 'mainakmishra00@gmail.com',
    },
    {
        name: 'Abhayjit Singh Gulati',
        phone: '+91 96200 01934',
        email: 'singhabhayjit07@gmail.com',
    },
];

export function Contact() {
    return (
        <div className="contact-page">
            <div className="contact-container">
                <Link to="/" className="contact-back">
                    <ArrowLeft size={18} />
                    Back to Home
                </Link>

                <div className="contact-header">
                    <h1 className="contact-title">Talk to Us</h1>
                    <p className="contact-subtitle">
                        Get in touch with our team. We'd love to hear from you.
                    </p>
                </div>

                <div className="contact-grid">
                    {teamMembers.map((member) => (
                        <div key={member.email} className="contact-card">
                            <div className="contact-card__avatar">
                                {member.name.split(' ').map(n => n[0]).join('')}
                            </div>
                            <h3 className="contact-card__name">{member.name}</h3>

                            <div className="contact-card__details">
                                <a href={`tel:${member.phone.replace(/\s/g, '')}`} className="contact-card__link">
                                    <Phone size={16} />
                                    {member.phone}
                                </a>
                                <a href={`mailto:${member.email}`} className="contact-card__link">
                                    <Mail size={16} />
                                    {member.email}
                                </a>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
