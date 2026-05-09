"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence, useScroll, useMotionValueEvent } from "framer-motion";
import Link from "next/link";
import { cn } from "@/lib/utils";

interface NavItem {
  name: string;
  link: string;
}

export const FloatingNav = ({
  navItems,
  className,
}: {
  navItems: NavItem[];
  className?: string;
}) => {
  const { scrollY } = useScroll();
  const [visible, setVisible] = useState(true);

  useMotionValueEvent(scrollY, "change", (current) => {
    const prev = scrollY.getPrevious() ?? 0;
    if (current < 50) {
      setVisible(true);
    } else if (current > prev && current > 100) {
      setVisible(false);
    } else {
      setVisible(true);
    }
  });

  return (
    <AnimatePresence mode="wait">
      {visible && (
        <motion.div
          initial={{ opacity: 0, y: -100 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -100, opacity: 0 }}
          transition={{ duration: 0.3 }}
          className={cn(
            "fixed inset-x-0 top-4 z-50 mx-auto flex max-w-fit items-center justify-center gap-1 rounded-full border border-white/10 bg-black/80 px-4 py-2 shadow-[0px_2px_3px_-1px_rgba(0,0,0,0.1),0px_1px_0px_0px_rgba(25,28,33,0.02),0px_0px_0px_1px_rgba(25,28,33,0.05)] backdrop-blur-md",
            className
          )}
        >
          {navItems.map((item, idx) => (
            <Link
              key={idx}
              href={item.link}
              className="relative rounded-full px-4 py-2 text-sm font-medium text-neutral-300 transition-colors hover:text-primary"
            >
              <span className="relative z-10">{item.name}</span>
            </Link>
          ))}
          <Link
            href="/dashboard"
            className="relative rounded-full border border-primary/50 bg-primary/10 px-4 py-2 text-sm font-semibold text-primary transition-all hover:bg-primary/20 hover:shadow-[0_0_20px_rgba(243,202,64,0.3)]"
          >
            Dashboard
          </Link>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
