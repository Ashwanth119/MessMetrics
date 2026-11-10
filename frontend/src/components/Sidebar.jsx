import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Utensils,
  Flame,
  ChartNoAxesCombined,
  UserRound,
  X
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: "Today's Menu", path: '/menu', icon: Utensils },
  { name: 'Calorie Tracker', path: '/calories', icon: Flame },
  { name: 'Nutrition', path: '/nutrition', icon: ChartNoAxesCombined },
  { name: 'Profile', path: '/profile', icon: UserRound }
]

function Sidebar({ isOpen, onClose }) {
  return (
    <>
      <div
        className={`sidebar-overlay ${isOpen ? 'visible' : ''}`}
        onClick={onClose}
      />

      <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h2>MessMetrics</h2>
          <button className="close-sidebar" onClick={onClose}>
            <X size={22} />
          </button>
        </div>

        <nav className="sidebar-nav">
          <p className="nav-heading">MENU</p>

          {navigation.map(({ name, path, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              end={path === '/'}
              className={({ isActive }) =>
                `nav-link ${isActive ? 'active' : ''}`
              }
              onClick={onClose}
            >
              <Icon size={20} />
              <span>{name}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <span>MessMetrics</span>
          <small>Student Portal</small>
        </div>
      </aside>
    </>
  )
}

export default Sidebar