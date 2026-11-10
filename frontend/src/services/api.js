
const API_URL = import.meta.env.VITE_API_URL

export async function getHostels() {
    const response = await fetch(`${API_URL}/hostels`)

    if (!response.ok) {
        throw new Error("Failed to fetch hostels")
    }

    return response.json()
}

export async function registerStudent(studentData) {
    const response = await fetch(`${API_URL}/auth/register/student`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(studentData)
    })

    const data = await response.json()

    if (!response.ok) {
        throw new Error(data.detail || "Student registration failed")
    }

    return data
}

export async function loginUser(username, password) {
    const formData = new URLSearchParams()

    formData.append('username', username)
    formData.append('password', password)

    const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData
    })

    const data = await response.json()

    if (!response.ok) {
        throw new Error(data.detail || "Login failed")
    }

    return data
}


export async function getCurrentUser() {
    const token = localStorage.getItem('access_token')

    const response = await fetch(`${API_URL}/users/me`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })

    const data = await response.json()

    if (!response.ok) {
        throw new Error(data.detail || 'Failed to fetch profile')
    }

    return data
}
