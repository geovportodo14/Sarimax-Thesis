import { Lock } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function LockedBudgetCard() {
    return (
        <Card className="opacity-75 border-dashed relative overflow-hidden">
            <div className="absolute inset-0 bg-background/50 backdrop-blur-[1px] flex flex-col items-center justify-center z-10">
                <div className="bg-muted p-3 rounded-full mb-2">
                    <Lock className="h-6 w-6 text-muted-foreground" />
                </div>
                <p className="font-medium text-sm text-muted-foreground">Budget Locked</p>
            </div>
            <CardHeader>
                <CardTitle className="text-muted-foreground">Monthly Budget</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-24 w-full bg-muted/20 rounded-md animate-pulse" />
            </CardContent>
        </Card>
    )
}
