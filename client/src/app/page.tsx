"use client";

import { useState, useEffect } from "react";
import { Navigation, HeroSection, HeroVisual, StatsGrid, FeaturesSection, CTASection, Footer } from "@/components/landing/landing-components";

export default function LandingPage() {
  const [isLoaded, setIsLoaded] = useState(false);
  const [activeFeature, setActiveFeature] = useState(0);

  useEffect(() => {
    setIsLoaded(true);
  }, []);

  return (
    <div className="min-h-screen bg-dark-green overflow-hidden">
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 gradient-mesh opacity-20" />
        <div className="absolute top-20 left-20 w-72 h-72 bg-primary/20 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-accent-pink/20 rounded-full blur-3xl animate-float" style={{ animationDelay: "1.5s" }} />
        <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-accent-lavender/20 rounded-full blur-3xl animate-float" style={{ animationDelay: "3s" }} />
      </div>
      <Navigation isLoaded={isLoaded} />
      <HeroSection isLoaded={isLoaded} />
      <HeroVisual isLoaded={isLoaded} />
      <StatsGrid />
      <FeaturesSection activeFeature={activeFeature} onFeatureChange={setActiveFeature} />
      <CTASection />
      <Footer />
    </div>
  );
}