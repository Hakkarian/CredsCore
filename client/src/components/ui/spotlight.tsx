"use client";

import { useEffect, useRef, useState } from "react";
import { motion, useAnimation } from "framer-motion";

export const Spotlight = ({
  children,
  className = "",
  fill = "white",
}: {
  children?: React.ReactNode;
  className?: string;
  fill?: string;
}) => {
  return (
    <div className={`relative overflow-hidden ${className}`}>
      <SpotlightBeam fill={fill} />
      {children}
    </div>
  );
};

const SpotlightBeam = ({ fill }: { fill: string }) => {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [opacity, setOpacity] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      setPosition({ x: e.clientX - rect.left, y: e.clientY - rect.top });
    };
    const el = containerRef.current;
    el?.addEventListener("mousemove", handleMouseMove);
    return () => el?.removeEventListener("mousemove", handleMouseMove);
  }, []);

  return (
    <div
      ref={containerRef}
      className="pointer-events-none absolute inset-0 z-0"
      onMouseEnter={() => setOpacity(1)}
      onMouseLeave={() => setOpacity(0)}
    >
      <motion.div
        className="absolute inset-0 z-0"
        animate={{ opacity }}
        transition={{ duration: 0.4 }}
      >
        <div
          className="absolute inset-0 z-10"
          style={{
            background: `radial-gradient(800px circle at ${position.x}px ${position.y}px, ${fill}15, transparent 40%)`,
          }}
        />
      </motion.div>
    </div>
  );
};

export const SpotlightHero = ({
  className = "",
  fill = "#F3CA40",
}: {
  className?: string;
  fill?: string;
}) => {
  const controls = useAnimation();

  useEffect(() => {
    controls.start({
      opacity: [0, 1, 0],
      x: [0, 200, 400],
      y: [0, 100, 50],
      transition: { duration: 5, repeat: Infinity, ease: "linear" },
    });
  }, [controls]);

  return (
    <motion.svg
      className={`absolute z-0 ${className}`}
      animate={controls}
      viewBox="0 0 800 800"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <radialGradient id="spotlight-gradient" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor={fill} stopOpacity="0.3" />
          <stop offset="100%" stopColor={fill} stopOpacity="0" />
        </radialGradient>
      </defs>
      <ellipse cx="400" cy="400" rx="400" ry="400" fill="url(#spotlight-gradient)" />
    </motion.svg>
  );
};
