"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { useAppStore } from "@/store/useStore"

export default function VerifyPage() {
    const router = useRouter()
    const { setVerified } = useAppStore()
    const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying')

    useEffect(() => {
        // Simulate verification delay
        const timer = setTimeout(() => {
            setStatus('success')
            setVerified(true)
        }, 2000)

        return () => clearTimeout(timer)
    }, [setVerified])

    const handleContinue = () => {
        router.push('/dashboard')
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle>
                    {status === 'verifying' ? 'Verifying Connection...' : 'Connection Successful!'}
                </CardTitle>
                <CardDescription>
                    {status === 'verifying'
                        ? 'We are checking for recent data from your device.'
                        : 'Your device is now connected and sending data.'}
                </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col items-center py-8 space-y-4">
                {status === 'verifying' ? (
                    <>
                        <div className="h-12 w-12 rounded-full border-4 border-primary border-t-transparent animate-spin" />
                        <p className="text-sm text-muted-foreground">Waiting for data...</p>
                    </>
                ) : (
                    <>
                        <div className="h-12 w-12 rounded-full bg-green-100 text-green-600 flex items-center justify-center">
                            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                        </div>
                        <p className="text-sm text-muted-foreground">Data received successfully.</p>
                    </>
                )}
            </CardContent>
            <CardFooter>
                {status === 'success' && (
                    <Button className="w-full" onClick={handleContinue}>Go to Dashboard</Button>
                )}
            </CardFooter>
        </Card>
    )
}
