// @ts-check
const { themes: prismThemes } = require('prism-react-renderer');

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'ZTA — Zero Trust for Multi-Agent Systems',
  tagline: 'Cloud-native Zero Trust authorization for MAS, with no code changes required.',
  favicon: 'img/favicon.ico',

  url: 'https://cisco-eti.github.io',
  baseUrl: '/',

  organizationName: 'cisco-eti',
  projectName: 'identity-auth-server',

  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  markdown: {
    mermaid: true,
  },

  themes: ['@docusaurus/theme-mermaid'],

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/cisco-eti/identity-auth-server/tree/main/docs/ui/',
          routeBasePath: '/',
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: 'img/zta-social-card.png',
      navbar: {
        title: 'ZTA',
        logo: {
          alt: 'ZTA Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'docs',
            position: 'left',
            label: 'Docs',
          },
          {
            href: 'https://github.com/cisco-eti/identity-auth-server',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              { label: 'Overview', to: '/overview' },
              { label: 'Quick Start', to: '/installation/prerequisites' },
              { label: 'Architecture', to: '/architecture/overview' },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'GitHub Issues',
                href: 'https://github.com/cisco-eti/identity-auth-server/issues',
              },
              {
                label: 'Contributing',
                to: '/contributing',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/cisco-eti/identity-auth-server',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Cisco Systems, Inc. Built with Docusaurus.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
        additionalLanguages: ['bash', 'yaml', 'go', 'python'],
      },
      colorMode: {
        defaultMode: 'light',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
    }),
};

module.exports = config;
