export default function SetupLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <div className="flex min-h-screen flex-col items-center justify-center p-4 bg-muted/50">
            <div className="w-full max-w-lg space-y-6">
                {/* Simple Header */}
                <div className="flex items-center justify-center gap-2 mb-8">
                    <svg className="h-8 w-8 text-primary" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" /></svg>
                    <span className="font-bold text-2xl text-foreground">EnergySim</span>
                </div>
                {children}
            </div>
        </div>
    )
}
