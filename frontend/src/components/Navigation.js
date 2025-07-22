import React from 'react';
import { Link } from 'react-router-dom';

function Navigation() {
  return (
    <nav className="navbar">
      <div className="nav-container">
        <h1 className="nav-title">Citizen Developer Posting Board</h1>
        <div className="nav-links">
          <Link to="/" className="nav-link">View Ideas</Link>
          <Link to="/new-idea" className="nav-link nav-link-primary">Post New Idea</Link>
        </div>
      </div>
    </nav>
  );
}

export default Navigation;