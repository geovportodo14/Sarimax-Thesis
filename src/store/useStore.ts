import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AppState {
    tariff: number | null
    setTariff: (tariff: number) => void

    device: {
        id: string
        name: string
        verified: boolean
    } | null
    setDevice: (device: { id: string; name: string }) => void
    setVerified: (status: boolean) => void

    budget: number | null
    setBudget: (budget: number) => void

    // Simulation State
    daysActive: number
    incrementDays: () => void
    setDaysActive: (days: number) => void

    reset: () => void
}

export const useAppStore = create<AppState>()(
    persist(
        (set) => ({
            tariff: null,
            setTariff: (tariff) => set({ tariff }),

            device: null,
            setDevice: (device) => set({ device: { ...device, verified: false } }),
            setVerified: (status) => set((state) => ({
                device: state.device ? { ...state.device, verified: status } : null
            })),

            budget: null,
            setBudget: (budget) => set({ budget }),

            daysActive: 0,
            incrementDays: () => set((state) => ({ daysActive: state.daysActive + 1 })),
            setDaysActive: (days) => set({ daysActive: days }),

            reset: () => set({ tariff: null, device: null, budget: null, daysActive: 0 }),
        }),
        {
            name: 'energysim-storage', // unique name
        }
    )
)
