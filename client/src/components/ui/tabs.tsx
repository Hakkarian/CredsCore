"use client";

import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { useState } from "react";

export const Tabs = ({
  tabs,
  activeTab,
  onChange,
  className,
  containerClassName,
}: {
  tabs: { title: string; value: string }[];
  activeTab: string;
  onChange: (value: string) => void;
  className?: string;
  containerClassName?: string;
}) => {
  return (
    <div
      className={cn(
        "flex flex-wrap items-center gap-1 rounded-full border border-white/10 bg-black/60 p-1 backdrop-blur-md",
        containerClassName
      )}
    >
      {tabs.map((tab) => (
        <button
          key={tab.value}
          onClick={() => onChange(tab.value)}
          className={cn(
            "relative rounded-full px-5 py-2 text-sm font-medium transition-colors",
            activeTab === tab.value
              ? "text-primary"
              : "text-neutral-400 hover:text-neutral-200",
            className
          )}
        >
          {activeTab === tab.value && (
            <motion.span
              layoutId="tab-indicator"
              className="absolute inset-0 rounded-full bg-primary/10 border border-primary/30"
              transition={{ type: "spring", bounce: 0.3, duration: 0.5 }}
            />
          )}
          <span className="relative z-10">{tab.title}</span>
        </button>
      ))}
    </div>
  );
};
