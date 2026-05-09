"use client";

import { FloatingNav } from "@/components/ui/floating-nav";

const NAV_LINKS = [
  { name: "Home", link: "/" },
  { name: "Dashboard", link: "/dashboard" },
  { name: "Docs", link: "/docs" },
];

interface SiteHeaderProps {
  activePage?: string;
}

export function SiteHeader({ activePage: _activePage }: SiteHeaderProps) {
  return <FloatingNav navItems={NAV_LINKS} />;
}
