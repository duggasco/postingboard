import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authApi, ideaApi, skillApi } from '../api/api';

function AdminDashboard() {
  const [stats, setStats] = useState({
    totalIdeas: 0,
    openIdeas: 0,
    claimedIdeas: 0,
    completedIdeas: 0,
    totalSkills: 0,
  });
  const navigate = useNavigate();

  useEffect(() => {
    checkAuth();
    fetchStats();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await authApi.checkAuth();
      if (!response.data.is_admin) {
        navigate('/admin');
      }
    } catch (err) {
      navigate('/admin');
    }
  };

  const fetchStats = async () => {
    try {
      const [ideasResponse, skillsResponse] = await Promise.all([
        ideaApi.getIdeas(),
        skillApi.getSkills(),
      ]);

      const ideas = ideasResponse.data;
      const stats = {
        totalIdeas: ideas.length,
        openIdeas: ideas.filter(idea => idea.status === 'open').length,
        claimedIdeas: ideas.filter(idea => idea.status === 'claimed').length,
        completedIdeas: ideas.filter(idea => idea.status === 'complete').length,
        totalSkills: skillsResponse.data.length,
      };

      setStats(stats);
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  const handleLogout = async () => {
    try {
      await authApi.logout();
      navigate('/');
    } catch (err) {
      console.error('Error logging out:', err);
    }
  };

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <h1>Admin Dashboard</h1>
        <button onClick={handleLogout} className="logout-button">
          Logout
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Ideas</h3>
          <p className="stat-number">{stats.totalIdeas}</p>
        </div>
        <div className="stat-card">
          <h3>Open Ideas</h3>
          <p className="stat-number">{stats.openIdeas}</p>
        </div>
        <div className="stat-card">
          <h3>Claimed Ideas</h3>
          <p className="stat-number">{stats.claimedIdeas}</p>
        </div>
        <div className="stat-card">
          <h3>Completed Ideas</h3>
          <p className="stat-number">{stats.completedIdeas}</p>
        </div>
        <div className="stat-card">
          <h3>Total Skills</h3>
          <p className="stat-number">{stats.totalSkills}</p>
        </div>
      </div>

      <div className="admin-actions">
        <h2>Admin Actions</h2>
        <div className="action-buttons">
          <Link to="/admin/ideas" className="action-button">
            Manage Ideas
          </Link>
          <Link to="/admin/skills" className="action-button">
            Manage Skills
          </Link>
          <Link to="/" className="action-button secondary">
            View Public Site
          </Link>
        </div>
      </div>
    </div>
  );
}

export default AdminDashboard;