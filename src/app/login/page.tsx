'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/context/AuthContext'

export default function Login() {
  const { login } = useAuth()
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true); setError('')
    try {
      await login(email, password)
      router.push('/dashboard')
    } catch { setError('Invalid email or password') }
    finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🎬</div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">MusicVideo AI</h1>
          <p className="text-gray-400 mt-2">Create AI-powered music videos instantly</p>
        </div>
        <div className="bg-gray-900 rounded-2xl p-8 border border-gray-800">
          <h2 className="text-xl font-semibold mb-6">Sign In</h2>
          {error && <p className="text-red-400 text-sm mb-4 bg-red-900/20 p-3 rounded-lg">{error}</p>}
          <form onSubmit={submit} className="space-y-4">
            <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)}
              className="w-full bg-gray-800 rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-purple-500 border border-gray-700" required />
            <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)}
              className="w-full bg-gray-800 rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-purple-500 border border-gray-700" required />
            <button type="submit" disabled={loading}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 py-3 rounded-xl font-semibold disabled:opacity-50 transition-all">
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
          <p className="text-center text-gray-400 mt-4 text-sm">
            No account? <Link href="/register" className="text-purple-400 hover:underline">Create one free</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
