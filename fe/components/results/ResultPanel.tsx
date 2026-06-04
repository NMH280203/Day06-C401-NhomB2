"use client";

import { useCallback, useEffect, useState } from "react";
import type { FoodSuggestion, Restaurant } from "@/lib/types";
import { FoodList } from "./FoodList";
import { RestaurantList } from "./RestaurantList";
import { MapEmbed } from "@/components/map/MapEmbed";

interface ResultPanelProps {
  foods: FoodSuggestion[];
  restaurants: Restaurant[];
}

type TabKey = "foods" | "restaurants" | "map";

export function ResultPanel({ foods, restaurants }: ResultPanelProps) {
  const [activeTab, setActiveTab] = useState<TabKey>("foods");
  const [isSheetOpen, setIsSheetOpen] = useState(false);
  const [selectedPlaceId, setSelectedPlaceId] = useState<string | null>(null);

  const hasData = foods.length > 0 || restaurants.length > 0;

  useEffect(() => {
    const firstWithCoords = restaurants.find(
      (r) => r.lat != null && r.lng != null
    );
    if (firstWithCoords) {
      setSelectedPlaceId(firstWithCoords.place_id);
    } else if (restaurants[0]) {
      setSelectedPlaceId(restaurants[0].place_id);
    } else {
      setSelectedPlaceId(null);
    }
  }, [restaurants]);

  const focusOnMap = useCallback((restaurant: Restaurant) => {
    setSelectedPlaceId(restaurant.place_id);
    setActiveTab("map");
    setIsSheetOpen(true);
  }, []);

  if (!hasData) return null;

  const tabs: { key: TabKey; label: string; icon: string; show: boolean }[] = [
    { key: "foods", label: "Món ăn", icon: "🍜", show: foods.length > 0 },
    {
      key: "restaurants",
      label: "Quán ăn",
      icon: "🏪",
      show: restaurants.length > 0,
    },
    {
      key: "map",
      label: "Bản đồ",
      icon: "🗺️",
      show: restaurants.length > 0,
    },
  ];

  const visibleTabs = tabs.filter((t) => t.show);

  const renderContent = () => {
    switch (activeTab) {
      case "foods":
        return <FoodList foods={foods} />;
      case "restaurants":
        return (
          <RestaurantList
            restaurants={restaurants}
            onViewOnMap={focusOnMap}
          />
        );
      case "map":
        return (
          <div className="h-[400px]">
            <MapEmbed
              restaurants={restaurants}
              selectedPlaceId={selectedPlaceId}
              onSelectPlace={setSelectedPlaceId}
            />
          </div>
        );
    }
  };

  const panelContent = (
    <>
      <div className="flex border-b border-surface-200 px-2">
        {visibleTabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex items-center gap-1.5 px-4 py-3.5 text-sm font-medium border-b-2 transition-all duration-300 ${
              activeTab === tab.key
                ? "border-primary-500 text-primary-600"
                : "border-transparent text-surface-400 hover:text-surface-600 hover:border-surface-300/50"
            }`}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto p-4">{renderContent()}</div>
    </>
  );

  return (
    <>
      <aside className="hidden lg:flex flex-col w-96 border-l border-surface-200 bg-white/80 backdrop-blur-xl h-full animate-slide-in-right">
        {panelContent}
      </aside>

      {hasData && (
        <button
          onClick={() => setIsSheetOpen(!isSheetOpen)}
          className="lg:hidden fixed bottom-24 right-4 z-40 w-14 h-14 rounded-2xl btn-glow flex items-center justify-center active:scale-95 transition-transform animate-glow-pulse"
          aria-label="Xem kết quả"
        >
          <span className="text-xl">{isSheetOpen ? "✕" : "📋"}</span>
          {!isSheetOpen && (
            <span className="absolute -top-1 -right-1 w-5 h-5 bg-accent-teal rounded-full text-[10px] text-white font-bold flex items-center justify-center shadow-sm">
              {foods.length + restaurants.length}
            </span>
          )}
        </button>
      )}

      {isSheetOpen && (
        <>
          <div
            className="lg:hidden fixed inset-0 bg-surface-950/20 backdrop-blur-sm z-40 animate-fade-in"
            onClick={() => setIsSheetOpen(false)}
          />
          <div className="lg:hidden fixed bottom-0 left-0 right-0 z-50 bg-white rounded-t-3xl shadow-2xl max-h-[75vh] flex flex-col animate-slide-up">
            <div className="flex justify-center pt-3 pb-1">
              <div className="w-10 h-1 bg-surface-300/50 rounded-full" />
            </div>
            {panelContent}
          </div>
        </>
      )}
    </>
  );
}
