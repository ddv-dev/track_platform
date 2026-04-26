// frontend/src/App.jsx
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { Navbar } from './components/layout/Navbar';
import { HomePage } from './pages/HomePage';
import { TracksPage } from './pages/TracksPage';
import { TrackDetailPage } from './pages/TrackDetailPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ProfilePage } from './pages/ProfilePage';
import { ChatPage } from './pages/ChatPage';
import { PracticalReviewsPage } from './pages/PracticalReviewsPage';
import { CuratorRequestsPage } from './pages/CuratorRequestsPage';
import { CuratorStatsPage } from './pages/CuratorStatsPage';
// Импортируем новые компоненты
import { TeacherTasksPage } from './pages/TeacherTasksPage.jsx';
import { TeacherStatsPage } from './pages/TeacherStatsPage';
import { useAuth } from './hooks/useAuth';

const PrivateRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" />;
};

const CuratorRoute = ({ children }) => {
  const { isAuthenticated, user } = useAuth();
  return isAuthenticated && user?.role === 'curator' ? children : <Navigate to="/" />;
};

// Создаём защитник для маршрутов преподавателя
const TeacherRoute = ({ children }) => {
  const { isAuthenticated, user } = useAuth();
  return isAuthenticated && user?.role === 'teacher' ? children : <Navigate to="/" />;
};

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/tracks" element={<TracksPage />} />
        <Route path="/tracks/:id" element={<TrackDetailPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/profile" element={<PrivateRoute><ProfilePage /></PrivateRoute>} />
        <Route path="/chat" element={<PrivateRoute><ChatPage /></PrivateRoute>} />
        <Route path="/curator/reviews" element={<CuratorRoute><PracticalReviewsPage /></CuratorRoute>} />
        <Route path="/curator/requests" element={<CuratorRoute><CuratorRequestsPage /></CuratorRoute>} />
        <Route path="/curator/stats" element={<CuratorRoute><CuratorStatsPage /></CuratorRoute>} />
        {/* Новые маршруты для преподавателя */}
        <Route path="/teacher/tasks" element={<TeacherRoute><TeacherTasksPage /></TeacherRoute>} />
        <Route path="/teacher/stats" element={<TeacherRoute><TeacherStatsPage /></TeacherRoute>} />
      </Routes>
      <Toaster position="top-right" />
    </BrowserRouter>
  );
}

export default App;