import { useEffect, useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import './StudentLayout.css'

function StudentLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem('messmetrics-theme') === 'dark')
  const navigate = useNavigate()

  useEffect(() => {
    document.documentElement.dataset.theme = darkMode ? 'dark' : 'light'
    localStorage.setItem('messmetrics-theme', darkMode ? 'dark' : 'light')
  }, [darkMode])

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
          <button
            className="theme-toggle"
            type="button"
            onClick={() => setDarkMode(mode => !mode)}
            aria-label={`Switch to ${darkMode ? 'light' : 'dark'} mode`}
            title={`Switch to ${darkMode ? 'light' : 'dark'} mode`}
          >
            {darkMode ? '☀ Light mode' : '☾ Dark mode'}
          </button>
        </header>

        <main className="student-content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default StudentLayout
