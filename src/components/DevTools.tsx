"use client"
import { Button } from "@/components/ui/button"
import { useAppStore } from "@/store/useStore"

export function DevTools() {
    const { incrementDays, daysActive, reset } = useAppStore()

    if (process.env.NODE_ENV === 'production') return null

    return (
        <div className="fixed bottom-4 right-4 p-2 bg-card border rounded-lg shadow-lg text-xs space-y-2 z-50">
            <p className="font-bold">DevControls (Days: {daysActive})</p>
            <div className="flex gap-2">
                <Button size="sm" variant="outline" onClick={incrementDays}>+1 Day</Button>
                <Button size="sm" variant="destructive" onClick={reset}>Reset App</Button>
            </div>
        </div>
    )
}
