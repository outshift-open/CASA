import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import styles from './index.module.css';

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title">{siteConfig.title}</h1>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/installation/prerequisites">
            Get Started →
          </Link>
          <Link
            className="button button--outline button--lg"
            style={{ marginLeft: '1rem', color: 'white', borderColor: 'white' }}
            to="/architecture/architecture-overview">
            Architecture
          </Link>
        </div>
      </div>
    </header>
  );
}

function Feature({ title, description, link }) {
  return (
    <div className={clsx('col col--4')}>
      <div className="padding-horiz--md padding-vert--md">
        <h3>
          <Link to={link}>{title}</Link>
        </h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

const features = [
  {
    title: 'Zero Trust, No Code Changes',
    description:
      'ZTA enforces intent-scoped authorization at the sidecar level. Your agents and MCP servers need no SDK or configuration changes.',
    link: '/concepts/mas',
  },
  {
    title: 'Kubernetes-Native',
    description:
      'Deploy via Helm. Configure via CRDs. Works with Istio or Cilium. Fits naturally into your existing cloud-native stack.',
    link: '/installation/control-plane',
  },
  {
    title: 'Deterministic + Semantic Checks',
    description:
      'Choose rule-based validation, AI-powered intent matching, or both — configured per Multi-Agent System, not per service.',
    link: '/concepts/deterministic-checks',
  },
];

export default function Home() {
  return (
    <Layout
      title="ZTA Docs"
      description="Zero Trust for Multi-Agent Systems — Kubernetes-native authorization platform">
      <HomepageHeader />
      <main>
        <section style={{ padding: '2rem 0' }}>
          <div className="container">
            <div className="row">
              {features.map((props, idx) => (
                <Feature key={idx} {...props} />
              ))}
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
