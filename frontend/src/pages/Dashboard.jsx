import { useEffect, useState } from "react"
import {
    getMyMenu,
    getMyMealLogs,
    saveMealLog,
    getMyCalories
} from "../services/api"
import "./Dashboard.css"

const getToday = () => {
    const date = new Date()
    date.setMinutes(date.getMinutes() - date.getTimezoneOffset())
    return date.toISOString().split("T")[0]
}

const mealNames = {
    BREAKFAST: "Breakfast",
    LUNCH: "Lunch",
    SNACKS: "Snacks",
    DINNER: "Dinner"
}

const nutritionFields = [
    ["calories", "Calories", "kcal"],
    ["protein_g", "Protein", "g"],
    ["carbohydrates_total_g", "Carbohydrates", "g"],
    ["sugar_g", "Sugar", "g"],
    ["fiber_g", "Fiber", "g"],
    ["fat_total_g", "Total fat", "g"],
    ["fat_saturated_g", "Saturated fat", "g"],
    ["cholesterol_mg", "Cholesterol", "mg"],
    ["sodium_mg", "Sodium", "mg"],
    ["potassium_mg", "Potassium", "mg"]
]

function Dashboard() {
    const [menuDate, setMenuDate] = useState(getToday())
    const [menu, setMenu] = useState(null)
    const [mealLogs, setMealLogs] = useState([])
    const [calories, setCalories] = useState({})
    const [selections, setSelections] = useState({})
    const [grams, setGrams] = useState({})
    const [expandedMeal, setExpandedMeal] = useState(null)
    const [loading, setLoading] = useState(true)
    const [savingMeal, setSavingMeal] = useState(null)
    const [error, setError] = useState("")
    const [message, setMessage] = useState("")

    useEffect(() => {
        async function loadDashboard() {
            setLoading(true)
            setError("")
            setMessage("")

            try {
                const [menuData, logsData, calorieData] = await Promise.all([
                    getMyMenu(menuDate),
                    getMyMealLogs(menuDate),
                    getMyCalories(menuDate)
                ])

                setMenu(menuData)
                setMealLogs(logsData)
                setCalories(calorieData.meal_totals || {})

                const selected = {}
                const quantities = {}
                const menuItemsById = new Map(
                    menuData.meals.flatMap(meal => meal.items).map(item => [item.menu_id, item])
                )

                logsData.forEach(log => {
                    selected[log.meal_type] = log.items
                        .filter(item => item.mess_menu_id !== null)
                        .map(item => item.mess_menu_id)

                    log.items.forEach(item => {
                        if (item.mess_menu_id !== null) {
                            const menuItem = menuItemsById.get(item.mess_menu_id)
                            const referenceGrams = menuItem?.nutrition?.serving_size_g || 100
                            quantities[item.mess_menu_id] = String(Math.round(item.servings_consumed * referenceGrams))
                        }
                    })
                })

                setSelections(selected)
                setGrams(quantities)
                setExpandedMeal(null)
            } catch (err) {
                setError(err.message || "Failed to load dashboard")
            } finally {
                setLoading(false)
            }
        }

        loadDashboard()
    }, [menuDate])

    const toggleItem = (mealType, menuId, checked) => {
        setSelections(previous => {
            const current = previous[mealType] || []

            return {
                ...previous,
                [mealType]: checked
                    ? [...current, menuId]
                    : current.filter(id => id !== menuId)
            }
        })

        if (checked) {
            setGrams(previous => ({
                ...previous,
                [menuId]: previous[menuId] || "100"
            }))
        }
    }

    const updateGrams = (menuId, value) => {
        setGrams(previous => ({
            ...previous,
            [menuId]: value
        }))
    }

    const saveMeal = async meal => {
        const mealType = meal.meal_type
        const selectedIds = selections[mealType] || []

        const mealItemsById = new Map(meal.items.map(item => [item.menu_id, item]))
        const items = selectedIds.map(menuId => {
            const item = mealItemsById.get(menuId)
            const referenceGrams = item?.nutrition?.serving_size_g || 100
            return {
                mess_menu_id: menuId,
                servings_consumed: Number(grams[menuId]) / referenceGrams
            }
        })

        if (items.some(item => !Number.isFinite(item.servings_consumed) || item.servings_consumed <= 0)) {
            setError("Enter a valid amount in grams greater than zero.")
            return
        }

        setSavingMeal(mealType)
        setError("")
        setMessage("")

        try {
            const savedLog = await saveMealLog({
                log_date: menuDate,
                meal_type: mealType,
                items
            })

            setMealLogs(previous => [
                ...previous.filter(log => log.meal_type !== mealType),
                savedLog
            ])

            const calorieData = await getMyCalories(menuDate)
            setCalories(calorieData.meal_totals || {})
            setMessage(`${mealNames[mealType]} saved successfully.`)
            setExpandedMeal(null)
        } catch (err) {
            setError(err.message || "Failed to save meal")
        } finally {
            setSavingMeal(null)
        }
    }

    const isMealLogged = mealType =>
        mealLogs.some(log => log.meal_type === mealType)

    if (loading) {
        return <div className="dashboard-page"><p>Loading dashboard...</p></div>
    }

    return (
        <div className="dashboard-page">
            <div className="page-heading">
                <h1>Dashboard</h1>
                <p>Welcome to MessMetrics!</p>
            </div>

            <div className="dashboard-grid">
                <div className="dashboard-card menu-dashboard-card">
                    <div className="menu-card-heading">
                        <div>
                            <h2>Today's Menu</h2>
                            <p>View your menu and log your meals.</p>
                        </div>

                        <input
                            type="date"
                            value={menuDate}
                            onChange={event => setMenuDate(event.target.value)}
                        />
                    </div>

                    {menu && (
                        <p className="menu-hostel">
                            {menu.hostel} · {menu.mess}
                        </p>
                    )}

                    {error && <p className="menu-error">{error}</p>}
                    {message && <p className="menu-success">{message}</p>}

                    {!menu?.meals?.length ? (
                        <p className="empty-menu">No menu available for this date.</p>
                    ) : (
                        <div className="dashboard-meals">
                            {menu.meals.map(meal => {
                                const mealType = meal.meal_type
                                const isExpanded = expandedMeal === mealType
                                const selectedIds = selections[mealType] || []
                                const logged = isMealLogged(mealType)
                                const mealCalories = calories[mealType]?.calories

                                return (
                                    <div className="dashboard-meal" key={mealType}>
                                        <div className="dashboard-meal-heading">
                                            <h3>{mealNames[mealType] || mealType}</h3>
                                            <span className={logged ? "meal-status logged" : "meal-status"}>
                                                {logged ? "Logged" : "Not logged"}
                                            </span>
                                        </div>

                                        {!isExpanded ? (
                                            <>
                                                {meal.items.length === 0 ? (
                                                    <p className="empty-menu">No items available.</p>
                                                ) : (
                                                    <>
                                                        <ul>
                                                            {meal.items.slice(0, 3).map(item => (
                                                                <li key={item.menu_id}>
                                                                    <span>{item.name}</span>
                                                                    <span className="serving-info">
                                                                        {item.serving_quantity
                                                                            ? `${item.serving_quantity} ${item.serving_unit || ""}`
                                                                            : ""}
                                                                    </span>
                                                                </li>
                                                            ))}
                                                        </ul>

                                                        {meal.items.length > 3 && (
                                                            <p className="more-items">
                                                                + {meal.items.length - 3} more items
                                                            </p>
                                                        )}
                                                    </>
                                                )}

                                                {logged && mealCalories != null && (
                                                    <p className="meal-calories">
                                                        {Math.round(mealCalories)} kcal consumed
                                                    </p>
                                                )}

                                                <button
                                                    className="meal-action-button"
                                                    onClick={() => {
                                                        setMessage("")
                                                        setExpandedMeal(mealType)
                                                    }}
                                                >
                                                    {logged ? "Edit meal" : "View menu & Log meal"}
                                                </button>
                                            </>
                                        ) : (
                                            <>
                                                <div className="meal-selection-list">
                                                    {meal.items.map(item => {
                                                        const checked = selectedIds.includes(item.menu_id)

                                                        return (
                                                            <div className="meal-selection-item" key={item.menu_id}>
                                                                <label className="meal-checkbox-label">
                                                                    <input
                                                                        type="checkbox"
                                                                        checked={checked}
                                                                        onChange={event =>
                                                                            toggleItem(
                                                                                mealType,
                                                                                item.menu_id,
                                                                                event.target.checked
                                                                            )
                                                                        }
                                                                    />
                                                                    <span>{item.name}</span>
                                                                </label>

                                                                {checked && (
                                                                    <div className="servings-input-label">
                                                                      <label htmlFor={`grams-${item.menu_id}`}>Amount (g)</label>
                                                                      <input
                                                                          id={`grams-${item.menu_id}`}
                                                                          className="grams-input"
                                                                          type="number"
                                                                          min="1"
                                                                          step="1"
                                                                          value={grams[item.menu_id] || "100"}
                                                                          onChange={event => updateGrams(item.menu_id, event.target.value)}
                                                                      />
                                                                      {item.nutrition?.calories != null && (
                                                                          <span className="grams-calories-estimate">
                                                                              ≈ {Math.round(item.nutrition.calories * Number(grams[item.menu_id] || 100) / (item.nutrition.serving_size_g || 100))} kcal
                                                                          </span>
                                                                      )}
                                                                      <details className="grams-nutrition-estimate">
                                                                          <summary>Nutrition for this amount</summary>
                                                                          <dl>
                                                                              {nutritionFields.map(([key, label, unit]) => {
                                                                                  const value = item.nutrition?.[key]
                                                                                  if (value == null) return null
                                                                                  const amount = Number(grams[item.menu_id] || 100)
                                                                                  const reference = item.nutrition?.serving_size_g || 100
                                                                                  const scaledValue = value * amount / reference
                                                                                  return (
                                                                                      <div key={key}>
                                                                                          <dt>{label}</dt>
                                                                                          <dd>{unit === 'mg' ? Math.round(scaledValue) : Math.round(scaledValue * 10) / 10} {unit}</dd>
                                                                                      </div>
                                                                                  )
                                                                              })}
                                                                          </dl>
                                                                      </details>
                                                                      <div className="servings-controls">
                                                                          <button
                                                                              type="button"
                                                                              onClick={() =>
                                                                                  updateGrams(
                                                                                      item.menu_id,
                                                                                      String(Math.max(1, Number(grams[item.menu_id] || 100) - 1))
                                                                                  )
                                                                              }
                                                                          >
                                                                              −
                                                                          </button>

                                                                          <span>{grams[item.menu_id] || "100"}</span>

                                                                          <button
                                                                              type="button"
                                                                              onClick={() =>
                                                                                  updateGrams(
                                                                                      item.menu_id,
                                                                                      String(Number(grams[item.menu_id] || 100) + 1)
                                                                                  )
                                                                              }
                                                                          >
                                                                              +
                                                                          </button>
                                                                      </div>
                                                                  </div>
                                                                )}
                                                            </div>
                                                        )
                                                    })}
                                                </div>

                                                <p className="selected-count">
                                                    {selectedIds.length} item(s) selected
                                                </p>

                                                <div className="meal-actions">
                                                    <button
                                                        className="meal-save-button"
                                                        onClick={() => saveMeal(meal)}
                                                        disabled={savingMeal === mealType}
                                                    >
                                                        {savingMeal === mealType
                                                            ? "Saving..."
                                                            : "Save meal"}
                                                    </button>

                                                    <button
                                                        className="meal-cancel-button"
                                                        onClick={() => setExpandedMeal(null)}
                                                        disabled={savingMeal === mealType}
                                                    >
                                                        Cancel
                                                    </button>
                                                </div>
                                            </>
                                        )}
                                    </div>
                                )
                            })}
                        </div>
                    )}
                </div>

                <div className="dashboard-card">
                    <h3>Calories</h3>
                    <p>Track your daily calorie intake.</p>
                </div>

                <div className="dashboard-card">
                    <h3>Nutrition</h3>
                    <p>View your nutritional information.</p>
                </div>
            </div>
        </div>
    )
}

export default Dashboard
