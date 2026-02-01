// HealthLogPopup component - Shows when daily health is not logged
import { useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { logHealth } from '../../api/healthApi';
import type { HealthLogInput } from '../../api/healthApi';
import './HealthLogPopup.css';

interface HealthLogPopupProps {
    onClose: () => void;
    onLogged: () => void;
}

export default function HealthLogPopup({ onClose, onLogged }: HealthLogPopupProps) {
    const navigate = useNavigate();
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [formData, setFormData] = useState<HealthLogInput>({
        sleep_hours: 7,
        sleep_quality: 7,
        energy_level: 7,
        stress_level: 5,
        mood_score: 7,
        // These are set to 0 since users can update them later in the day
        activity_minutes: 0,
        steps: 0,
        water_glasses: 0,
        caffeine_cups: 0,
        notes: '',
    });

    const handleSliderChange = (field: keyof HealthLogInput, value: number) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const handleInputChange = (field: keyof HealthLogInput, value: string | number) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        try {
            await logHealth(formData);
            onLogged();
            onClose();
        } catch (err) {
            console.error('Error logging health:', err);
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleGoToWellness = () => {
        onClose();
        navigate('/wellness');
    };

    return (
        <div className="popup-overlay" onClick={onClose}>
            <div className="popup-content" onClick={(e) => e.stopPropagation()}>
                <button className="popup-close" onClick={onClose}>×</button>

                <div className="popup-header">
                    <h2>Daily Health Check-in</h2>
                    <p>Take a moment to log how you're feeling today</p>
                </div>

                <form onSubmit={handleSubmit} className="popup-form">
                    <div className="popup-form-row">
                        <div className="popup-form-group">
                            <label>Hours Slept</label>
                            <input
                                type="number"
                                min="0"
                                max="24"
                                step="0.5"
                                value={formData.sleep_hours}
                                onChange={(e) => handleInputChange('sleep_hours', parseFloat(e.target.value) || 0)}
                            />
                        </div>
                        <div className="popup-slider-group">
                            <div className="popup-slider-header">
                                <label>Sleep Quality</label>
                                <span>{formData.sleep_quality}/10</span>
                            </div>
                            <input
                                type="range"
                                min="1"
                                max="10"
                                value={formData.sleep_quality}
                                onChange={(e) => handleSliderChange('sleep_quality', parseInt(e.target.value))}
                            />
                        </div>
                    </div>

                    <div className="popup-form-row">
                        <div className="popup-slider-group">
                            <div className="popup-slider-header">
                                <label>Energy</label>
                                <span>{formData.energy_level}/10</span>
                            </div>
                            <input
                                type="range"
                                min="1"
                                max="10"
                                value={formData.energy_level}
                                onChange={(e) => handleSliderChange('energy_level', parseInt(e.target.value))}
                            />
                        </div>
                        <div className="popup-slider-group">
                            <div className="popup-slider-header">
                                <label>Stress</label>
                                <span>{formData.stress_level}/10</span>
                            </div>
                            <input
                                type="range"
                                min="1"
                                max="10"
                                value={formData.stress_level}
                                onChange={(e) => handleSliderChange('stress_level', parseInt(e.target.value))}
                            />
                        </div>
                        <div className="popup-slider-group">
                            <div className="popup-slider-header">
                                <label>Mood</label>
                                <span>{formData.mood_score}/10</span>
                            </div>
                            <input
                                type="range"
                                min="1"
                                max="10"
                                value={formData.mood_score}
                                onChange={(e) => handleSliderChange('mood_score', parseInt(e.target.value))}
                            />
                        </div>
                    </div>

                    <div className="popup-actions">
                        <button type="submit" className="popup-submit-btn" disabled={isSubmitting}>
                            {isSubmitting ? 'Saving...' : 'Log Health'}
                        </button>
                        <button type="button" className="popup-link-btn" onClick={handleGoToWellness}>
                            Full Form →
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
