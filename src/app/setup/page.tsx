import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"

export default function SetupPage() {
    return (
        <Card>
            <CardHeader>
                <CardTitle>Welcome to EnergySim Dashboard</CardTitle>
                <CardDescription>
                    Get control of your energy budget with real-time monitoring and AI forecasts.
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="space-y-2 text-sm text-muted-foreground">
                    <p>We'll guide you through a quick 3-step setup:</p>
                    <ul className="list-disc pl-5 space-y-1">
                        <li>Set your electricity rate</li>
                        <li>Connect your smart plug</li>
                        <li>Verify data connection</li>
                    </ul>
                </div>
            </CardContent>
            <CardFooter>
                <Link href="/setup/tariff" className="w-full">
                    <Button className="w-full">Get Started</Button>
                </Link>
            </CardFooter>
        </Card>
    )
}
