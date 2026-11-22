import { useEffect, useState } from "react";
import {
    getMyProfile,
    updateMyProfile,
    getHostels
} from "../services/api";

const initialForm = {
    username: "",
    full_name: "",
    hostel_id: "",
    room_number: "",
    date_of_birth: "",
    height_cm: "",
    weight_kg: "",
    sex: "",
    activity_level: ""
};

function Profile() {
    const [profile, setProfile] = useState(null);
    const [hostels, setHostels] = useState([]);
    const [form, setForm] = useState(initialForm);

    const [isEditing, setIsEditing] = useState(false);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    useEffect(() => {
        loadProfile();
        loadHostels();
    }, []);

    async function loadProfile() {
        try {
            const data = await getMyProfile();
            setProfile(data);
        } catch (err) {
            setError(err.message || "Failed to load profile.");
        } finally {
            setLoading(false);
        }
    }

    async function loadHostels() {
        try {
            const data = await getHostels();
            setHostels(data);
        } catch (err) {
            setError(err.message || "Failed to load hostels.");
        }
    }

    function populateForm(data) {
        setForm({
            username: data.username ?? "",
            full_name: data.full_name ?? "",
            hostel_id: String(data.hostel_id ?? ""),
            room_number: data.room_number ?? "",
            date_of_birth: data.date_of_birth ?? "",
            height_cm: String(data.height_cm ?? ""),
            weight_kg: String(data.weight_kg ?? ""),
            sex: data.sex ?? "",
            activity_level: data.activity_level ?? "sedentary"
        });
    }

    function handleEdit() {
        populateForm(profile);
        setError("");
        setSuccess("");
        setIsEditing(true);
    }

    function handleCancel() {
        setIsEditing(false);
        setError("");
        populateForm(profile);
    }

    function handleChange(event) {
        const { name, value } = event.target;

        setForm(prev => ({
            ...prev,
            [name]: value
        }));
    }

    async function handleSubmit(event) {
        event.preventDefault();

        if (saving) return;

        setError("");
        setSuccess("");

        if (!form.hostel_id) {
            setError("Please select a hostel.");
            return;
        }

        setSaving(true);

        try {
            const payload = {
                username: form.username.trim(),
                full_name: form.full_name.trim(),
                hostel_id: Number(form.hostel_id),
                room_number: form.room_number.trim(),
                date_of_birth: form.date_of_birth,
                height_cm: Number(form.height_cm),
                weight_kg: Number(form.weight_kg),
                sex: form.sex,
                activity_level: form.activity_level
            };

            const updatedProfile = await updateMyProfile(payload);

            setProfile(updatedProfile);
            setIsEditing(false);
            setSuccess("Profile updated successfully.");
        } catch (err) {
            setError(err.message || "Failed to update profile.");
        } finally {
            setSaving(false);
        }
    }

    if (loading) {
        return <p>Loading profile...</p>;
    }

    if (!profile) {
        return <p className="form-error">{error || "Unable to load profile."}</p>;
    }

    return (
        <div>
            <div className="page-heading">
                <h1>My Profile</h1>
                <p>View and manage your personal information.</p>
            </div>

            {error && <p className="form-error">{error}</p>}
            {success && <p className="form-success">{success}</p>}

            {!isEditing ? (
                <div className="profile-card">
                    <div className="profile-header">
                        <div className="profile-avatar">
                            {profile.username.charAt(0).toUpperCase()}
                        </div>

                        <div>
                            <h2>{profile.username}</h2>
                            <p>Student Account</p>
                        </div>
                    </div>

                    <div className="profile-details">
                        <div className="profile-field">
                            <label>Username</label>
                            <p>{profile.username}</p>
                        </div>

                        <div className="profile-field">
                            <label>Full Name</label>
                            <p>{profile.full_name}</p>
                        </div>

                        <div className="profile-field">
                            <label>Email</label>
                            <p>{profile.email}</p>
                        </div>

                        <div className="profile-field">
                            <label>Roll Number</label>
                            <p>{profile.roll_number}</p>
                        </div>

                        <div className="profile-field">
                            <label>Hostel</label>
                            <p>{profile.hostel_number} - {profile.hostel_name}</p>
                        </div>

                        <div className="profile-field">
                            <label>Room Number</label>
                            <p>{profile.room_number}</p>
                        </div>

                        <div className="profile-field">
                            <label>Date of Birth</label>
                            <p>{profile.date_of_birth || "Not provided"}</p>
                        </div>

                        <div className="profile-field">
                            <label>Height</label>
                            <p>{profile.height_cm} cm</p>
                        </div>

                        <div className="profile-field">
                            <label>Weight</label>
                            <p>{profile.weight_kg} kg</p>
                        </div>

                        <div className="profile-field">
                            <label>Sex</label>
                            <p>{profile.sex}</p>
                        </div>

                        <div className="profile-field">
                            <label>Activity Level</label>
                            <p>{profile.activity_level.replaceAll("_", " ")}</p>
                        </div>

                        <div className="profile-field">
                            <label>Account Status</label>
                            <p>{profile.is_active ? "Active" : "Inactive"}</p>
                        </div>

                        <div className="profile-field">
                            <label>Joined On</label>
                            <p>{new Date(profile.created_at).toLocaleDateString()}</p>
                        </div>
                    </div>

                    <div className="profile-actions">
                        <button type="button" onClick={handleEdit}>
                            Edit Profile
                        </button>
                    </div>
                </div>
            ) : (
                <div className="profile-card">
                    <div className="profile-header">
                        <div>
                            <h2>Edit Profile</h2>
                            <p>Update your personal information.</p>
                        </div>
                    </div>

                    <form onSubmit={handleSubmit}>
                        <div className="profile-details">
                            <div className="profile-field">
                                <label>Username</label>
                                <input
                                    name="username"
                                    value={form.username}
                                    onChange={handleChange}
                                    required
                                />
                            </div>

                            <div className="profile-field">
                                <label>Full Name</label>
                                <input
                                    name="full_name"
                                    value={form.full_name}
                                    onChange={handleChange}
                                    required
                                />
                            </div>

                            <div className="profile-field">
                                <label>Email</label>
                                <p>{profile.email}</p>
                            </div>

                            <div className="profile-field">
                                <label>Roll Number</label>
                                <p>{profile.roll_number}</p>
                            </div>

                            <div className="profile-field">
                                <label>Hostel</label>
                                <select
                                    name="hostel_id"
                                    value={form.hostel_id}
                                    onChange={handleChange}
                                    required
                                >
                                    <option value="">Select Hostel</option>
                                    {hostels.map(hostel => (
                                        <option key={hostel.id} value={hostel.id}>
                                            {hostel.hostel_number} - {hostel.name}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div className="profile-field">
                                <label>Room Number</label>
                                <input
                                    name="room_number"
                                    value={form.room_number}
                                    onChange={handleChange}
                                    required
                                />
                            </div>

                            <div className="profile-field">
                                <label>Date of Birth</label>
                                <input
                                    type="date"
                                    name="date_of_birth"
                                    value={form.date_of_birth}
                                    onChange={handleChange}
                                    required
                                />
                            </div>

                            <div className="profile-field">
                                <label>Height (cm)</label>
                                <input
                                    type="number"
                                    name="height_cm"
                                    value={form.height_cm}
                                    onChange={handleChange}
                                    min="1"
                                    step="0.1"
                                    required
                                />
                            </div>

                            <div className="profile-field">
                                <label>Weight (kg)</label>
                                <input
                                    type="number"
                                    name="weight_kg"
                                    value={form.weight_kg}
                                    onChange={handleChange}
                                    min="1"
                                    step="0.1"
                                    required
                                />
                            </div>

                            <div className="profile-field">
                                <label>Sex</label>
                                <select
                                    name="sex"
                                    value={form.sex}
                                    onChange={handleChange}
                                    required
                                >
                                    <option value="">Select</option>
                                    <option value="male">Male</option>
                                    <option value="female">Female</option>
                                </select>
                            </div>

                            <div className="profile-field">
                                <label>Activity Level</label>
                                <select
                                    name="activity_level"
                                    value={form.activity_level}
                                    onChange={handleChange}
                                    required
                                >
                                    <option value="sedentary">Sedentary</option>
                                    <option value="light">Light</option>
                                    <option value="moderate">Moderate</option>
                                    <option value="very_active">Very Active</option>
                                    <option value="extra_active">Extra Active</option>
                                </select>
                            </div>

                            <div className="profile-field">
                                <label>Account Status</label>
                                <p>{profile.is_active ? "Active" : "Inactive"}</p>
                            </div>

                            <div className="profile-field">
                                <label>Joined On</label>
                                <p>{new Date(profile.created_at).toLocaleDateString()}</p>
                            </div>
                        </div>

                        <div className="profile-actions">
                            <button type="submit" disabled={saving}>
                                {saving ? "Saving..." : "Save Changes"}
                            </button>

                            <button
                                type="button"
                                onClick={handleCancel}
                                disabled={saving}
                            >
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            )}
        </div>
    );
}

export default Profile;
