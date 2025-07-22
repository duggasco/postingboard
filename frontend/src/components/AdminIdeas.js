import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authApi, ideaApi, adminApi, skillApi } from '../api/api';

function AdminIdeas() {
  const [ideas, setIdeas] = useState([]);
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    checkAuth();
    fetchData();
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

  const fetchData = async () => {
    try {
      const [ideasResponse, skillsResponse] = await Promise.all([
        ideaApi.getIdeas(),
        skillApi.getSkills(),
      ]);
      setIdeas(ideasResponse.data);
      setSkills(skillsResponse.data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching data:', err);
      setLoading(false);
    }
  };

  const handleEdit = (idea) => {
    setEditingId(idea.id);
    setEditForm({
      title: idea.title,
      description: idea.description,
      email: idea.email,
      benefactor_team: idea.benefactor_team,
      size: idea.size,
      reward: idea.reward || '',
      needed_by: idea.needed_by.split('T')[0],
      priority: idea.priority,
      status: idea.status,
      skills: idea.skills,
    });
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditForm({});
  };

  const handleSaveEdit = async (id) => {
    try {
      const data = {
        ...editForm,
        needed_by: new Date(editForm.needed_by).toISOString(),
      };
      await adminApi.updateIdea(id, data);
      await fetchData();
      setEditingId(null);
      setEditForm({});
    } catch (err) {
      console.error('Error updating idea:', err);
      alert('Error updating idea');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this idea?')) {
      try {
        await adminApi.deleteIdea(id);
        await fetchData();
      } catch (err) {
        console.error('Error deleting idea:', err);
        alert('Error deleting idea');
      }
    }
  };

  const handleStatusChange = async (id, newStatus) => {
    try {
      await adminApi.updateIdea(id, { status: newStatus });
      await fetchData();
    } catch (err) {
      console.error('Error updating status:', err);
      alert('Error updating status');
    }
  };

  const handleSkillToggle = (skillName) => {
    const currentSkills = editForm.skills || [];
    if (currentSkills.includes(skillName)) {
      setEditForm({
        ...editForm,
        skills: currentSkills.filter(s => s !== skillName),
      });
    } else {
      setEditForm({
        ...editForm,
        skills: [...currentSkills, skillName],
      });
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="admin-ideas">
      <div className="admin-header">
        <h1>Manage Ideas</h1>
        <Link to="/admin/dashboard" className="back-link">
          Back to Dashboard
        </Link>
      </div>

      <div className="ideas-table">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Team</th>
              <th>Status</th>
              <th>Priority</th>
              <th>Size</th>
              <th>Skills</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {ideas.map(idea => (
              <tr key={idea.id}>
                {editingId === idea.id ? (
                  <>
                    <td>{idea.id}</td>
                    <td>
                      <input
                        type="text"
                        value={editForm.title}
                        onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                      />
                    </td>
                    <td>
                      <input
                        type="text"
                        value={editForm.benefactor_team}
                        onChange={(e) => setEditForm({ ...editForm, benefactor_team: e.target.value })}
                      />
                    </td>
                    <td>
                      <select
                        value={editForm.status}
                        onChange={(e) => setEditForm({ ...editForm, status: e.target.value })}
                      >
                        <option value="open">Open</option>
                        <option value="claimed">Claimed</option>
                        <option value="complete">Complete</option>
                      </select>
                    </td>
                    <td>
                      <select
                        value={editForm.priority}
                        onChange={(e) => setEditForm({ ...editForm, priority: e.target.value })}
                      >
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                      </select>
                    </td>
                    <td>
                      <select
                        value={editForm.size}
                        onChange={(e) => setEditForm({ ...editForm, size: e.target.value })}
                      >
                        <option value="small">Small</option>
                        <option value="medium">Medium</option>
                        <option value="large">Large</option>
                        <option value="extra_large">Extra Large</option>
                      </select>
                    </td>
                    <td>
                      <div className="skill-checkboxes">
                        {skills.map(skill => (
                          <label key={skill.id}>
                            <input
                              type="checkbox"
                              checked={editForm.skills.includes(skill.name)}
                              onChange={() => handleSkillToggle(skill.name)}
                            />
                            {skill.name}
                          </label>
                        ))}
                      </div>
                    </td>
                    <td>
                      <button onClick={() => handleSaveEdit(idea.id)} className="save-btn">
                        Save
                      </button>
                      <button onClick={handleCancelEdit} className="cancel-btn">
                        Cancel
                      </button>
                    </td>
                  </>
                ) : (
                  <>
                    <td>{idea.id}</td>
                    <td>{idea.title}</td>
                    <td>{idea.benefactor_team}</td>
                    <td>
                      <select
                        value={idea.status}
                        onChange={(e) => handleStatusChange(idea.id, e.target.value)}
                        className="status-select"
                      >
                        <option value="open">Open</option>
                        <option value="claimed">Claimed</option>
                        <option value="complete">Complete</option>
                      </select>
                    </td>
                    <td className={`priority-${idea.priority}`}>
                      {idea.priority.charAt(0).toUpperCase() + idea.priority.slice(1)}
                    </td>
                    <td>{idea.size}</td>
                    <td>{idea.skills.join(', ')}</td>
                    <td>
                      <button onClick={() => handleEdit(idea)} className="edit-btn">
                        Edit
                      </button>
                      <button onClick={() => handleDelete(idea.id)} className="delete-btn">
                        Delete
                      </button>
                    </td>
                  </>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default AdminIdeas;