import React from 'react'

interface BadgeProps {
  children: React.ReactNode
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'info' | 'glass'
  className?: string
}

export function Badge({
  children,
  variant = 'primary',
  className = '',
}: BadgeProps) {
  const baseStyle = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold tracking-wide transition-all'
  
  const variants = {
    primary: 'bg-orange-500/10 text-orange-400 border border-orange-500/20',
    secondary: 'bg-slate-700/50 text-slate-300 border border-slate-600/30',
    success: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
    warning: 'bg-amber-500/10 text-amber-400 border border-amber-500/20',
    info: 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20',
    glass: 'bg-white/5 text-white/80 border border-white/10 backdrop-blur-sm'
  }

  return (
    <span className={`${baseStyle} ${variants[variant]} ${className}`}>
      {children}
    </span>
  )
}
