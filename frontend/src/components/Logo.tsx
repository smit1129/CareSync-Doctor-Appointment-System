import React from "react";

export function Logo({ className = "w-6 h-6", textClassName = "text-xl", showText = true }: { className?: string, textClassName?: string, showText?: boolean }) {
  return (
    <div className="flex items-center gap-2">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        className={`text-teal-400 ${className}`}
      >
        <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
        <path d="M12 7v5l2 2" className="text-cyan-300" strokeWidth="2.5" />
      </svg>
      {showText && <span className={`font-bold tracking-tight ${textClassName}`}>CareSync</span>}
    </div>
  );
}
