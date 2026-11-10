import { useEffect, useState } from 'react'
import { getCurrentUser } from '../services/api'

function Profile() {
  const [user, setUser] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchProfile() {
      try {
        const data = await getCurrentUser()
        setUser(data)
      } catch (error) {
        setError(error.message)
      } finally {
        setLoading(false)
      }
    }

    fetchProfile()
  }, [])

  if (loading) {
    return <p>Loading profile...</p>
  }

  if (error) {
    return <p className="form-error">{error}</p>
  }

  return (
    <div>
      <div className="page-heading">
        <h1>My Profile</h1>
        <p>View your account information.</p>
      </div>

      <div className="profile-card">
        <div className="profile-header">
          <div className="profile-avatar">
            {user.username.charAt(0).toUpperCase()}
          </div>
          <div>
            <h2>{user.username}</h2>
            <p>Student Account</p>
          </div>
        </div>

        <div className="profile-details">
          <div className="profile-field">
            <label>User ID</label>
            <p>{user.id}</p>
          </div>

          <div className="profile-field">
            <label>Username</label>
            <p>{user.username}</p>
          </div>

          <div className="profile-field">
            <label>Email</label>
            <p>{user.email}</p>
          </div>

          <div className="profile-field">
            <label>Account Status</label>
            <p>{user.is_active ? 'Active' : 'Inactive'}</p>
          </div>

          <div className="profile-field">
            <label>Joined On</label>
            <p>{new Date(user.created_at).toLocaleDateString()}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Profile