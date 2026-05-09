"use client";

import { useState } from "react";
import { DocsHeader, DocsSidebar, OverviewContent, QuickStartContent, ApiReferenceContent, EndpointsContent, ExamplesContent, ModelsContent } from "@/components/docs/docs-content";
import styles from "./page.module.scss";

const SECTIONS = [
  { id: "overview", title: "Overview", icon: "📋" },
  { id: "quickstart", title: "Quick Start", icon: "🚀" },
  { id: "api", title: "API Reference", icon: "📡" },
  { id: "endpoints", title: "Endpoints", icon: "🔌" },
  { id: "examples", title: "Examples", icon: "💡" },
  { id: "models", title: "Models", icon: "🧠" },
];

export default function DocsPage() {
  const [activeSection, setActiveSection] = useState("overview");

  return (
    <main className={styles.main}>
      <div className={styles.container}>
        <DocsHeader />
        <div className={styles.grid}>
          <DocsSidebar sections={SECTIONS} activeSection={activeSection} onSectionChange={setActiveSection} />
          <div className={styles.content}>
            {activeSection === "overview" && <OverviewContent />}
            {activeSection === "quickstart" && <QuickStartContent />}
            {activeSection === "api" && <ApiReferenceContent />}
            {activeSection === "endpoints" && <EndpointsContent />}
            {activeSection === "examples" && <ExamplesContent />}
            {activeSection === "models" && <ModelsContent />}
          </div>
        </div>
      </div>
    </main>
  );
}
