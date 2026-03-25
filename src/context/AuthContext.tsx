'use client'
import { createContext, useContext, useEffect, useState } from 'react'
import { api } from '@/lib/api'

type User = { id: number; email: string; username: string }
type AuthContextType = { user: User | null; loading: boolean; login: (e: string, p: string) => Promise<void>; register: (e: string, u: string, p: string) => Promise<void>; logout: () => void }

const AuthContext = createContext<AuthContextType>({} as AuthContextType)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) api.me().then(setUser).catch(() => localStorage.removeItem('token')).finally(() => setLoading(false))
    else setLoading(false)
  }, [])

  const login = async (email: string, password: string) => {
    const data = await api.login(email, password)
    localStorage.setItem('token', data.access_token)
    setUser(await api.me())
  }

  const register = async (email: string, username: string, password: string) => {
    await api.register(email, username, password)
    await login(email, password)
  }

  const logout = () => { localStorage.removeItem('token'); setUser(null) }

  return <AuthContext.Provider value={{ user, loading, login, register, logout }}>{children}</AuthContext.Provider>
}

export const useAuth = () => useContext(AuthContext)
