"use client";

const NAV_LINKS = [
  { label: "Home", href: "/" },
  { label: "Dashboard", href: "/dashboard" },
  { label: "Docs", href: "/docs" },
];

interface SiteHeaderProps {
  activePage?: string;
}

export function SiteHeader({ activePage }: SiteHeaderProps) {
  return (
    <header className="sticky top-0 z-50 bg-dark-green/90 backdrop-blur-md border-b border-card-border/30">
      <div className="max-w-7xl mx-auto px-8 py-5 flex items-center justify-between">
        <a href="/" className="flex items-center gap-3">
          <div className="w-10 h-10 gradient-primary rounded-xl flex items-center justify-center shadow-md">
            <span className="text-dark-green font-bold text-sm">CC</span>
          </div>
          <span className="font-display font-bold text-lg text-white">CredsCore</span>
        </a>
        <nav className="flex items-center gap-8">
          {NAV_LINKS.map((link) => {
            const isActive = activePage === link.label.toLowerCase();
            return (
              <a
                key={link.label}
                href={link.href}
                className={`transition-colors duration-200 text-sm font-medium ${
                  isActive
                    ? "text-primary"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                {link.label}
              </a>
            );
          })}
        </nav>
      </div>
    </header>
  );
}