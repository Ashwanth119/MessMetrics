
const API_URL = import.meta.env.VITE_API_URL || '/api'

async function readJsonResponse(response, fallbackMessage) {
    const responseText = await response.text()
    let data

    if (responseText) {
        try {
            data = JSON.parse(responseText)
        } catch {
            if (response.ok) {
                throw new Error('The server returned an invalid response. Please try again.')
            }
        }
    } else if (response.ok) {
        throw new Error('The server returned an empty response. Please try again.')
    }

    if (!response.ok) {
        throw new Error(data?.detail || fallbackMessage)
    }

    return data
}

export async function getHostels() {
    const response = await fetch(`${API_URL}/hostels`)

    return readJsonResponse(response, 'Failed to fetch hostels')
}

export async function registerStudent(studentData) {
    const response = await fetch(`${API_URL}/auth/register/student`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(studentData)
    })

    return readJsonResponse(response, 'Student registration failed')
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

    return readJsonResponse(response, 'Login failed')
}

export async function getCurrentUser() {
    const token = localStorage.getItem('access_token')

    const response = await fetch(`${API_URL}/users/me`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })

    return readJsonResponse(response, 'Failed to fetch profile')
}

export async function getMyProfile() {
    const response = await fetch(`${API_URL}/students/me/profile`, {
        headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`
        }
    })

    return readJsonResponse(response, "Failed to fetch student profile")
}

export async function updateMyProfile(profileData) {
    const response = await fetch(`${API_URL}/students/me/profile`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token")}`
        },
        body: JSON.stringify(profileData)
    })

    return readJsonResponse(response, "Failed to update student profile")
}

export async function getMyMenu(menuDate) {
    const token = localStorage.getItem("access_token")

    const response = await fetch(
        `${API_URL}/students/me/menu?menu_date=${menuDate}`,
        {
            headers: {
                Authorization: `Bearer ${token}`
            }
        }
    )

    if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Failed to fetch menu")
    }

    return response.json()
}

export async function getMyMealLogs(logDate) {
    const response = await fetch(
        `${API_URL}/students/me/meal-logs?log_date=${logDate}`,
        {
            headers: {
                Authorization: `Bearer ${localStorage.getItem("access_token")}`
            }
        }
    )

    if (!response.ok) {
        throw new Error("Failed to fetch meal logs")
    }

    return response.json()
}

export async function saveMealLog(data) {
    const response = await fetch(`${API_URL}/students/me/meal-logs`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token")}`
        },
        body: JSON.stringify(data)
    })

    if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Failed to save meal log")
    }

    return response.json()
}

export async function getMyCalories(logDate) {
    const response = await fetch(
        `${API_URL}/students/me/calories?log_date=${logDate}`,
        {
            headers: {
                Authorization: `Bearer ${localStorage.getItem("access_token")}`
            }
        }
    )

    if (!response.ok) {
        throw new Error("Failed to fetch calorie summary")
    }

    return response.json()
}

export async function getMyCalorieProfile() {
    const response = await fetch(`${API_URL}/students/me/calorie-profile`, {
        headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`
        }
    })

    return readJsonResponse(response, 'Failed to fetch calorie profile')
}

export async function updateMyActivityLevel(activityLevel) {
    const response = await fetch(`${API_URL}/students/me/calorie-profile`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem("access_token")}`
        },
        body: JSON.stringify({ activity_level: activityLevel })
    })

    return readJsonResponse(response, 'Failed to save activity level')
}
