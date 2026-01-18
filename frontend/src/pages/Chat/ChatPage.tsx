import React, { useState } from 'react';
import './ChatPage.css'

export default function ChatInterface() {
    const [messages, setMessages] = useState<{ text: string; sender: string; id: number }[]>([]);
    const [input, setInput] = useState('');

    const handleSubmit = async (e: any) => {
        if (e) e.preventDefault();
        if (!input.trim()) return;
        const PORT = import.meta.env.REACT_APP_BACKEND_PORT || '8000';
        const userMsg = { text: input, sender: 'user', id: Date.now() };
        setMessages(prev => [...prev, userMsg]);
        setInput('');

        try {
            const res = await fetch(`http://localhost:${PORT}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: input })
            });
            const data = await res.json();
            setMessages(prev => [...prev, { text: data.reply, sender: 'bot', id: Date.now() }]);
        } catch {
            setMessages(prev => [...prev, { text: 'Error connecting to AI', sender: 'bot', id: Date.now() }]);
        }
    };

    return (
        <div className="chat-container">
            <div className="messages-container">
                {messages.length === 0 ? (
                    <div className="empty-state">
                        <p>Start a conversation...</p>
                    </div>
                ) : (
                    messages.map((msg) => (
                        <div key={msg.id} className={`message ${msg.sender}`}>
                            <div className="message-bubble">
                                {msg.text}
                            </div>
                        </div>
                    ))
                )}
            </div>

            <div className="input-container">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSubmit(e)}
                    placeholder="Type your message..."
                    className="chat-input"
                />
                <button onClick={handleSubmit} className="send-button">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
                    </svg>
                </button>
            </div>
        </div>
    );
}