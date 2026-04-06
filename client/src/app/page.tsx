"use client";

import { SiteHeader } from "@/components/layout/site-header";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-dark-green">
      <SiteHeader activePage="home" />
    </div>
  );
}