import React, { useState, useEffect, useCallback } from 'react';
import { ideaApi, skillApi } from '../api/api';
import IdeaCard from './IdeaCard';
import ClaimModal from './ClaimModal';

function IdeaList() {
  const [ideas, setIdeas] = useState([]);
  const [skills, setSkills] = useState([]);
  const [filters, setFilters] = useState({
    skill: '',
    priority: '',
    team: '',
    status: '',
    sortBy: 'date_submitted',
    order: 'desc'
  });
  const [loading, setLoading] = useState(true);
  const [selectedIdea, setSelectedIdea] = useState(null);
  const [showClaimModal, setShowClaimModal] = useState(false);
  const [teams, setTeams] = useState([]);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [ideasResponse, skillsResponse] = await Promise.all([
        ideaApi.getIdeas({
          skill: filters.skill,
          priority: filters.priority,
          team: filters.team,
          status: filters.status,
          sort_by: filters.sortBy,
          order: filters.order
        }),
        skillApi.getSkills()
      ]);
      
      setIdeas(ideasResponse.data);
      setSkills(skillsResponse.data);
      
      const uniqueTeams = [...new Set(ideasResponse.data.map(idea => idea.benefactor_team))];
      setTeams(uniqueTeams.filter(team => team));
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
  };

  const handleClaimIdea = (idea) => {
    setSelectedIdea(idea);
    setShowClaimModal(true);
  };

  const handleClaimSuccess = () => {
    setShowClaimModal(false);
    setSelectedIdea(null);
    fetchData();
  };

  const getPriorityClass = (priority) => {
    switch (priority) {
      case 'high':
        return 'priority-high';
      case 'medium':
        return 'priority-medium';
      default:
        return 'priority-low';
    }
  };

  const getSizeClass = (size) => {
    switch (size) {
      case 'extra_large':
        return 'size-xl';
      case 'large':
        return 'size-l';
      case 'medium':
        return 'size-m';
      default:
        return 'size-s';
    }
  };

  return (
    <div className="idea-list-container">
      <div className="filters-section">
        <h2>Filter & Sort Ideas</h2>
        <div className="filters-grid">
          <div className="filter-group">
            <label htmlFor="skill-filter">Skill</label>
            <select
              id="skill-filter"
              value={filters.skill}
              onChange={(e) => handleFilterChange('skill', e.target.value)}
            >
              <option value="">All Skills</option>
              {skills.map(skill => (
                <option key={skill.id} value={skill.name}>{skill.name}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="priority-filter">Priority</label>
            <select
              id="priority-filter"
              value={filters.priority}
              onChange={(e) => handleFilterChange('priority', e.target.value)}
            >
              <option value="">All Priorities</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="team-filter">Team</label>
            <select
              id="team-filter"
              value={filters.team}
              onChange={(e) => handleFilterChange('team', e.target.value)}
            >
              <option value="">All Teams</option>
              {teams.map(team => (
                <option key={team} value={team}>{team}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="status-filter">Status</label>
            <select
              id="status-filter"
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
            >
              <option value="">All Statuses</option>
              <option value="open">Open</option>
              <option value="claimed">Claimed</option>
              <option value="complete">Complete</option>
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="sort-filter">Sort By</label>
            <select
              id="sort-filter"
              value={filters.sortBy}
              onChange={(e) => handleFilterChange('sortBy', e.target.value)}
            >
              <option value="date_submitted">Date Submitted</option>
              <option value="needed_by">Needed By Date</option>
              <option value="priority">Priority</option>
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="order-filter">Order</label>
            <select
              id="order-filter"
              value={filters.order}
              onChange={(e) => handleFilterChange('order', e.target.value)}
            >
              <option value="desc">Descending</option>
              <option value="asc">Ascending</option>
            </select>
          </div>
        </div>
      </div>

      <div className="ideas-section">
        <h2>Available Ideas ({ideas.filter(idea => idea.status === 'open').length} open)</h2>
        {loading ? (
          <div className="loading">Loading ideas...</div>
        ) : ideas.length === 0 ? (
          <div className="no-ideas">No ideas found. Be the first to post one!</div>
        ) : (
          <div className="ideas-grid">
            {ideas.map(idea => (
              <IdeaCard
                key={idea.id}
                idea={idea}
                onClaim={() => handleClaimIdea(idea)}
                getPriorityClass={getPriorityClass}
                getSizeClass={getSizeClass}
              />
            ))}
          </div>
        )}
      </div>

      {showClaimModal && (
        <ClaimModal
          idea={selectedIdea}
          onClose={() => setShowClaimModal(false)}
          onSuccess={handleClaimSuccess}
        />
      )}
    </div>
  );
}

export default IdeaList;