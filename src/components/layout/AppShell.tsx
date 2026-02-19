"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { LayoutDashboard, LineChart, Zap, Menu, Settings, Database } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

interface AppShellProps {
    children: React.ReactNode
}

export function AppShell({ children }: AppShellProps) {
    const pathname = usePathname()
    const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false)

    const navItems = [
        {
            title: "Monitoring",
            href: "/dashboard",
            icon: LayoutDashboard,
            active: pathname === "/dashboard",
        },
        {
            title: "Forecast",
            href: "/dashboard/forecast",
            icon: LineChart,
            active: pathname === "/dashboard/forecast",
        },
        {
            title: "Scenarios",
            href: "/dashboard/scenarios",
            icon: Zap,
            active: pathname === "/dashboard/scenarios",
        },
        { // Optional Budget or Devices as per plan, putting Budget here as primary?
            // Plan said "Budget (Range-based)". Maybe inside Forecast or separate?
            // Plan says "Budget components... Budget locked...".
            // Route map example: "Dashboard (Active) -> Budget -> Scenario".
            // So Budget is a top level route.
            title: "Budget",
            href: "/dashboard/budget",
            icon: Database, // Icon placeholder
            active: pathname === "/dashboard/budget",
        }
    ]

    return (
        <div className="flex min-h-screen flex-col bg-background">
            {/* Top Header */}
            <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
                <div className="container flex h-14 items-center justify-between">
                    {/* Logo */}
                    <div className="flex items-center gap-2 font-bold text-xl text-primary">
                        <Zap className="h-6 w-6 fill-primary" />
                        <span className="hidden sm:inline-block">EnergySim</span>
                    </div>

                    {/* Desktop Nav */}
                    <nav className="hidden md:flex items-center gap-6 text-sm font-medium">
                        {navItems.map((item) => (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={cn(
                                    "transition-colors hover:text-foreground/80",
                                    item.active ? "text-foreground" : "text-foreground/60"
                                )}
                            >
                                {item.title}
                            </Link>
                        ))}
                    </nav>

                    {/* User/Settings Actions */}
                    <div className="flex items-center gap-2">
                        <Button variant="ghost" size="icon" aria-label="Settings">
                            <Settings className="h-5 w-5" />
                        </Button>
                        {/* Mobile Menu Toggle (Drawer Trigger - placeholder) */}
                        <Button
                            variant="ghost"
                            size="icon"
                            className="md:hidden"
                            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                        >
                            <Menu className="h-5 w-5" />
                        </Button>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 container py-6 md:py-10">
                {children}
            </main>

            {/* Mobile Bottom Nav */}
            <div className="md:hidden fixed bottom-0 left-0 right-0 border-t bg-background z-40 pb-safe">
                <nav className="flex items-center justify-around h-16">
                    {navItems.map((item) => (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "flex flex-col items-center justify-center w-full h-full gap-1 text-[10px] font-medium transition-colors",
                                item.active ? "text-primary" : "text-muted-foreground hover:text-primary/50"
                            )}
                        >
                            <item.icon className="h-5 w-5" />
                            {item.title}
                        </Link>
                    ))}
                </nav>
            </div>
            {/* Spacer for bottom nav on mobile */}
            <div className="h-16 md:hidden" />
        </div>
    )
}
