export function TypingIndicator({ text }: { text: string }) {
  return (
    <div className="flex items-center gap-3 animate-fade-in">
      <div className="flex items-center gap-2.5 glass-card !rounded-2xl px-5 py-3.5">
        <div className="flex gap-1.5">
          <span
            className="w-2 h-2 bg-gradient-to-br from-primary-400 to-primary-500 rounded-full animate-pulse-dot"
            style={{ animationDelay: "0s" }}
          />
          <span
            className="w-2 h-2 bg-gradient-to-br from-primary-400 to-primary-500 rounded-full animate-pulse-dot"
            style={{ animationDelay: "0.2s" }}
          />
          <span
            className="w-2 h-2 bg-gradient-to-br from-primary-400 to-primary-500 rounded-full animate-pulse-dot"
            style={{ animationDelay: "0.4s" }}
          />
        </div>
        <span className="text-sm text-surface-500 ml-1 font-medium">{text}</span>
      </div>
    </div>
  );
}
