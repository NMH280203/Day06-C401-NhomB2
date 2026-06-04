export function TypingIndicator({ text }: { text: string }) {
  return (
    <div className="flex items-center gap-3">
      <div className="relative flex items-center gap-2.5 glass-card !rounded-2xl px-5 py-3.5 overflow-hidden">
        <div
          className="absolute inset-0 opacity-40 bg-gradient-to-r from-transparent via-primary-200/30 to-transparent animate-shimmer"
          style={{ backgroundSize: "200% 100%" }}
        />
        <div className="relative flex gap-1.5">
          {[0, 0.15, 0.3].map((delay, i) => (
            <span
              key={i}
              className="w-2 h-2 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full animate-pulse-dot"
              style={{ animationDelay: `${delay}s` }}
            />
          ))}
        </div>
        <span className="relative text-sm text-surface-600 ml-1 font-medium">
          {text}
        </span>
      </div>
    </div>
  );
}
