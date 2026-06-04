import React from 'react'

export default function ChatLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-col h-screen overflow-hidden bg-gradient-to-tr from-slate-950 via-slate-900 to-slate-950 text-slate-100 font-sans">
      {children}
    </div>
  )
}
