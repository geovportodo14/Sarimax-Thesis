"use client"

import { useState, useEffect } from "react"
import { useAppStore } from "@/store/useStore"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { LockedBudgetCard } from "@/components/dashboard/LockedBudgetCard"

export default function BudgetPage() {
    const { budget, setBudget, daysActive } = useAppStore()
    const [localBudget, setLocalBudget] = useState(budget || 2000)
    const isLearning = daysActive < 7

    useEffect(() => {
        if (budget) setLocalBudget(budget)
    }, [budget])

    const handleSave = () => {
        setBudget(localBudget)
    }

    if (isLearning) {
        return (
            <div className="max-w-xl mx-auto space-y-4">
                <h1 className="text-3xl font-bold tracking-tight">Budget Settings</h1>
                <p className="text-muted-foreground p-4 bg-muted/20 rounded-lg">
                    Your budget settings are currently locked while we analyze your usage patterns.
                    Please check back in {7 - daysActive} days.
                </p>
                <LockedBudgetCard />
            </div>
        )
    }

    // Calculate some dummy ranges based on simplified assumption
    const minRecommended = 1500
    const maxRecommended = 3000

    return (
        <div className="max-w-xl mx-auto space-y-6">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Budget Settings</h1>
                <p className="text-muted-foreground">
                    Set your monthly limit to receive alerts when you're exceeding it.
                </p>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Monthly Budget Limit</CardTitle>
                    <CardDescription>
                        Recommended range: ₱{minRecommended} - ₱{maxRecommended} based on your usage
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-8">
                    <div className="flex items-center justify-between">
                        <div className="space-y-1">
                            <span className="text-2xl font-bold">₱{localBudget.toLocaleString()}</span>
                            <p className="text-xs text-muted-foreground">Target Amount</p>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <Label>Adjust Limit</Label>
                        <Slider
                            defaultValue={[localBudget]}
                            max={5000}
                            step={100}
                            onValueChange={(val) => setLocalBudget(val[0])}
                        />
                        <div className="flex justify-between text-xs text-muted-foreground">
                            <span>₱0</span>
                            <span>₱5,000+</span>
                        </div>
                    </div>

                    <div className="space-y-2">
                        <Label>Manual Entry</Label>
                        <Input
                            type="number"
                            value={localBudget}
                            onChange={(e) => setLocalBudget(Number(e.target.value))}
                        />
                    </div>
                </CardContent>
                <CardFooter className="flex justify-end gap-2">
                    <Button variant="outline" onClick={() => setLocalBudget(budget || 2000)}>Reset</Button>
                    <Button onClick={handleSave}>Save Changes</Button>
                </CardFooter>
            </Card>
        </div>
    )
}
