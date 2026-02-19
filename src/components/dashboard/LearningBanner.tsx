import { Info } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

export function LearningBanner({ daysActive }: { daysActive: number }) {
    const daysLeft = 7 - daysActive

    return (
        <Alert className="bg-blue-50 border-blue-200 text-blue-900">
            <Info className="h-4 w-4 text-blue-600" />
            <AlertTitle>Learning Mode Active</AlertTitle>
            <AlertDescription>
                We are learning your usage patterns. Budget and full forecasts will unlock in {daysLeft} day{daysLeft !== 1 ? 's' : ''}.
            </AlertDescription>
        </Alert>
    )
}
