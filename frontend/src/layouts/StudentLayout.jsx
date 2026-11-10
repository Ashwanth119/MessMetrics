import { useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import './StudentLayout.css'

function StudentLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const navigate = useNavigate()

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: '⌂' },
    { name: "Today's Menu", path: '/menu', icon: '☷' },
    { name: 'Calorie Tracker', path: '/calories', icon: '◷' },
    { name: 'Nutrition', path: '/nutrition', icon: '♧' },
    { name: 'Profile', path: '/profile', icon: '◎' }
  ]

  function handleLogout() {
    localStorage.removeItem('access_token')
    navigate('/login', { replace: true })
  }

  return (
    <div className="student-layout">
      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside className={`student-sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-brand">
          <h2>MessMetrics</h2>
          <span>Student Portal</span>
        </div>

        <nav className="sidebar-nav">
          <p className="sidebar-section-title">MENU</p>

          {navItems.map(item => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? 'active' : ''}`
              }
              onClick={() => setSidebarOpen(false)}
            >
              <span className="sidebar-icon">{item.icon}</span>
              {item.name}
            </NavLink>
          ))}
        </nav>

        <button className="sidebar-logout" onClick={handleLogout}>
          <span className="sidebar-icon">↪</span>
          Logout
        </button>
      </aside>

      <div className="student-main">
        <header className="student-header">
          <button
            className="sidebar-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            ☰
          </button>
          <span>MessMetrics</span>
        </header>

        <main className="student-content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default StudentLayout