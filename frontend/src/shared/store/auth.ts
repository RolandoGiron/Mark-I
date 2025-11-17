import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Usuario } from '../types'

interface AuthState {
  user: Usuario | null
  token: string | null
  isAuthenticated: boolean
  setAuth: (user: Usuario, token: string) => void
  clearAuth: () => void
  updateUser: (user: Usuario) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      setAuth: (user, token) => {
        localStorage.setItem('auth_token', token)
        localStorage.setItem('user', JSON.stringify(user))
        set({ user, token, isAuthenticated: true })
      },

      clearAuth: () => {
        localStorage.removeItem('auth_token')
        localStorage.removeItem('user')
        set({ user: null, token: null, isAuthenticated: false })
      },

      updateUser: (user) => {
        localStorage.setItem('user', JSON.stringify(user))
        set({ user })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
