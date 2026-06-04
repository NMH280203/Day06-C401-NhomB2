import { useState, useCallback, useEffect } from 'react'
import { useChatStore } from './useChatStore'
import { Location } from '../lib/types'

export function useGeolocation() {
  const [location, setLocationState] = useState<Location | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState<boolean>(false)
  const setContext = useChatStore((state) => state.setContext)
  const storeLocation = useChatStore((state) => state.context.location)

  // Initialize from store if already exists
  useEffect(() => {
    if (storeLocation) {
      setLocationState(storeLocation)
    }
  }, [storeLocation])

  const request = useCallback(() => {
    if (typeof window === 'undefined' || !navigator.geolocation) {
      setError('Geolocation is not supported by your browser')
      return
    }

    setLoading(true)
    setError(null)

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const lat = position.coords.latitude
        const lng = position.coords.longitude

        // Try reverse geocoding with Nominatim (OpenStreetMap) or mock
        let address = 'Vị trí hiện tại'
        try {
          const res = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`,
            { headers: { 'User-Agent': 'FoodAI-Chatbot-Frontend' } }
          )
          if (res.ok) {
            const data = await res.json()
            address = data.display_name || address
            // Shorten the address for better badge layout
            const parts = address.split(',')
            if (parts.length > 3) {
              address = parts.slice(0, 3).join(',').trim()
            }
          }
        } catch (e) {
          console.warn('Could not reverse geocode address, using fallback:', e)
        }

        const newLoc: Location = { lat, lng, address }
        setLocationState(newLoc)
        setContext({ location: newLoc })
        setLoading(false)
      },
      (err) => {
        let msg = 'Không thể truy cập vị trí.'
        switch (err.code) {
          case err.PERMISSION_DENIED:
            msg = 'Vui lòng cho phép quyền truy cập vị trí trong trình duyệt.'
            break
          case err.POSITION_UNAVAILABLE:
            msg = 'Thông tin vị trí không khả dụng.'
            break
          case err.TIMEOUT:
            msg = 'Yêu cầu vị trí đã hết thời gian chờ.'
            break
        }
        setError(msg)
        setLoading(false)
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    )
  }, [setContext])

  return { location, error, loading, request }
}
