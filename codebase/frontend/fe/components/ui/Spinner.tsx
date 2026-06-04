import React from 'react'

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function Spinner({ size = 'md', className = '' }: SpinnerProps) {
  const sizes = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4',
  }

  return (
    <div className={`flex justify-center items-center ${className}`}>
      <div
        className={`${sizes[size]} animate-spin rounded-full border-t-orange-500 border-r-transparent border-b-orange-500 border-l-transparent`}
        role="status"
      >
        <span className="sr-only">Loading...</span>
      </div>
    </div>
  )
}
