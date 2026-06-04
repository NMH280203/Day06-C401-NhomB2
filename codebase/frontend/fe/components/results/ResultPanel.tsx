import React, { useState, useEffect } from 'react'
import { useChatStore } from '../../hooks/useChatStore'
import { FoodList } from './FoodList'
import { RestaurantList } from './RestaurantList'
import { MapEmbed } from '../map/MapEmbed'
import { Utensils, Store, Map, ChevronUp, ChevronDown } from 'lucide-react'

export function ResultPanel() {
  const { foods, restaurants } = useChatStore((state) => state.results)
  const userLocation = useChatStore((state) => state.context.location)

  const [activeTab, setActiveTab] = useState<'foods' | 'restaurants' | 'map'>('foods')
  const [mobileExpanded, setMobileExpanded] = useState<boolean>(false)

  const showFoods = foods.length > 0
  const showRestaurants = restaurants.length > 0
  const showMap = restaurants.length > 0 || !!userLocation

  // Auto-switch tabs based on data updates
  useEffect(() => {
    if (showFoods) {
      setActiveTab('foods')
      setMobileExpanded(true) // Auto-expand when results arrive
    } else if (showRestaurants) {
      setActiveTab('restaurants')
      setMobileExpanded(true)
    } else if (showMap) {
      setActiveTab('map')
    }
  }, [showFoods, showRestaurants, showMap])

  // Check if there is any data to show at all
  const hasData = showFoods || showRestaurants || showMap

  if (!hasData) return null

  return (
    <>
      {/* Desktop Panel - Hidden on Mobile */}
      <aside className="hidden md:flex flex-col w-96 border-l border-slate-800/80 bg-slate-950/80 backdrop-blur-xl h-full flex-shrink-0">
        {/* Tab Navigation */}
        <div className="flex border-b border-slate-800/80 p-2 bg-slate-900/30 gap-1">
          {showFoods && (
            <button
              onClick={() => setActiveTab('foods')}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-3 text-xs font-semibold rounded-lg transition-all ${
                activeTab === 'foods'
                  ? 'bg-orange-500/10 text-orange-400 border border-orange-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'
              }`}
            >
              <Utensils className="w-3.5 h-3.5" />
              <span>Món ăn ({foods.length})</span>
            </button>
          )}

          {showRestaurants && (
            <button
              onClick={() => setActiveTab('restaurants')}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-3 text-xs font-semibold rounded-lg transition-all ${
                activeTab === 'restaurants'
                  ? 'bg-orange-500/10 text-orange-400 border border-orange-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'
              }`}
            >
              <Store className="w-3.5 h-3.5" />
              <span>Quán ăn ({restaurants.length})</span>
            </button>
          )}

          {showMap && (
            <button
              onClick={() => setActiveTab('map')}
              className={`flex-1 flex items-center justify-center gap-1.5 py-2 px-3 text-xs font-semibold rounded-lg transition-all ${
                activeTab === 'map'
                  ? 'bg-orange-500/10 text-orange-400 border border-orange-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'
              }`}
            >
              <Map className="w-3.5 h-3.5" />
              <span>Bản đồ</span>
            </button>
          )}
        </div>

        {/* Tab Contents */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
          {activeTab === 'foods' && showFoods && <FoodList foods={foods} />}
          {activeTab === 'restaurants' && showRestaurants && <RestaurantList restaurants={restaurants} />}
          {activeTab === 'map' && showMap && <MapEmbed restaurants={restaurants} />}
        </div>
      </aside>

      {/* Mobile Bottom Sheet Panel */}
      <div
        className={`md:hidden fixed inset-x-0 bottom-0 z-40 bg-slate-950/95 border-t border-slate-800/90 shadow-2xl transition-all duration-500 ease-in-out flex flex-col ${
          mobileExpanded ? 'h-[70vh] rounded-t-3xl' : 'h-[60px] rounded-none'
        }`}
      >
        {/* Handle Bar / Header */}
        <div
          onClick={() => setMobileExpanded(!mobileExpanded)}
          className="flex items-center justify-between px-5 h-[60px] cursor-pointer border-b border-slate-900/50 select-none flex-shrink-0"
        >
          <div className="flex items-center gap-2">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-orange-500"></span>
            </span>
            <span className="text-sm font-bold text-slate-200">
              Kết quả gợi ý ({foods.length} món, {restaurants.length} quán)
            </span>
          </div>
          <button className="text-slate-400 hover:text-slate-200">
            {mobileExpanded ? <ChevronDown className="w-5 h-5" /> : <ChevronUp className="w-5 h-5" />}
          </button>
        </div>

        {/* Tab Navigation (Visible when expanded) */}
        {mobileExpanded && (
          <>
            <div className="flex border-b border-slate-900 p-2 gap-1 bg-slate-900/20 flex-shrink-0">
              {showFoods && (
                <button
                  onClick={() => setActiveTab('foods')}
                  className={`flex-1 flex items-center justify-center gap-1 py-2 text-xs font-semibold rounded-lg transition-all ${
                    activeTab === 'foods'
                      ? 'bg-orange-500/15 text-orange-400'
                      : 'text-slate-450 hover:bg-slate-900/50'
                  }`}
                >
                  <Utensils className="w-3.5 h-3.5" />
                  <span>Món ăn ({foods.length})</span>
                </button>
              )}

              {showRestaurants && (
                <button
                  onClick={() => setActiveTab('restaurants')}
                  className={`flex-1 flex items-center justify-center gap-1 py-2 text-xs font-semibold rounded-lg transition-all ${
                    activeTab === 'restaurants'
                      ? 'bg-orange-500/15 text-orange-400'
                      : 'text-slate-450 hover:bg-slate-900/50'
                  }`}
                >
                  <Store className="w-3.5 h-3.5" />
                  <span>Quán ăn ({restaurants.length})</span>
                </button>
              )}

              {showMap && (
                <button
                  onClick={() => setActiveTab('map')}
                  className={`flex-1 flex items-center justify-center gap-1 py-2 text-xs font-semibold rounded-lg transition-all ${
                    activeTab === 'map'
                      ? 'bg-orange-500/15 text-orange-400'
                      : 'text-slate-455 hover:bg-slate-900/50'
                  }`}
                >
                  <Map className="w-3.5 h-3.5" />
                  <span>Bản đồ</span>
                </button>
              )}
            </div>

            {/* Scrollable Contents */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {activeTab === 'foods' && showFoods && <FoodList foods={foods} />}
              {activeTab === 'restaurants' && showRestaurants && <RestaurantList restaurants={restaurants} />}
              {activeTab === 'map' && showMap && <MapEmbed restaurants={restaurants} />}
            </div>
          </>
        )}
      </div>
    </>
  )
}
