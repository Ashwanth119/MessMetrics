
import { useEffect, useState } from 'react'
import { getMyCalories } from '../services/api'
import { useSelectedDate } from '../context/SelectedDateContext'

const nutrients = [
  ['calories', 'Calories', 'kcal'],
  ['protein_g', 'Protein', 'g'],
  ['carbohydrates_total_g', 'Carbohydrates', 'g'],
  ['sugar_g', 'Sugar', 'g'],
  ['fiber_g', 'Fiber', 'g'],
  ['fat_total_g', 'Total fat', 'g'],
  ['fat_saturated_g', 'Saturated fat', 'g'],
  ['cholesterol_mg', 'Cholesterol', 'mg'],
  ['sodium_mg', 'Sodium', 'mg'],
  ['potassium_mg', 'Potassium', 'mg']
]

const meals = [
  ['BREAKFAST', 'Breakfast'],
  ['LUNCH', 'Lunch'],
  ['SNACKS', 'Snacks'],
  ['DINNER', 'Dinner']
]

function formatAmount(value, unit) {
  const amount = Number(value || 0)
  return `${unit === 'mg' ? Math.round(amount) : Math.round(amount * 10) / 10} ${unit}`
}

function Nutrition() {
  const { selectedDate, setSelectedDate } = useSelectedDate()

  const [summary, setSummary] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let ignore = false
    setLoading(true)
    setError('')

    getMyCalories(selectedDate)
      .then(data => {
        if (!ignore) setSummary(data)
      })
      .catch(err => {
        if (!ignore) setError(err.message || 'Could not load nutrition totals.')
      })
      .finally(() => {
        if (!ignore) setLoading(false)
      })

    return () => { ignore = true }
  }, [selectedDate])

  return (
    <div className="nutrition-page">
      <div className="page-heading nutrition-heading">
        <div>
          <h1>Nutrition</h1>
          <p>Cumulative nutrition from the foods and gram amounts you logged, split by meal.</p>
        </div>
        <label>
          Date
          <input
            type="date"
            value={selectedDate}
            onChange={event => setSelectedDate(event.target.value)}
          />
        </label>
      </div>

      <section className="nutrition-card">
        {loading ? <p>Loading nutrition totals...</p> : error ? <p className="form-error">{error}</p> : (
          <div className="nutrition-table-wrap">
            <table className="nutrition-breakdown-table">
              <thead>
                <tr>
                  <th>Nutrient</th>
                  {meals.map(([, label]) => <th key={label}>{label}</th>)}
                  <th>Daily total</th>
                </tr>
              </thead>
              <tbody>
                {nutrients.map(([key, label, unit]) => (
                  <tr key={key}>
                    <th scope="row">{label}</th>
                    {meals.map(([mealType]) => (
                      <td key={mealType}>{formatAmount(summary?.meal_totals?.[mealType]?.[key], unit)}</td>
                    ))}
                    <td className="nutrition-daily-total">{formatAmount(summary?.daily_totals?.[key], unit)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}

export default Nutrition
