"use client";

import { useState } from "react";
import { ClipboardList, Rocket, Radio, Plug, Lightbulb, Brain } from "lucide-react";
import { DocsHeader, DocsSidebar, OverviewContent, QuickStartContent, ApiReferenceContent, EndpointsContent, ExamplesContent, ModelsContent } from "@/components/docs/docs-content";
import styles from "./page.module.scss";

const SECTIONS = [
  { id: "overview", title: "Overview", icon: ClipboardList },
  { id: "quickstart", title: "Quick Start", icon: Rocket },
  { id: "api", title: "API Reference", icon: Radio },
  { id: "endpoints", title: "Endpoints", icon: Plug },
  { id: "examples", title: "Examples", icon: Lightbulb },
  { id: "models", title: "Models", icon: Brain },
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
