"use client";

import { useState, useEffect } from "react";
import { Navigation } from "@/components/landing/landing-components";

export default function LandingPage() {
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    setIsLoaded(true);
  }, []);

  return (
    <div className="min-h-screen bg-dark-green">
      <Navigation isLoaded={isLoaded} />
    </div>
  );
}