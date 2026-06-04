import { Message, UserContext, FoodSuggestion, Restaurant } from './types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface SendMessagePayload {
  messages: Message[]
  context: UserContext
}

export interface SendMessageCallbacks {
  onThinking?: (status: string) => void
  onFoodResults?: (foods: FoodSuggestion[]) => void
  onRestaurantResults?: (restaurants: Restaurant[]) => void
  onTextDelta?: (delta: string) => void
  onAskContext?: (field: string, message: string) => void
  onDone?: (follow_up_suggestions: string[]) => void
  onError?: (message: string) => void
}

/**
 * Sends a message to the AI Chatbot backend and parses the SSE stream response.
 */
export async function sendMessage(
  payload: SendMessagePayload,
  callbacks: SendMessageCallbacks
): Promise<void> {
  // If backend URL is empty or matches a placeholder, fall back to mockSendMessage
  if (!process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_URL === 'MOCK') {
    return mockSendMessage(payload, callbacks)
  }

  try {
    const response = await fetch(`${API_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`)
    }

    if (!response.body) {
      throw new Error('ReadableStream not supported on response.')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    while (true) {
      const { value, done } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      // Save the last incomplete line back to buffer
      buffer = lines.pop() || ''

      let currentEvent = ''
      let currentData = ''

      for (const line of lines) {
        const trimmed = line.trim()
        if (!trimmed) continue

        if (trimmed.startsWith('event:')) {
          currentEvent = trimmed.substring(6).trim()
        } else if (trimmed.startsWith('data:')) {
          currentData = trimmed.substring(5).trim()
          
          // Trigger the corresponding callback
          try {
            switch (currentEvent) {
              case 'thinking':
                callbacks.onThinking?.(currentData)
                break
              case 'food_results':
                callbacks.onFoodResults?.(JSON.parse(currentData) as FoodSuggestion[])
                break
              case 'restaurant_results':
                callbacks.onRestaurantResults?.(JSON.parse(currentData) as Restaurant[])
                break
              case 'text':
                // For SSE, text delta is usually plain text or JSON string
                let parsedText = currentData
                try {
                  parsedText = JSON.parse(currentData)
                } catch {
                  // Fallback to raw string
                }
                callbacks.onTextDelta?.(parsedText)
                break
              case 'ask_context':
                const contextAsk = JSON.parse(currentData) as { field: string; message: string }
                callbacks.onAskContext?.(contextAsk.field, contextAsk.message)
                break
              case 'done':
                const doneData = currentData ? (JSON.parse(currentData) as string[]) : []
                callbacks.onDone?.(doneData)
                break
              case 'error':
                callbacks.onError?.(currentData)
                break
              default:
                break
            }
          } catch (err) {
            console.error('Error parsing SSE event data:', err, 'Line:', trimmed)
          }

          // Reset events for next data block
          currentEvent = ''
          currentData = ''
        }
      }
    }
  } catch (error) {
    console.error('Fetch error, falling back to mock mode:', error)
    if (callbacks.onError) {
      callbacks.onError(error instanceof Error ? error.message : String(error))
    }
  }
}

/**
 * Fetches nearby restaurants based on search filters.
 */
export async function getRestaurants(params: {
  lat: number
  lng: number
  query?: string
  budget?: number
  radius?: number
  limit?: number
}): Promise<{ restaurants: Restaurant[]; total: number }> {
  if (!process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_URL === 'MOCK') {
    // Return mock restaurants filtered by basic query/budget parameters
    const mockList = getMockRestaurants()
    const filtered = mockList.filter((r) => {
      if (params.budget && r.price_level * 100000 > params.budget) return false
      if (params.query && !r.name.toLowerCase().includes(params.query.toLowerCase())) return false
      return true
    })
    return { restaurants: filtered.slice(0, params.limit || 5), total: filtered.length }
  }

  const queryParams = new URLSearchParams({
    lat: params.lat.toString(),
    lng: params.lng.toString(),
    ...(params.query && { query: params.query }),
    ...(params.budget && { budget: params.budget.toString() }),
    ...(params.radius && { radius: params.radius.toString() }),
    ...(params.limit && { limit: params.limit.toString() }),
  })

  try {
    const response = await fetch(`${API_URL}/api/restaurants?${queryParams.toString()}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch restaurants: ${response.statusText}`)
    }
    return await response.json()
  } catch (err) {
    console.error('Error getting restaurants, using mock data:', err)
    return { restaurants: getMockRestaurants().slice(0, params.limit || 5), total: getMockRestaurants().length }
  }
}

/**
 * Mock stream generator for testing independent of the backend.
 */
export async function mockSendMessage(
  payload: SendMessagePayload,
  callbacks: SendMessageCallbacks
): Promise<void> {
  const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))
  const userMessages = payload.messages.filter((m) => m.role === 'user')
  const userText = userMessages[userMessages.length - 1]?.content.toLowerCase() || ''

  try {
    // 1. Thinking step
    callbacks.onThinking?.('Đang phân tích yêu cầu ăn uống của bạn...')
    await wait(800)

    // Check query types
    const isRice = userText.includes('cơm') || userText.includes('rice')
    const isCoffee = userText.includes('cà phê') || userText.includes('nước') || userText.includes('coffee')

    // 2. Thinking stage 2
    callbacks.onThinking?.('Đang tìm các món ăn phù hợp với ngân sách của bạn...')
    await wait(1000)

    // 3. Yield Food recommendations
    let foodSuggestions: FoodSuggestion[] = []
    if (isCoffee) {
      foodSuggestions = [
        {
          name: 'Cà phê Trứng',
          category: 'Đồ uống',
          description: 'Cà phê espresso nóng hổi phủ lớp kem trứng đánh bông béo ngậy ngọt ngào.',
          estimated_price: 45000,
          reason: 'Món nước đặc sản Hà Nội cực kỳ thích hợp để thưởng thức buổi sáng.',
          tags: ['Đặc sản', 'Béo ngậy', 'Cà phê'],
        },
        {
          name: 'Trà Đào Cam Sả',
          category: 'Đồ uống',
          description: 'Trà đào thơm phức kết hợp cam vàng chua nhẹ và hương thơm nồng của sả tươi.',
          estimated_price: 39000,
          reason: 'Món trà thanh mát giải nhiệt hoàn hảo cho những ngày oi bức.',
          tags: ['Thanh mát', 'Trái cây', 'Giải nhiệt'],
        }
      ]
    } else if (isRice) {
      foodSuggestions = [
        {
          name: 'Cơm Tấm Sườn Bì Chả',
          category: 'Cơm',
          description: 'Cơm hạt tấm dẻo thơm ăn kèm sườn heo nướng mật ong vị đậm đà, bì thính heo giòn dai và chả trứng đúc thịt.',
          estimated_price: 55000,
          reason: 'Đáp ứng nhu cầu cơm tấm truyền thống đầy đủ dinh dưỡng, no bụng lâu.',
          tags: ['Truyền thống', 'Ăn trưa', 'Đậm đà'],
        },
        {
          name: 'Cơm Gà Hải Nam',
          category: 'Cơm chicken',
          description: 'Cơm được nấu bằng nước luộc gà béo ngậy, dùng chung với thịt gà luộc da giòn, dai ngọt kèm nước sốt gừng tỏi đặc trưng.',
          estimated_price: 60000,
          reason: 'Lựa chọn nhẹ nhàng, dinh dưỡng cao thích hợp cho cả bữa trưa lẫn tối.',
          tags: ['Ít dầu mỡ', 'Thơm dẻo', 'Gà ta'],
        }
      ]
    } else {
      // Default / Noodles
      foodSuggestions = [
        {
          name: 'Phở Bò Tái Lăn',
          category: 'Món nước',
          description: 'Bánh phở mềm dai chan nước dùng hầm xương ngọt lịm, bò tái lăn xào tỏi thơm nức cùng rất nhiều hành lá.',
          estimated_price: 50000,
          reason: 'Phù hợp với sở thích ăn phở truyền thống, hương vị đậm đà và làm ấm bụng.',
          tags: ['Đặc sản', 'Bò tái', 'Nước dùng đậm đà'],
        },
        {
          name: 'Bún Chả Hà Nội',
          category: 'Món khô/nước dùng',
          description: 'Chả viên nướng xém cạnh thơm phức ngâm trong nước mắm chua ngọt ấm nóng, ăn kèm bún rối và rau sống tươi mát.',
          estimated_price: 45000,
          reason: 'Món ăn thanh mát, hài hòa giữa vị chua, ngọt, mặn và hương thơm khói đặc trưng.',
          tags: ['Cổ điển', 'Nướng than', 'Đặc sản'],
        }
      ]
    }

    callbacks.onFoodResults?.(foodSuggestions)
    await wait(600)

    // 4. Thinking stage 3
    callbacks.onThinking?.('Đang quét các nhà hàng gần vị trí của bạn (bán kính 2km)...')
    await wait(1200)

    // 5. Yield Restaurant recommendations
    let restaurants: Restaurant[] = []
    if (isCoffee) {
      restaurants = [
        {
          place_id: 'res_1',
          name: 'Cà Phê Giảng',
          address: 'Ngõ 39 Nguyễn Hữu Huân, Lý Thái Tổ, Hoàn Kiếm, Hà Nội',
          distance_km: 0.8,
          rating: 4.6,
          price_level: 2,
          is_open: true,
          phone: '0989898989',
          maps_url: 'https://maps.google.com/?q=Ca+Phe+Giang+Nguyen+Huu+Huan',
          photo_url: 'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&q=80&w=400',
          featured_dishes: ['Cà phê trứng', 'Đậu nành trứng', 'Bia trứng'],
          score: 9.5,
        },
        {
          place_id: 'res_2',
          name: 'The Coffee House - Lý Thường Kiệt',
          address: '45 Lý Thường Kiệt, Trần Hưng Đạo, Hoàn Kiếm, Hà Nội',
          distance_km: 1.2,
          rating: 4.3,
          price_level: 2,
          is_open: true,
          phone: '1800 6936',
          maps_url: 'https://maps.google.com/?q=The+Coffee+House+Ly+Thuong+Kiet',
          photo_url: 'https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&q=80&w=400',
          featured_dishes: ['Trà đào cam sả', 'Cà phê sữa đá', 'Bánh mousse gấu'],
          score: 8.8,
        }
      ]
    } else if (isRice) {
      restaurants = [
        {
          place_id: 'res_3',
          name: 'Cơm Tấm Sườn Kiều Giang',
          address: '192 Nguyễn Hữu Cảnh, Quận Bình Thạnh, TP. HCM',
          distance_km: 1.5,
          rating: 4.1,
          price_level: 3,
          is_open: true,
          phone: '02838383838',
          maps_url: 'https://maps.google.com/?q=Com+Tam+Kieu+Giang+Nguyen+Huu+Canh',
          photo_url: 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&q=80&w=400',
          featured_dishes: ['Cơm tấm sườn chả', 'Cơm gà nướng'],
          score: 8.5,
        },
        {
          place_id: 'res_4',
          name: 'Cơm Gà Hải Nam Singapore',
          address: '21 Phan Xích Long, Quận Phú Nhuận, TP. HCM',
          distance_km: 0.5,
          rating: 4.4,
          price_level: 2,
          is_open: true,
          phone: '0901234567',
          maps_url: 'https://maps.google.com/?q=Com+Ga+Hai+Nam+Phan+Xich+Long',
          photo_url: 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&q=80&w=400',
          featured_dishes: ['Cơm gà luộc Hải Nam', 'Gà quay xốt tiêu'],
          score: 9.0,
        }
      ]
    } else {
      restaurants = [
        {
          place_id: 'res_5',
          name: 'Phở Thìn Lò Đúc',
          address: '13 Lò Đúc, Phạm Đình Hổ, Hai Bà Trưng, Hà Nội',
          distance_km: 0.3,
          rating: 4.5,
          price_level: 2,
          is_open: true,
          phone: '0977665544',
          maps_url: 'https://maps.google.com/?q=Pho+Thin+Lo+Duc',
          photo_url: 'https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?auto=format&fit=crop&q=80&w=400',
          featured_dishes: ['Phở tái lăn', 'Quẩy giòn', 'Trà đá'],
          score: 9.6,
        },
        {
          place_id: 'res_6',
          name: 'Bún Chả Hương Liên (Obama)',
          address: '24 Lê Văn Hưu, Phan Chu Trinh, Hai Bà Trưng, Hà Nội',
          distance_km: 1.1,
          rating: 4.4,
          price_level: 2,
          is_open: true,
          phone: '02439434106',
          maps_url: 'https://maps.google.com/?q=Bun+Cha+Huong+Lien+Le+Van+Huu',
          photo_url: 'https://images.unsplash.com/photo-1627308595229-7830a5c91f9f?auto=format&fit=crop&q=80&w=400',
          featured_dishes: ['Suất bún chả Obama', 'Nem hải sản', 'Nem cua bể'],
          score: 9.2,
        }
      ]
    }

    callbacks.onRestaurantResults?.(restaurants)
    await wait(600)

    // 6. Text response typing stream
    let responseText = ''
    if (isCoffee) {
      responseText = `Dựa trên sở thích uống nước giải khát hoặc cà phê của bạn, tôi đề xuất bạn thử **Cà phê Trứng** thơm béo đặc sản tại **Cà Phê Giảng** (cách bạn chỉ 0.8km). Nếu bạn thích đồ uống tươi mát giải nhiệt, món **Trà Đào Cam Sả** của quán **The Coffee House** ở phố Lý Thường Kiệt sẽ là sự lựa chọn hoàn hảo!\n\nTôi đã đính kèm danh sách đồ uống và quán cà phê ở cột bên phải. Bạn có muốn tìm hiểu thêm về thực đơn hay giờ mở cửa không?`
    } else if (isRice) {
      responseText = `Để nạp năng lượng no lâu cho bữa ăn chính của bạn, tôi xin gợi ý món **Cơm Tấm Sườn Bì Chả** hoặc **Cơm Gà Hải Nam**. \n\nBạn có thể ghé **Cơm Gà Hải Nam Singapore** chỉ cách bạn 0.5km với không gian mát mẻ, hoặc quán cơm tấm **Kiều Giang** ngon nổi tiếng cách 1.5km. Cả hai quán đều mở cửa và nằm trong khoảng giá 40,000đ - 65,000đ của bạn.`
    } else {
      responseText = `Chào bạn! Tôi đã tìm thấy một số gợi ý tuyệt vời cho bạn xung quanh đây. Nổi bật nhất là món **Phở Bò Tái Lăn** tại **Phở Thìn Lò Đúc** (cách bạn chỉ 300m, đang mở cửa, điểm đánh giá xuất sắc 4.5⭐). Ngoài ra, nếu bạn thích hương vị nướng than truyền thống thì bún chả **Hương Liên** (quán bún chả Obama nổi tiếng) cách 1.1km cũng là một lựa chọn cực kỳ đáng thử đấy!\n\nChi tiết thực đơn, khoảng cách và địa chỉ cụ thể đã được cập nhật ở tab bên phải.`
    }

    const words = responseText.split(' ')
    
    // Type out the text in chunks
    for (let i = 0; i < words.length; i += 3) {
      const chunk = words.slice(i, i + 3).join(' ') + ' '
      callbacks.onTextDelta?.(chunk)
      await wait(80)
    }

    await wait(500)

    // 7. Complete stream with follow-up suggestions
    const followUps = isCoffee
      ? ['Tìm quán cà phê yên tĩnh', 'Quán nào mở 24/7?', 'Có chỗ đậu xe hơi không?']
      : isRice
      ? ['Tìm cơm tấm rẻ hơn dưới 40k', 'Quán cơm gà nào giao hàng nhanh?', 'Có cơm chay không?']
      : ['Tìm quán bún riêu', 'Quán nào có máy lạnh?', 'Quán ăn vỉa hè giá rẻ']

    callbacks.onDone?.(followUps)

  } catch {
    callbacks.onError?.('Đã xảy ra lỗi kết nối với máy chủ AI. Vui lòng thử lại!')
  }
}

/**
 * Global mock restaurant dataset for offline queries
 */
function getMockRestaurants(): Restaurant[] {
  return [
    {
      place_id: 'res_5',
      name: 'Phở Thìn Lò Đúc',
      address: '13 Lò Đúc, Phạm Đình Hổ, Hai Bà Trưng, Hà Nội',
      distance_km: 0.3,
      rating: 4.5,
      price_level: 2,
      is_open: true,
      phone: '0977665544',
      maps_url: 'https://maps.google.com/?q=Pho+Thin+Lo+Duc',
      photo_url: 'https://images.unsplash.com/photo-1582878826629-29b7ad1cdc43?auto=format&fit=crop&q=80&w=400',
      featured_dishes: ['Phở tái lăn', 'Quẩy giòn', 'Trà đá'],
      score: 9.6,
    },
    {
      place_id: 'res_6',
      name: 'Bún Chả Hương Liên (Obama)',
      address: '24 Lê Văn Hưu, Phan Chu Trinh, Hai Bà Trưng, Hà Nội',
      distance_km: 1.1,
      rating: 4.4,
      price_level: 2,
      is_open: true,
      phone: '02439434106',
      maps_url: 'https://maps.google.com/?q=Bun+Cha+Huong+Lien+Le+Van+Huu',
      photo_url: 'https://images.unsplash.com/photo-1627308595229-7830a5c91f9f?auto=format&fit=crop&q=80&w=400',
      featured_dishes: ['Suất bún chả Obama', 'Nem hải sản', 'Nem cua bể'],
      score: 9.2,
    },
    {
      place_id: 'res_1',
      name: 'Cà Phê Giảng',
      address: 'Ngõ 39 Nguyễn Hữu Huân, Lý Thái Tổ, Hoàn Kiếm, Hà Nội',
      distance_km: 0.8,
      rating: 4.6,
      price_level: 2,
      is_open: true,
      phone: '0989898989',
      maps_url: 'https://maps.google.com/?q=Ca+Phe+Giang+Nguyen+Huu+Huuan',
      photo_url: 'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&q=80&w=400',
      featured_dishes: ['Cà phê trứng', 'Đậu nành trứng', 'Bia trứng'],
      score: 9.5,
    },
    {
      place_id: 'res_2',
      name: 'The Coffee House - Lý Thường Kiệt',
      address: '45 Lý Thường Kiệt, Trần Hưng Đạo, Hoàn Kiếm, Hà Nội',
      distance_km: 1.2,
      rating: 4.3,
      price_level: 2,
      is_open: true,
      phone: '1800 6936',
      maps_url: 'https://maps.google.com/?q=The+Coffee+House+Ly+Thuong+Kiet',
      photo_url: 'https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&q=80&w=400',
      featured_dishes: ['Trà đào cam sả', 'Cà phê sữa đá', 'Bánh mousse gấu'],
      score: 8.8,
    },
    {
      place_id: 'res_3',
      name: 'Cơm Tấm Sườn Kiều Giang',
      address: '192 Nguyễn Hữu Cảnh, Quận Bình Thạnh, TP. HCM',
      distance_km: 1.5,
      rating: 4.1,
      price_level: 3,
      is_open: true,
      phone: '02838383838',
      maps_url: 'https://maps.google.com/?q=Com+Tam+Kieu+Giang+Nguyen+Huu+Canh',
      photo_url: 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&q=80&w=400',
      featured_dishes: ['Cơm tấm sườn chả', 'Cơm gà nướng'],
      score: 8.5,
    },
    {
      place_id: 'res_4',
      name: 'Cơm Gà Hải Nam Singapore',
      address: '21 Phan Xích Long, Quận Phú Nhuận, TP. HCM',
      distance_km: 0.5,
      rating: 4.4,
      price_level: 2,
      is_open: true,
      phone: '0901234567',
      maps_url: 'https://maps.google.com/?q=Com+Ga+Hai+Nam+Phan+Xich+Long',
      photo_url: 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&q=80&w=400',
      featured_dishes: ['Cơm gà luộc Hải Nam', 'Gà quay xốt tiêu'],
      score: 9.0,
    }
  ]
}
