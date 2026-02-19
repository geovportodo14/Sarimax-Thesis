import { redirect } from 'next/navigation'

export default function Home() {
  // TODO: Add logic to check if user is new (-> /setup)
  // For now, assume user has data -> /dashboard
  redirect('/dashboard')
}
