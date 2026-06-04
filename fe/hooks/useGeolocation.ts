"use client";

import { useState, useCallback } from "react";
import type { Location } from "@/lib/types";
import { useChatStore } from "@/store/chatStore";

interface UseGeolocationReturn {
  location: Location | null;
  error: string | null;
  loading: boolean;
  request: () => void;
}

export function useGeolocation(): UseGeolocationReturn {
  const [location, setLocation] = useState<Location | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const setContext = useChatStore((state) => state.setContext);

  const request = useCallback(() => {
    if (!navigator.geolocation) {
      setError("Trình duyệt không hỗ trợ định vị");
      return;
    }

    setLoading(true);
    setError(null);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const loc: Location = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        };
        setLocation(loc);
        setContext({ location: loc });
        setLoading(false);
      },
      (err) => {
        let msg = "Không thể lấy vị trí";
        switch (err.code) {
          case err.PERMISSION_DENIED:
            msg = "Bạn đã từ chối quyền truy cập vị trí";
            break;
          case err.POSITION_UNAVAILABLE:
            msg = "Thông tin vị trí không khả dụng";
            break;
          case err.TIMEOUT:
            msg = "Yêu cầu vị trí đã hết thời gian";
            break;
        }
        setError(msg);
        setLoading(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000, // cache 5 min
      }
    );
  }, [setContext]);

  return { location, error, loading, request };
}
