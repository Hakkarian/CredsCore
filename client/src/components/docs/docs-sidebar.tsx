"use client";

import cn from "classnames";
import styles from "./docs-sidebar.module.scss";

interface DocsSidebarProps {
  sections: { id: string; title: string; icon: string }[];
  activeSection: string;
  onSectionChange: (id: string) => void;
}

export function DocsSidebar({ sections, activeSection, onSectionChange }: DocsSidebarProps) {
  return (
    <aside className={styles.docsSidebar}>
      <nav className={styles.docsSidebarNav}>
        {sections.map((section) => (
          <button
            key={section.id}
            onClick={() => onSectionChange(section.id)}
            className={cn(styles.docsSidebarButton, activeSection === section.id && styles.active)}
          >
            <span className={styles.docsSidebarIcon}>{section.icon}</span>
            <span>{section.title}</span>
          </button>
        ))}
      </nav>
    </aside>
  );
}