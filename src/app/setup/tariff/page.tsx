"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useAppStore } from "@/store/useStore"

export default function TariffPage() {
    const router = useRouter()
    const { tariff, setTariff } = useAppStore()
    const [localTariff, setLocalTariff] = useState(tariff?.toString() || "")

    const handleNext = () => {
        const val = parseFloat(localTariff)
        if (!isNaN(val) && val > 0) {
            setTariff(val)
            router.push("/setup/device")
        }
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle>Electricity Rate</CardTitle>
                <CardDescription>
                    Enter your cost per kWh (e.g., from your bill).
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="grid w-full items-center gap-1.5">
                    <Label htmlFor="tariff">Rate (PHP/kWh)</Label>
                    <Input
                        type="number"
                        id="tariff"
                        placeholder="11.50"
                        value={localTariff}
                        onChange={(e) => setLocalTariff(e.target.value)}
                        step="0.01"
                        min="0"
                    />
                </div>
            </CardContent>
            <CardFooter className="flex justify-between">
                <Link href="/setup">
                    <Button variant="ghost">Back</Button>
                </Link>
                <Button onClick={handleNext} disabled={!localTariff}>Next</Button>
            </CardFooter>
        </Card>
    )
}
