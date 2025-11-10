import { useEffect, useState } from 'react'

export function OnlineStatus() {
  const [online, setOnline] = useState<boolean>(navigator.onLine)

  useEffect(() => {
    const on = () => setOnline(true)
    const off = () => setOnline(false)
    window.addEventListener('online', on)
    window.addEventListener('offline', off)
    return () => {
      window.removeEventListener('online', on)
      window.removeEventListener('offline', off)
    }
  }, [])

  if (online) return null

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      zIndex: 1000,
      background: '#b00020',
      color: 'white',
      textAlign: 'center',
      padding: '8px',
      fontSize: 14
    }}>
      Sin conexión. Algunos datos pueden no estar actualizados.
    </div>
  )
}
