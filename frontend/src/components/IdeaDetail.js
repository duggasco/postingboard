import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ideaApi } from '../api/api';
import ClaimModal from './ClaimModal';

function IdeaDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [idea, setIdea] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showClaimModal, setShowClaimModal] = useState(false);

  useEffect(() => {
    fetchIdea();
  }, [id]);

  const fetchIdea = async () => {
    try {
      setLoading(true);
      const response = await ideaApi.getIdea(id);
      setIdea(response.data);
    } catch (error) {
      console.error('Failed to fetch idea:', error);
      setError('Failed to load idea details');
    } finally {
      setLoading(false);
    }
  };

  const handleClaim = async (claimData) => {
    try {
      await ideaApi.claimIdea(idea.id, claimData);
      setShowClaimModal(false);
      fetchIdea(); // Refresh the idea to show updated status
    } catch (error) {
      console.error('Failed to claim idea:', error);
      throw error;
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'long', 
      day: 'numeric', 
      year: 'numeric' 
    });
  };

  const getPriorityClass = (priority) => {
    switch(priority) {
      case 'high': return 'priority-high';
      case 'medium': return 'priority-medium';
      default: return 'priority-low';
    }
  };

  const getSizeClass = (size) => {
    switch(size) {
      case 'extra_large': return 'size-xl';
      case 'large': return 'size-large';
      case 'medium': return 'size-medium';
      default: return 'size-small';
    }
  };

  if (loading) {
    return <div className="loading">Loading idea details...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  if (!idea) {
    return <div className="error-message">Idea not found</div>;
  }

  const isOverdue = new Date(idea.needed_by) < new Date() && idea.status === 'open';

  return (
    <div className="idea-detail-container">
      <button className="back-button" onClick={() => navigate('/')}>
        ← Back to Ideas
      </button>

      <div className={`idea-detail ${idea.status === 'claimed' ? 'claimed' : ''} ${idea.status === 'complete' ? 'complete' : ''}`}>
        <div className="idea-detail-header">
          <h1>{idea.title}</h1>
          <div className="idea-badges">
            <span className={`badge ${getPriorityClass(idea.priority)}`}>
              {idea.priority.toUpperCase()}
            </span>
            <span className={`badge ${getSizeClass(idea.size)}`}>
              {idea.size.replace('_', ' ').toUpperCase()}
            </span>
            {idea.status !== 'open' && (
              <span className={`badge status-${idea.status}`}>
                {idea.status.toUpperCase()}
              </span>
            )}
          </div>
        </div>

        <div className="idea-detail-content">
          <section className="description-section">
            <h2>Description</h2>
            <p className="idea-full-description">{idea.description}</p>
          </section>

          <section className="details-section">
            <h2>Details</h2>
            <div className="details-grid">
              <div className="detail-item">
                <span className="detail-label">Benefactor Team:</span>
                <span className="detail-value">{idea.benefactor_team}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Contact Email:</span>
                <span className="detail-value">{idea.email}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Needed By:</span>
                <span className={`detail-value ${isOverdue ? 'overdue' : ''}`}>
                  {formatDate(idea.needed_by)}
                  {isOverdue && ' (OVERDUE)'}
                </span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Posted On:</span>
                <span className="detail-value">{formatDate(idea.date_submitted)}</span>
              </div>
              {idea.reward && (
                <div className="detail-item">
                  <span className="detail-label">Reward:</span>
                  <span className="detail-value reward">{idea.reward}</span>
                </div>
              )}
            </div>
          </section>

          <section className="skills-section">
            <h2>Required Skills</h2>
            <div className="skills-list">
              {idea.skills.map((skill, index) => (
                <span key={index} className="skill-tag large">{skill}</span>
              ))}
            </div>
          </section>

          {idea.claims && idea.claims.length > 0 && (
            <section className="claims-section">
              <h2>Claim History</h2>
              <div className="claims-list">
                {idea.claims.map((claim, index) => (
                  <div key={index} className="claim-item">
                    <div className="claim-header">
                      <span className="claimer-name">{claim.claimer_name}</span>
                      <span className="claim-date">{formatDate(claim.claim_date)}</span>
                    </div>
                    <div className="claim-details">
                      <span className="claim-team">{claim.claimer_team}</span>
                      {claim.claimer_skills && (
                        <span className="claim-skills">Skills: {claim.claimer_skills}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>

        <div className="idea-detail-actions">
          {idea.status === 'open' && (
            <button 
              className="btn-primary btn-large" 
              onClick={() => setShowClaimModal(true)}
            >
              Claim This Idea
            </button>
          )}
        </div>
      </div>

      {showClaimModal && (
        <ClaimModal
          idea={idea}
          onClose={() => setShowClaimModal(false)}
          onSubmit={handleClaim}
        />
      )}
    </div>
  );
}

export default IdeaDetail;