import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ideaApi, skillApi } from '../api/api';

function IdeaForm() {
  const navigate = useNavigate();
  const [availableSkills, setAvailableSkills] = useState([]);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    email: '',
    benefactor_team: '',
    size: 'small',
    reward: '',
    needed_by: '',
    priority: 'low',
    skills: [],
    newSkill: ''
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSkills();
  }, []);

  const fetchSkills = async () => {
    try {
      const response = await skillApi.getSkills();
      setAvailableSkills(response.data);
    } catch (error) {
      console.error('Failed to fetch skills:', error);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setErrors(prev => ({ ...prev, [name]: '' }));
  };

  const handleSkillToggle = (skillName) => {
    setFormData(prev => ({
      ...prev,
      skills: prev.skills.includes(skillName)
        ? prev.skills.filter(s => s !== skillName)
        : [...prev.skills, skillName]
    }));
  };

  const handleAddNewSkill = () => {
    if (formData.newSkill.trim() && !formData.skills.includes(formData.newSkill.trim())) {
      setFormData(prev => ({
        ...prev,
        skills: [...prev.skills, prev.newSkill.trim()],
        newSkill: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.title.trim()) newErrors.title = 'Title is required';
    if (!formData.description.trim()) newErrors.description = 'Description is required';
    if (!formData.email.trim()) newErrors.email = 'Email is required';
    if (!formData.benefactor_team.trim()) newErrors.benefactor_team = 'Benefactor team is required';
    if (!formData.needed_by) newErrors.needed_by = 'Needed by date is required';
    if (formData.skills.length === 0) newErrors.skills = 'At least one skill is required';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setLoading(true);
    try {
      console.log('Submitting form data:', formData);
      await ideaApi.createIdea(formData);
      navigate('/');
    } catch (error) {
      console.error('Failed to create idea:', error);
      console.error('Error response:', error.response);
      const errorMessage = error.response?.data?.error || 'Failed to create idea. Please try again.';
      setErrors({ submit: errorMessage });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="idea-form-container">
      <h2>Post a New Idea</h2>
      <form onSubmit={handleSubmit} className="idea-form">
        <div className="form-group">
          <label htmlFor="title">Title*</label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            className={errors.title ? 'error' : ''}
          />
          {errors.title && <span className="error-message">{errors.title}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="description">Description*</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows="4"
            className={errors.description ? 'error' : ''}
          />
          {errors.description && <span className="error-message">{errors.description}</span>}
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="email">Your Email*</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className={errors.email ? 'error' : ''}
            />
            {errors.email && <span className="error-message">{errors.email}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="benefactor_team">Benefactor Team*</label>
            <input
              type="text"
              id="benefactor_team"
              name="benefactor_team"
              value={formData.benefactor_team}
              onChange={handleChange}
              className={errors.benefactor_team ? 'error' : ''}
            />
            {errors.benefactor_team && <span className="error-message">{errors.benefactor_team}</span>}
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="size">Size</label>
            <select
              id="size"
              name="size"
              value={formData.size}
              onChange={handleChange}
            >
              <option value="small">Small</option>
              <option value="medium">Medium</option>
              <option value="large">Large</option>
              <option value="extra_large">Extra Large</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="priority">Priority</label>
            <select
              id="priority"
              name="priority"
              value={formData.priority}
              onChange={handleChange}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="needed_by">Needed By Date*</label>
            <input
              type="date"
              id="needed_by"
              name="needed_by"
              value={formData.needed_by}
              onChange={handleChange}
              className={errors.needed_by ? 'error' : ''}
            />
            {errors.needed_by && <span className="error-message">{errors.needed_by}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="reward">Reward</label>
            <input
              type="text"
              id="reward"
              name="reward"
              value={formData.reward}
              onChange={handleChange}
              placeholder="BLK swag, lunch, etc."
            />
          </div>
        </div>

        <div className="form-group">
          <label>Required Skills*</label>
          
          <div className="skill-selection">
            <div className="skill-dropdown-row">
              <select 
                className="skill-dropdown"
                value=""
                onChange={(e) => {
                  if (e.target.value && !formData.skills.includes(e.target.value)) {
                    handleSkillToggle(e.target.value);
                  }
                }}
              >
                <option value="">Select a skill from dropdown...</option>
                {availableSkills
                  .filter(skill => !formData.skills.includes(skill.name))
                  .map(skill => (
                    <option key={skill.id} value={skill.name}>
                      {skill.name}
                    </option>
                  ))}
              </select>
              <span className="or-divider">OR</span>
              <div className="add-skill-input">
                <input
                  type="text"
                  placeholder="Add custom skill"
                  value={formData.newSkill}
                  onChange={(e) => setFormData(prev => ({ ...prev, newSkill: e.target.value }))}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddNewSkill())}
                />
                <button type="button" onClick={handleAddNewSkill}>Add</button>
              </div>
            </div>
            
            <div className="selected-skills">
              {formData.skills.length > 0 && (
                <>
                  <div className="selected-skills-label">Selected Skills:</div>
                  <div className="skills-tags">
                    {formData.skills.map(skill => (
                      <div key={skill} className="skill-tag">
                        <span>{skill}</span>
                        <button 
                          type="button" 
                          className="remove-skill"
                          onClick={() => handleSkillToggle(skill)}
                          aria-label={`Remove ${skill}`}
                        >
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>
          
          {errors.skills && <span className="error-message">{errors.skills}</span>}
        </div>

        {errors.submit && <div className="error-message submit-error">{errors.submit}</div>}

        <div className="form-actions">
          <button type="button" onClick={() => navigate('/')} className="btn-secondary">
            Cancel
          </button>
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Posting...' : 'Post Idea'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default IdeaForm;