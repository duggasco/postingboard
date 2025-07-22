import React, { useState } from 'react';
import { ideaApi } from '../api/api';

function ClaimModal({ idea, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    claimer_name: '',
    claimer_email: '',
    claimer_skills: '',
    claimer_team: ''
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setErrors(prev => ({ ...prev, [name]: '' }));
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.claimer_name.trim()) newErrors.claimer_name = 'Name is required';
    if (!formData.claimer_email.trim()) newErrors.claimer_email = 'Email is required';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setLoading(true);
    try {
      await ideaApi.claimIdea(idea.id, formData);
      onSuccess();
    } catch (error) {
      console.error('Failed to claim idea:', error);
      setErrors({ submit: 'Failed to claim idea. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Claim Idea: {idea.title}</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>

        <form onSubmit={handleSubmit} className="claim-form">
          <div className="form-group">
            <label htmlFor="claimer_name">Your Name*</label>
            <input
              type="text"
              id="claimer_name"
              name="claimer_name"
              value={formData.claimer_name}
              onChange={handleChange}
              className={errors.claimer_name ? 'error' : ''}
            />
            {errors.claimer_name && <span className="error-message">{errors.claimer_name}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="claimer_email">Your Email*</label>
            <input
              type="email"
              id="claimer_email"
              name="claimer_email"
              value={formData.claimer_email}
              onChange={handleChange}
              className={errors.claimer_email ? 'error' : ''}
            />
            {errors.claimer_email && <span className="error-message">{errors.claimer_email}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="claimer_team">Your Team</label>
            <input
              type="text"
              id="claimer_team"
              name="claimer_team"
              value={formData.claimer_team}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label htmlFor="claimer_skills">Your Skills</label>
            <textarea
              id="claimer_skills"
              name="claimer_skills"
              value={formData.claimer_skills}
              onChange={handleChange}
              rows="3"
              placeholder="List your relevant skills..."
            />
          </div>

          <div className="info-box">
            <p><strong>Note:</strong> By claiming this idea, you commit to working on it. The idea owner will be notified of your claim.</p>
          </div>

          {errors.submit && <div className="error-message submit-error">{errors.submit}</div>}

          <div className="form-actions">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Claiming...' : 'Claim Idea'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ClaimModal;