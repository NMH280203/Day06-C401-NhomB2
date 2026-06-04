"use client";

import { useState } from "react";
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

  const hasData = foods.length > 0 || restaurants.length > 0;

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
        return <RestaurantList restaurants={restaurants} />;
      case "map":
        return (
          <div className="h-[400px]">
            <MapEmbed restaurants={restaurants} />
          </div>
        );
    }
  };

  // Desktop panel
  const panelContent = (
    <>
      {/* Tabs */}
      <div className="flex border-b border-white/20 px-3">
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

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-5">{renderContent()}</div>
    </>
  );

  return (
    <>
      {/* Desktop: Side panel */}
      <aside className="hidden lg:flex flex-col w-96 glass-sidebar h-full animate-slide-in-right">
        {panelContent}
      </aside>

      {/* Mobile: Bottom sheet toggle button */}
      {hasData && (
        <button
          onClick={() => setIsSheetOpen(!isSheetOpen)}
          className="lg:hidden fixed bottom-24 right-4 z-40 w-14 h-14 rounded-2xl btn-glow flex items-center justify-center active:scale-95 transition-transform animate-glow-pulse"
          aria-label="Xem kết quả"
        >
          <span className="text-xl">
            {isSheetOpen ? "✕" : "📋"}
          </span>
          {!isSheetOpen && (
            <span className="absolute -top-1 -right-1 w-5 h-5 bg-accent-teal rounded-full text-[10px] text-white font-bold flex items-center justify-center shadow-sm">
              {foods.length + restaurants.length}
            </span>
          )}
        </button>
      )}

      {/* Mobile: Bottom sheet */}
      {isSheetOpen && (
        <>
          {/* Backdrop */}
          <div
            className="lg:hidden fixed inset-0 bg-surface-950/20 backdrop-blur-sm z-40 animate-fade-in"
            onClick={() => setIsSheetOpen(false)}
          />

          {/* Sheet */}
          <div className="lg:hidden fixed bottom-0 left-0 right-0 z-50 glass-light rounded-t-3xl shadow-glass-lg max-h-[75vh] flex flex-col animate-slide-up">
            {/* Handle */}
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
