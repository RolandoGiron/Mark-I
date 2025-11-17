import { useEffect } from 'react'
import { RouterProvider } from 'react-router-dom'
import { QueryProvider } from '@/shared/lib/react-query'
import { useThemeStore } from '@/shared/store/theme'
import { Toaster } from '@/shared/components/ui/toaster'
import { router } from '@/routes'

function App() {
  const theme = useThemeStore((state) => state.theme)

  // Aplicar tema al documento
  useEffect(() => {
    const root = window.document.documentElement
    root.classList.remove('light', 'dark')
    root.classList.add(theme)
  }, [theme])

  return (
    <QueryProvider>
      <RouterProvider router={router} />
      <Toaster />
    </QueryProvider>
  )
}

export default App
