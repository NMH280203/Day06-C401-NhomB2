export function TypingIndicator({ text }: { text: string }) {
  return (
    <div className="flex items-center gap-3 animate-fade-in">
      <div className="flex items-center gap-2 bg-surface-100 rounded-2xl px-4 py-3">
        <div className="flex gap-1">
          <span
            className="w-2 h-2 bg-primary-400 rounded-full animate-pulse-dot"
            style={{ animationDelay: "0s" }}
          />
          <span
            className="w-2 h-2 bg-primary-400 rounded-full animate-pulse-dot"
            style={{ animationDelay: "0.2s" }}
          />
          <span
            className="w-2 h-2 bg-primary-400 rounded-full animate-pulse-dot"
            style={{ animationDelay: "0.4s" }}
          />
        </div>
        <span className="text-sm text-surface-500 ml-1">{text}</span>
      </div>
    </div>
  );
}
