interface BadgeProps {
  children: React.ReactNode;
  variant?: "default" | "success" | "warning" | "error" | "info" | "primary";
  size?: "sm" | "md";
  className?: string;
}

export function Badge({
  children,
  variant = "default",
  size = "sm",
  className = "",
}: BadgeProps) {
  const variantClasses = {
    default: "bg-white/50 text-surface-600 border-white/40 backdrop-blur-sm",
    success:
      "bg-emerald-50/70 text-emerald-700 border-emerald-200/50 backdrop-blur-sm",
    warning: "bg-amber-50/70 text-amber-700 border-amber-200/50 backdrop-blur-sm",
    error: "bg-red-50/70 text-red-700 border-red-200/50 backdrop-blur-sm",
    info: "bg-primary-50/70 text-primary-700 border-primary-200/50 backdrop-blur-sm",
    primary:
      "bg-primary-50/70 text-primary-700 border-primary-200/50 backdrop-blur-sm",
  };

  const sizeClasses = {
    sm: "px-2.5 py-0.5 text-xs",
    md: "px-3 py-1 text-sm",
  };

  return (
    <span
      className={`inline-flex items-center font-medium rounded-full border transition-all duration-300 ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
    >
      {children}
    </span>
  );
}
