import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import IdeaList from './components/IdeaList';
import IdeaForm from './components/IdeaForm';
import IdeaDetail from './components/IdeaDetail';
import Navigation from './components/Navigation';
import AdminLogin from './components/AdminLogin';
import AdminDashboard from './components/AdminDashboard';
import AdminIdeas from './components/AdminIdeas';
import AdminSkills from './components/AdminSkills';

function App() {
  return (
    <Router>
      <div className="App">
        <Navigation />
        <div className="container">
          <Routes>
            <Route path="/" element={<IdeaList />} />
            <Route path="/new-idea" element={<IdeaForm />} />
            <Route path="/ideas/:id" element={<IdeaDetail />} />
            <Route path="/admin" element={<AdminLogin />} />
            <Route path="/admin/dashboard" element={<AdminDashboard />} />
            <Route path="/admin/ideas" element={<AdminIdeas />} />
            <Route path="/admin/skills" element={<AdminSkills />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
