"use client"

import { useState } from "react"
import { useAppStore } from "@/store/useStore"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { UsageChart } from "@/components/dashboard/UsageChart"
import { generateMockData } from "@/lib/mockData"

export default function ScenariosPage() {
    const { tariff } = useAppStore()

    // Scenario State
    const [acTemp, setAcTemp] = useState(24)
    const [usageHours, setUsageHours] = useState(8)
    const [scenarioTariff, setScenarioTariff] = useState(tariff || 12)

    // Simulation Logic (Simplified for Demo)
    // Base cost = ~150 kWh/mo * tariff
    const baseKwh = 150
    const baseCost = baseKwh * (tariff || 12)

    // Adjustments
    // +1C temp = -5% energy (Rule of thumb)
    const tempDiff = acTemp - 24
    const tempFactor = 1 - (tempDiff * 0.05)

    // +1h usage = +12.5% energy (if 8h is baseline)
    const usageDiff = usageHours - 8
    const usageFactor = 1 + (usageDiff * 0.125)

    const simulatedKwh = baseKwh * tempFactor * usageFactor
    const simulatedCost = simulatedKwh * scenarioTariff

    const savings = baseCost - simulatedCost
    const isSaving = savings > 0

    // Chart Data for Simulation
    // We'll overlay "Base" vs "Simulated"
    const chartData = generateMockData(7).map(d => ({
        ...d,
        // Add simulated series (just scaling for visual effect)
        simulated: (d.forecast || 0) * tempFactor * usageFactor
    }))

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Scenario Simulator</h1>
                <p className="text-muted-foreground">
                    Explore how changes in usage patterns affect your monthly bill.
                </p>
            </div>

            <div className="grid gap-6 md:grid-cols-12">
                {/* Controls Column */}
                <div className="md:col-span-4 space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Adjust Variables</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            {/* AC Temp Slider */}
                            <div className="space-y-3">
                                <div className="flex justify-between">
                                    <Label>AC Temperature</Label>
                                    <span className="font-bold">{acTemp}°C</span>
                                </div>
                                <Slider
                                    value={[acTemp]}
                                    min={18}
                                    max={30}
                                    step={1}
                                    onValueChange={(val) => setAcTemp(val[0])}
                                />
                                <p className="text-xs text-muted-foreground">Higher temp = lower energy.</p>
                            </div>

                            {/* Usage Hours Slider */}
                            <div className="space-y-3">
                                <div className="flex justify-between">
                                    <Label>Daily Defined Usage</Label>
                                    <span className="font-bold">{usageHours} hrs</span>
                                </div>
                                <Slider
                                    value={[usageHours]}
                                    min={1}
                                    max={24}
                                    step={1}
                                    onValueChange={(val) => setUsageHours(val[0])}
                                />
                            </div>

                            {/* Tariff Input */}
                            <div className="space-y-3">
                                <Label>Electricity Rate (Optional)</Label>
                                <Input
                                    type="number"
                                    value={scenarioTariff}
                                    onChange={(e) => setScenarioTariff(Number(e.target.value))}
                                />
                            </div>

                            <Button
                                variant="outline"
                                className="w-full"
                                onClick={() => {
                                    setAcTemp(24)
                                    setUsageHours(8)
                                    setScenarioTariff(tariff || 12)
                                }}
                            >
                                Reset to Baseline
                            </Button>
                        </CardContent>
                    </Card>
                </div>

                {/* Results Column */}
                <div className="md:col-span-8 space-y-6">
                    {/* Impact Summary Cards */}
                    <div className="grid gap-4 md:grid-cols-2">
                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm font-medium text-muted-foreground">Projected Monthly Cost</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-bold">₱{simulatedCost.toFixed(2)}</div>
                                {Math.abs(savings) > 1 && (
                                    <p className={`text-sm font-medium ${isSaving ? 'text-green-600' : 'text-red-600'}`}>
                                        {isSaving ? '▼ Save' : '▲ Pay extra'} ₱{Math.abs(savings).toFixed(2)}
                                    </p>
                                )}
                            </CardContent>
                        </Card>
                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm font-medium text-muted-foreground">Projected Consumption</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-bold">{simulatedKwh.toFixed(1)} kWh</div>
                                <p className="text-xs text-muted-foreground">vs {baseKwh.toFixed(1)} kWh baseline</p>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Simulation Chart */}
                    <UsageChart
                        title="Simulation Impact Curve"
                        subtitle="Visualizing the shift in daily load profile"
                        data={chartData}
                    />
                </div>
            </div>
        </div>
    )
}
