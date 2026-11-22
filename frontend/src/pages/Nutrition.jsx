import { useEffect, useState } from "react";
import { getMyCalories } from "../services/api";
import { useSelectedDate } from "../context/SelectedDateContext";
import "./Nutrition.css";

const nutrients = [
  ["calories", "Calories", "kcal"],
  ["protein_g", "Protein", "g"],
  ["carbohydrates_total_g", "Carbohydrates", "g"],
  ["sugar_g", "Sugar", "g"],
  ["fiber_g", "Fiber", "g"],
  ["fat_total_g", "Total fat", "g"],
  ["fat_saturated_g", "Saturated fat", "g"],
  ["cholesterol_mg", "Cholesterol", "mg"],
  ["sodium_mg", "Sodium", "mg"],
  ["potassium_mg", "Potassium", "mg"],
];

const meals = [
  ["BREAKFAST", "Breakfast", "#f59e0b"],
  ["LUNCH", "Lunch", "#10b981"],
  ["SNACKS", "Snacks", "#8b5cf6"],
  ["DINNER", "Dinner", "#3b82f6"],
];

function formatAmount(value, unit) {
  const amount = Number(value);
  if (!Number.isFinite(amount)) {
    return `0 ${unit}`;
  }

  const precision = unit === "kcal" || unit === "mg" ? 0 : 1;
  const formatted = new Intl.NumberFormat("en-US", {
    minimumFractionDigits: 0,
    maximumFractionDigits: precision,
  }).format(amount);
  return `${formatted} ${unit}`;
}

function formatPercentage(value, total) {
  if (!total) return "0%";
  return `${Math.round((value / total) * 100)}%`;
}

function NutritionCharts({ summary, nutrientKey }) {
  const [, nutrientLabel, unit] =
    nutrients.find(([key]) => key === nutrientKey) || nutrients[0];
  const values = meals.map(([mealType, label, color]) => ({
    mealType,
    label,
    color,
    value: Number(summary?.meal_totals?.[mealType]?.[nutrientKey] || 0),
  }));
  const total = values.reduce((sum, meal) => sum + meal.value, 0);
  const maximum = Math.max(...values.map((meal) => meal.value));
  const pieSegments = values.reduce((segments, meal) => {
    const previousEnd = segments.at(-1)?.end || 0;
    const end = previousEnd + (total ? (meal.value / total) * 100 : 0);
    return [...segments, { meal, start: previousEnd, end }];
  }, []);
  const pieGradient = pieSegments
    .map(({ meal, start, end }) => `${meal.color} ${start}% ${end}%`)
    .join(", ");

  return (
    <div className="nutrition-chart-grid">
      <article className="nutrition-chart-card">
        <h3>{nutrientLabel} by meal</h3>
        <p>
          Each slice shows that meal's share of the daily{" "}
          {nutrientLabel.toLowerCase()} total.
        </p>
        {total > 0 ? (
          <div className="nutrition-pie-layout">
            <div
              className="nutrition-pie"
              style={{ background: `conic-gradient(${pieGradient})` }}
              role="img"
              aria-label={`Pie chart showing ${nutrientLabel} distribution across meals`}
            >
              <div className="nutrition-pie-center">
                <strong>{formatAmount(total, unit)}</strong>
                <span>daily total</span>
              </div>
            </div>
            <ul className="nutrition-legend">
              {values.map((meal) => (
                <li key={meal.mealType}>
                  <span>
                    <i style={{ background: meal.color }} />
                    {meal.label}
                  </span>
                  <span>
                    {formatAmount(meal.value, unit)} (
                    {formatPercentage(meal.value, total)})
                  </span>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <p className="nutrition-chart-empty">
            No logged {nutrientLabel.toLowerCase()} for this date.
          </p>
        )}
      </article>

      <article className="nutrition-chart-card">
        <h3>{nutrientLabel} bar graph</h3>
        <p>Logged amount for each meal.</p>
        <div className="nutrition-column-chart">
          {values.map((meal) => (
            <div className="nutrition-column" key={meal.mealType}>
              <span className="nutrition-column-value">
                {formatAmount(meal.value, unit)}
              </span>
              <div
                className="nutrition-column-track"
                role="img"
                aria-label={`${meal.label}: ${formatAmount(meal.value, unit)}`}
              >
                <span
                  style={{
                    height: `${maximum ? (meal.value / maximum) * 100 : 0}%`,
                    background: meal.color,
                  }}
                />
              </div>
              <strong>{meal.label}</strong>
            </div>
          ))}
        </div>
      </article>
    </div>
  );
}

function Nutrition() {
  const { selectedDate, setSelectedDate } = useSelectedDate();
  const [summary, setSummary] = useState(null);
  const [selectedNutrient, setSelectedNutrient] = useState("calories");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let ignore = false;

    getMyCalories(selectedDate)
      .then((data) => {
        if (!ignore) setSummary(data);
      })
      .catch((err) => {
        if (!ignore)
          setError(err.message || "Could not load nutrition totals.");
      })
      .finally(() => {
        if (!ignore) setLoading(false);
      });

    return () => {
      ignore = true;
    };
  }, [selectedDate]);

  function handleDateChange(date) {
    setLoading(true);
    setError("");
    setSelectedDate(date);
  }

  return (
    <div className="nutrition-page">
      <div className="page-heading nutrition-heading">
        <div>
          <h1>Nutrition</h1>
          <p>
            Cumulative nutrition from your logged foods and gram amounts, split
            by meal.
          </p>
        </div>
        <label>
          Date
          <input
            type="date"
            value={selectedDate}
            onChange={(event) => handleDateChange(event.target.value)}
          />
        </label>
      </div>

      {loading ? (
        <section className="nutrition-card">
          <p>Loading nutrition totals...</p>
        </section>
      ) : error ? (
        <section className="nutrition-card">
          <p className="form-error">{error}</p>
        </section>
      ) : (
        summary && (
          <>
            <section className="nutrition-card">
              <div className="nutrition-chart-heading">
                <h2>Daily nutrient totals</h2>
              </div>
              <div className="nutrition-table-wrap">
                <table className="nutrition-breakdown-table">
                  <thead>
                    <tr>
                      <th>Nutrient</th>
                      {meals.map(([, label]) => (
                        <th key={label}>{label}</th>
                      ))}
                      <th>Daily total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {nutrients.map(([key, label, unit]) => (
                      <tr key={key}>
                        <th scope="row">{label}</th>
                        {meals.map(([mealType]) => (
                          <td key={mealType}>
                            {formatAmount(
                              summary?.meal_totals?.[mealType]?.[key],
                              unit,
                            )}
                          </td>
                        ))}
                        <td className="nutrition-daily-total">
                          {formatAmount(summary?.daily_totals?.[key], unit)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
            <NutritionCharts summary={summary} nutrientKey={selectedNutrient} />
            <section className="nutrition-select-box">
              <label htmlFor="nutrient-select">Select nutrient</label>
              <select
                id="nutrient-select"
                value={selectedNutrient}
                onChange={(event) => setSelectedNutrient(event.target.value)}
              >
                {nutrients.map(([key, label]) => (
                  <option value={key} key={key}>
                    {label}
                  </option>
                ))}
              </select>
            </section>
          </>
        )
      )}
    </div>
  );
}

export default Nutrition;
