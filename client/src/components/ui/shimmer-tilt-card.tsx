"use client";

import React from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

export const ShimmerBorder = ({
  children,
  className,
  shimmerColor = "#F3CA40",
  borderWidth = 1,
  borderRadius = "1rem",
  shimmerSize = "0.1em",
  shimmerDuration = "3s",
  background = "#0f0f1a",
  as: Component = "div",
}: {
  children: React.ReactNode;
  className?: string;
  shimmerColor?: string;
  borderWidth?: number;
  borderRadius?: string;
  shimmerSize?: string;
  shimmerDuration?: string;
  background?: string;
  as?: React.ElementType;
}) => {
  return (
    <Component
      style={
        {
          "--border-width": `${borderWidth}px`,
          "--border-radius": borderRadius,
          "--shimmer-color": shimmerColor,
          "--shimmer-size": shimmerSize,
          "--shimmer-duration": shimmerDuration,
        } as React.CSSProperties
      }
      className={cn(
        "relative overflow-hidden p-[1px]",
        className
      )}
    >
      {/* Shimmer pseudo-element */}
      <div
        className="absolute inset-0 animate-[shimmerBorder_var(--shimmer-duration)_linear_infinite]"
        style={{
          background: `conic-gradient(from 0deg, transparent 0%, var(--shimmer-color) 10%, transparent 20%)`,
          filter: "blur(var(--shimmer-size))",
        }}
      />

      {/* Inner content area */}
      <div
        className="relative z-10 h-full w-full overflow-hidden"
        style={{
          background,
          borderRadius: `calc(var(--border-radius) - 1px)`,
        }}
      >
        <div className="p-6">
          {children}
        </div>
      </div>
    </Component>
  );
};

/** Backward-compatible combo: ShimmerBorder + TiltCard */
export const ShimmerTiltCard = ({
  children,
  className,
  ...props
}: React.ComponentProps<typeof ShimmerBorder>) => {
  return (
    <TiltCard className={className}>
      <ShimmerBorder {...props}>
        {children}
      </ShimmerBorder>
    </TiltCard>
  );
};

export const TiltCard = ({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) => {
  return (
    <motion.div
      whileHover={{ scale: 1.01, rotateX: 1, rotateY: 1 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
      className={cn(
        "h-full w-full perspective-[1000px]",
        className
      )}
    >
      {children}
    </motion.div>
  );
};
