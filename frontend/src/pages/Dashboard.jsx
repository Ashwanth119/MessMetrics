function Dashboard() {
  return (
    <div>
      <div className="page-heading">
        <h1>Dashboard</h1>
        <p>Welcome to MessMetrics!</p>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h3>Today's Menu</h3>
          <p>View your hostel mess menu.</p>
        </div>

        <div className="dashboard-card">
          <h3>Calories</h3>
          <p>Track your daily calorie intake.</p>
        </div>

        <div className="dashboard-card">
          <h3>Nutrition</h3>
          <p>Understand your nutritional intake.</p>
        </div>
      </div>
    </div>
  )
}

export default Dashboard