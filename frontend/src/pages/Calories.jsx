
import { useEffect, useState } from "react";
import {
  getMyCalories,
  getMyCalorieProfile,
  updateMyActivityLevel,
} from "../services/api";
import { useSelectedDate } from "../context/SelectedDateContext";

const activityFactors = {
  sedentary: 1.2,
  light: 1.375,
  moderate: 1.55,
  very_active: 1.725,
  extra_active: 1.9,
};

function calculateAge(dateOfBirth) {
  if (!dateOfBirth) return null;
  const birthDate = new Date(`${dateOfBirth}T00:00:00`);
  const now = new Date();
  let age = now.getFullYear() - birthDate.getFullYear();
  const birthdayPending =
    now.getMonth() < birthDate.getMonth() ||
    (now.getMonth() === birthDate.getMonth() &&
      now.getDate() < birthDate.getDate());
  if (birthdayPending) age -= 1;
  return age;
}

function Calories() {
  const { selectedDate, setSelectedDate } = useSelectedDate();

  const [dailyTotals, setDailyTotals] = useState(null);
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState("");
  const [savingActivity, setSavingActivity] = useState(false);

  useEffect(() => {
    setDailyTotals(null);
    setError("");

    getMyCalories(selectedDate)
      .then((data) => setDailyTotals(data.daily_totals || {}))
      .catch((err) =>
        setError(err.message || "Could not load calorie summary."),
      );
  }, [selectedDate]);

  useEffect(() => {
    getMyCalorieProfile()
      .then(setProfile)
      .catch((err) =>
        setError(err.message || "Could not load your registered details."),
      );
  }, []);

  async function handleActivityChange(event) {
    const activityLevel = event.target.value;
    setProfile((current) => ({ ...current, activity_level: activityLevel }));
    setSavingActivity(true);
    setError("");
    try {
      await updateMyActivityLevel(activityLevel);
    } catch (err) {
      setError(err.message || "Could not save activity level.");
    } finally {
      setSavingActivity(false);
    }
  }

  const age = profile ? calculateAge(profile.date_of_birth) : null;
  const hasDetails =
    age > 0 && profile?.height_cm && profile?.weight_kg && profile?.sex;
  const bmr = hasDetails
    ? 10 * profile.weight_kg +
      6.25 * profile.height_cm -
      5 * age +
      (profile.sex === "male" ? 5 : -161)
    : null;
  const target =
    bmr && profile?.activity_level
      ? Math.round(bmr * activityFactors[profile.activity_level])
      : null;

  return (
    <div className="calories-page">
      <div className="page-heading">
        <h1>Calorie Tracker</h1>
        <p>Track calories from the foods and gram amounts you log.</p>
      </div>

      <section className="calorie-card">
        <div className="calorie-card-heading">
          <div>
            <h2>Calories consumed</h2>
            <p>Only selected foods and their entered gram amounts count.</p>
          </div>
          <input
            aria-label="Calorie log date"
            type="date"
            value={selectedDate}
            onChange={(event) => setSelectedDate(event.target.value)}
          />
        </div>
        {error && <p className="form-error">{error}</p>}
        <p className="calorie-total">
          {dailyTotals == null
            ? "Loading..."
            : `${Math.round(dailyTotals.calories || 0)} kcal`}
        </p>
      </section>

      <section className="calorie-card">
        <h2>Daily calorie needs</h2>
        <p>
          Your age, height, weight, and sex come from your registration details.
        </p>
        {profile && (
          <div className="calorie-profile-summary">
            <span>Age: {age ?? "Add your date of birth in your profile"}</span>
            <span>
              Height:{" "}
              {profile.height_cm ? `${profile.height_cm} cm` : "Not provided"}
            </span>
            <span>
              Weight:{" "}
              {profile.weight_kg ? `${profile.weight_kg} kg` : "Not provided"}
            </span>
          </div>
        )}
        <div className="calorie-activity-field">
          <label htmlFor="activity-level">Activity level</label>
          <select
            id="activity-level"
            value={profile?.activity_level || ""}
            onChange={handleActivityChange}
            disabled={!profile || savingActivity}
          >
            <option value="">Select activity level</option>
            <option value="sedentary">Sedentary</option>
            <option value="light">Lightly active</option>
            <option value="moderate">Moderately active</option>
            <option value="very_active">Very active</option>
            <option value="extra_active">Extra active</option>
          </select>
          {savingActivity && <small>Saving...</small>}
        </div>
        {target != null && (
          <p className="calorie-target">
            Estimated maintenance: <strong>{target} kcal/day</strong>
          </p>
        )}
        {profile && !hasDetails && (
          <p className="calorie-profile-note">
            Your registered date of birth, height, weight, and sex are needed to
            calculate an estimate.
          </p>
        )}
      </section>
    </div>
  );
}

export default Calories;
