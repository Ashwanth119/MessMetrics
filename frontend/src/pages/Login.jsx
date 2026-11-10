
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { loginUser } from '../services/api'

function Login() {
  const navigate = useNavigate()

  const [formData, setFormData] = useState({
    username: '',
    password: ''
  })

  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  function handleChange(e) {
    const { name, value } = e.target

    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    try {
      setIsSubmitting(true)

      const data = await loginUser(
        formData.username.trim(),
        formData.password
      )

      localStorage.setItem('access_token', data.access_token)

      navigate('/dashboard')
    } catch (error) {
      setError(error.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="register-page">
      <div className="register-container">
        <h1>Login</h1>
        <p>Welcome back to MessMetrics</p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username or Email *</label>
            <input
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Enter username or email"
              required
            />
          </div>

          <div className="form-group">
            <label>Password *</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter your password"
              required
            />
          </div>

          {error && <p className="form-error">{error}</p>}

          <button
            type="submit"
            className="register-button"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <p>
          Don't have an account?{' '}
          <a href="/register">Register here</a>
        </p>
      </div>
    </div>
  )
}

export default Login
