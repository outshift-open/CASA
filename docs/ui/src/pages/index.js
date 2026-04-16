import React from "react";
import clsx from "clsx";
import Link from "@docusaurus/Link";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import Layout from "@theme/Layout";
import styles from "./index.module.css";

function HomepageHeader() {
    const { siteConfig } = useDocusaurusContext();
    return (
        <header className={clsx("hero hero--primary", styles.heroBanner)}>
            <div className="container">
                <h1 className="hero__title">{siteConfig.title}</h1>
                <p className="hero__subtitle">{siteConfig.tagline}</p>
                <div className={styles.buttons}>
                    <Link
                        className="button button--secondary button--lg"
                        to="/installation/prerequisites"
                    >
                        Get Started →
                    </Link>
                    <Link
                        className="button button--outline button--lg"
                        style={{ color: "white", borderColor: "rgba(255,255,255,0.6)" }}
                        to="/architecture/architecture-overview"
                    >
                        Architecture
                    </Link>
                </div>
            </div>
        </header>
    );
}

function Feature({ icon, title, description, link }) {
    return (
        <div className="col col--4" style={{ marginBottom: "1.5rem" }}>
            <div className={styles.featureCard}>
                <div className={styles.featureIconWrap}>{icon}</div>
                <h3 className={styles.featureTitle}>
                    <Link to={link}>{title}</Link>
                </h3>
                <p className={styles.featureDesc}>{description}</p>
            </div>
        </div>
    );
}

const features = [
    {
        icon: "🛡️",
        title: "Zero Trust, No Code Changes",
        description:
            "ZTA enforces intent-scoped authorization at the sidecar level. Your agents and MCP servers need no SDK or configuration changes.",
        link: "/concepts/mas",
    },
    {
        icon: "☸️",
        title: "Kubernetes-Native",
        description:
            "Deploy via Helm. Configure via CRDs. Works with Istio or Cilium. Fits naturally into your existing cloud-native stack.",
        link: "/installation/control-plane",
    },
    {
        icon: "🔍",
        title: "Deterministic + Semantic Checks",
        description:
            "Choose rule-based validation, AI-powered intent matching, or both — configured per Multi-Agent System, not per service.",
        link: "/concepts/deterministic-checks",
    },
];

const quickLinks = [
    { label: "Core Concepts", to: "/concepts/mas" },
    { label: "Architecture", to: "/architecture/architecture-overview" },
    { label: "Installation", to: "/installation/prerequisites" },
    { label: "Demo Walkthrough", to: "/demo/walkthrough" },
    { label: "Explorer UI", to: "/explorer-ui" },
];

export default function Home() {
    return (
        <Layout
            title="ZTA Docs"
            description="Zero Trust for Multi-Agent Systems — Kubernetes-native authorization platform"
        >
            <HomepageHeader />
            <main>
                <section className={styles.featuresSection}>
                    <div className="container">
                        <div className="row">
                            {features.map((props, idx) => (
                                <Feature key={idx} {...props} />
                            ))}
                        </div>
                    </div>
                </section>
                <div className={styles.quickLinks}>
                    <span>Quick links</span>
                    {quickLinks.map(({ label, to }) => (
                        <Link key={to} to={to}>{label}</Link>
                    ))}
                </div>
            </main>
        </Layout>
    );
}
