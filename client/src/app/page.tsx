import { LandingPage } from "@/components/landing/landing-components";
import styles from "./page.module.scss";

export default function Home() {
  return (
    <main className={styles.main}>
      <LandingPage />
    </main>
  );
}
