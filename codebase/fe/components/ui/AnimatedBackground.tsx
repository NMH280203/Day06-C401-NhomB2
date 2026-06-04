"use client";

/** Nền gradient blob nhẹ — không chặn tương tác */
export function AnimatedBackground() {
  return (
    <div
      className="pointer-events-none fixed inset-0 overflow-hidden -z-10"
      aria-hidden
    >
      <div className="absolute -top-24 -left-24 w-80 h-80 rounded-full bg-primary-300/25 blur-3xl animate-blob" />
      <div
        className="absolute top-1/3 -right-20 w-96 h-96 rounded-full bg-accent-teal/20 blur-3xl animate-blob"
        style={{ animationDelay: "-4s" }}
      />
      <div
        className="absolute -bottom-32 left-1/3 w-[28rem] h-[28rem] rounded-full bg-accent-cyan/15 blur-3xl animate-float-slow"
        style={{ animationDelay: "-2s" }}
      />
    </div>
  );
}
