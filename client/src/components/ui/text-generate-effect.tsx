"use client";

import { useEffect, useState } from "react";
import { motion, stagger, useAnimate } from "framer-motion";
import { cn } from "@/lib/utils";

export const TextGenerateEffect = ({
  words,
  className,
}: {
  words: string;
  className?: string;
}) => {
  const [scope, animate] = useAnimate();
  const wordArray = words.split(" ");
  const [started, setStarted] = useState(false);

  useEffect(() => {
    if (started) return;
    setStarted(true);
    animate(
      "span",
      { opacity: 1, filter: "blur(0px)" },
      { duration: 0.5, delay: stagger(0.08) }
    );
  }, [animate, started]);

  return (
    <motion.div ref={scope} className={cn("font-display", className)}>
      {wordArray.map((word, idx) => (
        <motion.span
          key={word + idx}
          className="inline-block opacity-0"
          style={{ filter: "blur(8px)" }}
        >
          {word}{" "}
        </motion.span>
      ))}
    </motion.div>
  );
};
