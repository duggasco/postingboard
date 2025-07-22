import React from 'react';
import { useNavigate } from 'react-router-dom';

function IdeaCard({ idea, onClaim, getPriorityClass, getSizeClass }) {
  const navigate = useNavigate();
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    });
  };

  const isOverdue = new Date(idea.needed_by) < new Date() && idea.status === 'open';

  const handleCardClick = () => {
    navigate(`/ideas/${idea.id}`);
  };

  const handleClaimClick = (e) => {
    e.stopPropagation();
    onClaim();
  };

  return (
    <div 
      className={`idea-card ${idea.status === 'claimed' ? 'claimed' : ''} ${idea.status === 'complete' ? 'complete' : ''}`}
      onClick={handleCardClick}
      style={{ cursor: 'pointer' }}
    >
      <div className="idea-header">
        <h3>{idea.title}</h3>
        <div className="idea-badges">
          <span className={`badge ${getPriorityClass(idea.priority)}`}>
            {idea.priority.toUpperCase()}
          </span>
          <span className={`badge ${getSizeClass(idea.size)}`}>
            {idea.size.replace('_', ' ').toUpperCase()}
          </span>
        </div>
      </div>

      <p className="idea-description">{idea.description}</p>

      <div className="idea-details">
        <div className="detail-row">
          <span className="detail-label">Team:</span>
          <span className="detail-value">{idea.benefactor_team}</span>
        </div>
        <div className="detail-row">
          <span className="detail-label">Needed by:</span>
          <span className={`detail-value ${isOverdue ? 'overdue' : ''}`}>
            {formatDate(idea.needed_by)}
            {isOverdue && ' (OVERDUE)'}
          </span>
        </div>
        {idea.reward && (
          <div className="detail-row">
            <span className="detail-label">Reward:</span>
            <span className="detail-value reward">{idea.reward}</span>
          </div>
        )}
      </div>

      <div className="idea-skills">
        <span className="skills-label">Required Skills:</span>
        <div className="skills-list">
          {idea.skills.map((skill, index) => (
            <span key={index} className="skill-tag">{skill}</span>
          ))}
        </div>
      </div>

      <div className="idea-footer">
        <span className="submission-date">
          Posted {formatDate(idea.date_submitted)}
        </span>
        {idea.status === 'open' && (
          <button className="btn-claim" onClick={handleClaimClick}>
            Claim This Idea
          </button>
        )}
        {idea.status === 'claimed' && idea.claims.length > 0 && (
          <span className="status-text">
            Claimed by {idea.claims[0].claimer_name}
          </span>
        )}
        {idea.status === 'complete' && (
          <span className="status-text complete">
            Completed
          </span>
        )}
      </div>
    </div>
  );
}

export default IdeaCard;