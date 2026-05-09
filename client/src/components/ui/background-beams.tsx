"use client";

import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

export const BackgroundBeams = ({
  className,
  beamColor = "#F3CA40",
}: {
  className?: string;
  beamColor?: string;
}) => {
  return (
    <div
      className={cn(
        "absolute inset-0 z-0 overflow-hidden",
        className
      )}
    >
      <svg
        className="pointer-events-none absolute h-full w-full"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id="beam-grad-1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={beamColor} stopOpacity="0" />
            <stop offset="50%" stopColor={beamColor} stopOpacity="0.08" />
            <stop offset="100%" stopColor={beamColor} stopOpacity="0" />
          </linearGradient>
        </defs>
        {/* Diagonal beams */}
        {[...Array(6)].map((_, i) => (
          <motion.line
            key={`beam-${i}`}
            x1={`${i * 20}%`}
            y1="0%"
            x2={`${i * 20 + 40}%`}
            y2="100%"
            stroke="url(#beam-grad-1)"
            strokeWidth="1"
            initial={{ opacity: 0 }}
            animate={{ opacity: [0, 0.5, 0] }}
            transition={{
              duration: 4,
              delay: i * 0.6,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        ))}
        {[...Array(6)].map((_, i) => (
          <motion.line
            key={`beam-r-${i}`}
            x1={`${100 - i * 20}%`}
            y1="0%"
            x2={`${60 - i * 20}%`}
            y2="100%"
            stroke="url(#beam-grad-1)"
            strokeWidth="1"
            initial={{ opacity: 0 }}
            animate={{ opacity: [0, 0.5, 0] }}
            transition={{
              duration: 4,
              delay: i * 0.6 + 0.3,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        ))}
      </svg>
    </div>
  );
};
