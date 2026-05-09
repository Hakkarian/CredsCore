"use client";

import { useRef, useState } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import styles from "./label-input.module.scss";

export const LabelInput = ({
  label,
  type = "number",
  value,
  onChange,
  className,
  step = "any",
  min,
  max,
}: {
  label: string;
  type?: string;
  value: string | number;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  className?: string;
  step?: string;
  min?: number;
  max?: number;
}) => {
  const [focused, setFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const isActive = focused || (value !== "" && value !== undefined);

  return (
    <div className={cn(styles.wrapper, className)}>
      <motion.label
        animate={{
          y: isActive ? -22 : 0,
          scale: isActive ? 0.8 : 1,
          color: focused ? "#F3CA40" : "#D7C0D0",
        }}
        transition={{ duration: 0.2 }}
        className={cn(styles.label, isActive && styles.labelActive)}
        onClick={() => inputRef.current?.focus()}
      >
        {label}
      </motion.label>
      <input
        ref={inputRef}
        type={type}
        value={value}
        onChange={onChange}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        step={step}
        min={min}
        max={max}
        className={styles.input}
      />
    </div>
  );
};
