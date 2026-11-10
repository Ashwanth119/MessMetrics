import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Placeholder from './pages/Placeholder'
import ProtectedRoute from './components/ProtectedRoute'
import StudentLayout from './layouts/StudentLayout'
import Profile from './pages/Profile'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />

        <Route element={<ProtectedRoute />}>
          <Route element={<StudentLayout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/menu" element={<Placeholder title="Today's Menu" />} />
            <Route path="/calories" element={<Placeholder title="Calorie Tracker" />} />
            <Route path="/nutrition" element={<Placeholder title="Nutrition" />} />
            <Route path="/profile" element={<Profile/>} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App