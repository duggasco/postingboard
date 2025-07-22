import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authApi, skillApi, adminApi } from '../api/api';

function AdminSkills() {
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newSkillName, setNewSkillName] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editName, setEditName] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    checkAuth();
    fetchSkills();
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

  const fetchSkills = async () => {
    try {
      const response = await skillApi.getSkills();
      setSkills(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching skills:', err);
      setLoading(false);
    }
  };

  const handleAddSkill = async (e) => {
    e.preventDefault();
    if (!newSkillName.trim()) return;

    try {
      await adminApi.createSkill({ name: newSkillName });
      setNewSkillName('');
      await fetchSkills();
    } catch (err) {
      console.error('Error adding skill:', err);
      if (err.response?.data?.error) {
        alert(err.response.data.error);
      } else {
        alert('Error adding skill');
      }
    }
  };

  const handleEdit = (skill) => {
    setEditingId(skill.id);
    setEditName(skill.name);
  };

  const handleSaveEdit = async (id) => {
    if (!editName.trim()) return;

    try {
      await adminApi.updateSkill(id, { name: editName });
      setEditingId(null);
      setEditName('');
      await fetchSkills();
    } catch (err) {
      console.error('Error updating skill:', err);
      if (err.response?.data?.error) {
        alert(err.response.data.error);
      } else {
        alert('Error updating skill');
      }
    }
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditName('');
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this skill?')) {
      try {
        await adminApi.deleteSkill(id);
        await fetchSkills();
      } catch (err) {
        console.error('Error deleting skill:', err);
        if (err.response?.data?.error) {
          alert(err.response.data.error);
        } else {
          alert('Error deleting skill');
        }
      }
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="admin-skills">
      <div className="admin-header">
        <h1>Manage Skills</h1>
        <Link to="/admin/dashboard" className="back-link">
          Back to Dashboard
        </Link>
      </div>

      <div className="add-skill-form">
        <h2>Add New Skill</h2>
        <form onSubmit={handleAddSkill}>
          <input
            type="text"
            value={newSkillName}
            onChange={(e) => setNewSkillName(e.target.value)}
            placeholder="Enter skill name"
            required
          />
          <button type="submit">Add Skill</button>
        </form>
      </div>

      <div className="skills-list">
        <h2>Existing Skills</h2>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {skills.map(skill => (
              <tr key={skill.id}>
                <td>{skill.id}</td>
                <td>
                  {editingId === skill.id ? (
                    <input
                      type="text"
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                      autoFocus
                    />
                  ) : (
                    skill.name
                  )}
                </td>
                <td>
                  {editingId === skill.id ? (
                    <>
                      <button onClick={() => handleSaveEdit(skill.id)} className="save-btn">
                        Save
                      </button>
                      <button onClick={handleCancelEdit} className="cancel-btn">
                        Cancel
                      </button>
                    </>
                  ) : (
                    <>
                      <button onClick={() => handleEdit(skill)} className="edit-btn">
                        Edit
                      </button>
                      <button onClick={() => handleDelete(skill.id)} className="delete-btn">
                        Delete
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default AdminSkills;