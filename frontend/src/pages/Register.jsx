
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getHostels, registerStudent } from '../services/api'

function Register() {
  const navigate = useNavigate()

  const [formData, setFormData] = useState({
    username: '',
    full_name: '',
    roll_number: '',
    email: '',
    password: '',
    confirm_password: '',
    hostel: '',
    room_number: '',
    date_of_birth: '',
    height_cm: '',
    weight_kg: '',
    sex: ''
  })

  const [hostels, setHostels] = useState([])
  const [hostelError, setHostelError] = useState('')
  const [hostelLoadAttempt, setHostelLoadAttempt] = useState(0)
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    async function fetchHostels() {
      setHostelError('')
      try {
        const data = await getHostels()
        setHostels(data)
      } catch (error) {
        setHostelError(`Unable to load hostels: ${error.message}`)
      }
    }

    fetchHostels()
  }, [hostelLoadAttempt])

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

    if (formData.password !== formData.confirm_password) {
      setError('Passwords do not match')
      return
    }

    if (!formData.hostel) {
      setError('Please select your hostel')
      return
    }

    const studentData = {
      username: formData.username.trim(),
      email: formData.email.trim(),
      password: formData.password,
      full_name: formData.full_name.trim(),
      roll_number: formData.roll_number.trim(),
      hostel_number: formData.hostel.toUpperCase(),
      room_number: formData.room_number.trim(),
      date_of_birth: formData.date_of_birth || null,
      height_cm: formData.height_cm ? Number(formData.height_cm) : null,
      weight_kg: formData.weight_kg ? Number(formData.weight_kg) : null,
      sex: formData.sex || null
    }

    try {
      setIsSubmitting(true)
      await registerStudent(studentData)
      navigate('/login')
    } catch (error) {
      setError(error.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="register-page">
      <div className="register-container">
        <h1>Student Registration</h1>
        <p>Create your MessMetrics account</p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username *</label>
            <input
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Choose a username"
              minLength="3"
              maxLength="50"
              required
            />
          </div>

          <div className="form-group">
            <label>Full Name *</label>
            <input
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              placeholder="Enter your full name"
              required
            />
          </div>

          <div className="form-group">
            <label>Roll Number *</label>
            <input
              name="roll_number"
              value={formData.roll_number}
              onChange={handleChange}
              placeholder="Enter your roll number"
              required
            />
          </div>

          <div className="form-group">
            <label>Email *</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter your email"
              required
            />
          </div>

          <div className="form-group">
            <label>Hostel Number *</label>
            <select
              name="hostel"
              value={formData.hostel}
              onChange={handleChange}
              required
            >
              <option value="">Select your hostel</option>
              {hostels.map(hostel => (
                <option key={hostel.id} value={hostel.hostel_number}>
                  {hostel.name}
                </option>
              ))}
            </select>
            {hostelError && <p className="form-error">{hostelError}</p>}
            {hostelError && (
              <button
                type="button"
                className="secondary-button"
                onClick={() => setHostelLoadAttempt(attempt => attempt + 1)}
              >
                Retry loading hostels
              </button>
            )}
          </div>

          <div className="form-group">
            <label>Room Number *</label>
            <input
              name="room_number"
              value={formData.room_number}
              onChange={handleChange}
              placeholder="Enter your room number"
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
              placeholder="Create a password"
              minLength="8"
              maxLength="128"
              required
            />
          </div>

          <div className="form-group">
            <label>Confirm Password *</label>
            <input
              type="password"
              name="confirm_password"
              value={formData.confirm_password}
              onChange={handleChange}
              placeholder="Re-enter your password"
              required
            />
          </div>

          <div className="form-group">
            <label>Date of Birth *</label>
            <input
              type="date"
              name="date_of_birth"
              value={formData.date_of_birth}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Height (cm) *</label>
            <input
              type="number"
              name="height_cm"
              value={formData.height_cm}
              onChange={handleChange}
              placeholder="Enter height"
              min="1"
              required
            />
          </div>

          <div className="form-group">
            <label>Weight (kg) *</label>
            <input
              type="number"
              name="weight_kg"
              value={formData.weight_kg}
              onChange={handleChange}
              placeholder="Enter weight"
              min="1"
              step="0.1"
              required
            />
          </div>

          <div className="form-group">
            <label>Sex *</label>
            <select name="sex" value={formData.sex} onChange={handleChange} required>
              <option value="">Select</option>
              <option value="female">Female</option>
              <option value="male">Male</option>
            </select>
          </div>

          {error && <p className="form-error">{error}</p>}

          <button
            type="submit"
            className="register-button"
            disabled={isSubmitting || hostels.length === 0}
          >
            {isSubmitting ? 'Registering...' : 'Register'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Register
