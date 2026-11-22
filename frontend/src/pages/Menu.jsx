
import { useEffect, useState } from "react"
import { getMyMenu } from "../services/api"
import { useSelectedDate } from "../context/SelectedDateContext"
import "./Menu.css"

const meals = ["BREAKFAST", "LUNCH", "SNACKS", "DINNER"]

function getTodayIST() {
    return new Intl.DateTimeFormat("en-CA", {
        timeZone: "Asia/Kolkata",
        year: "numeric",
        month: "2-digit",
        day: "2-digit"
    }).format(new Date())
}

function formatDate(date) {
    return new Date(`${date}T00:00:00`).toLocaleDateString("en-IN", {
        day: "numeric",
        month: "long",
        year: "numeric"
    })
}

function Menu() {
    const { selectedDate, setSelectedDate } = useSelectedDate()

    const [menu, setMenu] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState("")

    useEffect(() => {
        let ignore = false

        async function fetchMenu() {
            setLoading(true)
            setError("")

            try {
                const data = await getMyMenu(selectedDate)
                if (!ignore) setMenu(data)
            } catch (err) {
                if (!ignore) setError(err.message)
            } finally {
                if (!ignore) setLoading(false)
            }
        }

        fetchMenu()

        return () => {
            ignore = true
        }
    }, [selectedDate])

    function formatMeal(meal) {
        return meal.charAt(0) + meal.slice(1).toLowerCase()
    }

    function hasNutrition(nutrition) {
        return nutrition && Object.values(nutrition).some(
            value => value !== null && value !== undefined
        )
    }

    const isToday = selectedDate === getTodayIST()

    return (
        <div className="menu-page">
            <div className="page-heading">
                <div>
                    <h1>{isToday ? "Today's Menu" : `Menu for ${formatDate(selectedDate)}`}</h1>
                    <p>View your hostel mess menu and food details.</p>
                </div>

                <input
                    type="date"
                    value={selectedDate}
                    onChange={e => setSelectedDate(e.target.value)}
                    className="menu-date"
                />
            </div>

            {loading && <p>Loading menu...</p>}

            {error && <p className="menu-error">{error}</p>}

            {!loading && !error && menu && (
                <>
                    <div className="menu-info">
                        <span>{menu.hostel}</span>
                        <span>{menu.mess}</span>
                        <span>{formatDate(menu.menu_date)}</span>
                    </div>

                    <div className="meals-container">
                        {meals.map(mealType => {
                            const meal = menu.meals.find(
                                item => item.meal_type === mealType
                            )

                            return (
                                <section className="meal-section" key={mealType}>
                                    <h2>{formatMeal(mealType)}</h2>

                                    {!meal || meal.items.length === 0 ? (
                                        <p className="empty-menu">
                                            No items available.
                                        </p>
                                    ) : (
                                        <div className="food-grid">
                                            {meal.items.map(food => (
                                                <div
                                                    className="food-card"
                                                    key={food.menu_id}
                                                >
                                                    <h3>{food.name}</h3>

                                                    {food.serving_quantity != null && (
                                                        <p>
                                                            Serving: {food.serving_quantity}
                                                            {food.serving_unit
                                                                ? ` ${food.serving_unit}`
                                                                : ""}
                                                        </p>
                                                    )}

                                                    {hasNutrition(food.nutrition) ? (
                                                        <div className="food-nutrition">
                                                            {food.nutrition.calories != null && (
                                                                <span>
                                                                    {food.nutrition.calories} kcal
                                                                </span>
                                                            )}
                                                            {food.nutrition.protein_g != null && (
                                                                <span>
                                                                    Protein: {food.nutrition.protein_g} g
                                                                </span>
                                                            )}
                                                            {food.nutrition.carbohydrates_total_g != null && (
                                                                <span>
                                                                    Carbs: {food.nutrition.carbohydrates_total_g} g
                                                                </span>
                                                            )}
                                                            {food.nutrition.fat_total_g != null && (
                                                                <span>
                                                                    Fat: {food.nutrition.fat_total_g} g
                                                                </span>
                                                            )}
                                                        </div>
                                                    ) : (
                                                        <p className="nutrition-unavailable">
                                                            Nutrition data unavailable
                                                        </p>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </section>
                            )
                        })}
                    </div>
                </>
            )}
        </div>
    )
}

export default Menu
