"use client";

import { useState } from "react";
import { DocsHeader, DocsSidebar, OverviewContent, QuickStartContent, ApiReferenceContent, EndpointsContent, ExamplesContent, ModelsContent } from "@/components/docs/docs-content";

const SECTIONS = [
  { id: "overview", title: "Overview", icon: "📖" },
  { id: "quickstart", title: "Quick Start", icon: "🚀" },
  { id: "api", title: "API Reference", icon: "⚡" },
  { id: "endpoints", title: "Endpoints", icon: "🔗" },
  { id: "examples", title: "Examples", icon: "💡" },
  { id: "models", title: "Models", icon: "🧠" },
];

const CONTENT_MAP: Record<string, React.FC> = {
  overview: OverviewContent,
  quickstart: QuickStartContent,
  api: ApiReferenceContent,
  endpoints: EndpointsContent,
  examples: ExamplesContent,
  models: ModelsContent,
};

export default function DocsPage() {
  const [activeSection, setActiveSection] = useState("overview");
  const ActiveContent = CONTENT_MAP[activeSection] || OverviewContent;

  return (
    <div className="min-h-screen bg-dark-green">
      <DocsHeader />
      <div className="pt-24 flex">
        <DocsSidebar sections={SECTIONS} activeSection={activeSection} onSectionChange={setActiveSection} />
        <main className="ml-64 flex-1 p-12">
          <ActiveContent />
        </main>
      </div>
    </div>
  );
}