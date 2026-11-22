
import { createContext, useContext, useState } from 'react'

const SelectedDateContext = createContext(null)

function getTodayIST() {
    return new Intl.DateTimeFormat('en-CA', {
        timeZone: 'Asia/Kolkata',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    }).format(new Date())
}

export function SelectedDateProvider({ children }) {
    const [selectedDate, setSelectedDate] = useState(getTodayIST)

    return (
        <SelectedDateContext.Provider value={{ selectedDate, setSelectedDate }}>
            {children}
        </SelectedDateContext.Provider>
    )
}

export function useSelectedDate() {
    const context = useContext(SelectedDateContext)

    if (!context) {
        throw new Error('useSelectedDate must be used within SelectedDateProvider')
    }

    return context
}
