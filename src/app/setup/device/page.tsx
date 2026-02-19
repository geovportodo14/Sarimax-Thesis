"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useAppStore } from "@/store/useStore"

export default function DevicePage() {
    const router = useRouter()
    const { device, setDevice } = useAppStore()

    const [deviceId, setDeviceId] = useState(device?.id || "")
    const [deviceName, setDeviceName] = useState(device?.name || "")

    const handleNext = () => {
        if (deviceId && deviceName) {
            setDevice({ id: deviceId, name: deviceName })
            router.push("/setup/verify")
        }
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle>Connect Device</CardTitle>
                <CardDescription>
                    Enter your Smart Plug ID or select a device.
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="grid w-full items-center gap-1.5">
                    <Label htmlFor="device-id">Device ID</Label>
                    <Input
                        id="device-id"
                        placeholder="bf..."
                        value={deviceId}
                        onChange={(e) => setDeviceId(e.target.value)}
                    />
                </div>
                <div className="grid w-full items-center gap-1.5">
                    <Label htmlFor="device-name">Device Name</Label>
                    <Input
                        id="device-name"
                        placeholder="e.g. Living Room AC"
                        value={deviceName}
                        onChange={(e) => setDeviceName(e.target.value)}
                    />
                </div>
            </CardContent>
            <CardFooter className="flex justify-between">
                <Link href="/setup/tariff">
                    <Button variant="ghost">Back</Button>
                </Link>
                <Button onClick={handleNext} disabled={!deviceId || !deviceName}>Connect</Button>
            </CardFooter>
        </Card>
    )
}
