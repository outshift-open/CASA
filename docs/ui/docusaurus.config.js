/**
 * Copyright 2026 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// @ts-check
const { themes: prismThemes } = require("prism-react-renderer");

/** @type {import('@docusaurus/types').Config} */
const config = {
    title: "CASA — Continuous Agent Semantic Authorization",
    tagline:
        "Cloud-native Zero Trust authorization for MAS, with no code changes required.",
    favicon: "img/favicon.ico",

    url: "https://outshift-open.github.io",
    baseUrl: "/",

    organizationName: "outshift-open",
    projectName: "identity-auth-server",

    onBrokenLinks: "warn",
    onBrokenMarkdownLinks: "warn",

    i18n: {
        defaultLocale: "en",
        locales: ["en"],
    },

    markdown: {
        mermaid: true,
    },

    themes: ["@docusaurus/theme-mermaid"],

    presets: [
        [
            "classic",
            /** @type {import('@docusaurus/preset-classic').Options} */
            ({
                docs: {
                    sidebarPath: require.resolve("./sidebars.js"),
                    editUrl:
                        "https://github.com/outshift-open/identity-auth-server/tree/main/docs/ui/",
                    routeBasePath: "/",
                },
                blog: false,
                theme: {
                    customCss: require.resolve("./src/css/custom.css"),
                },
            }),
        ],
    ],

    themeConfig:
        /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
        ({
            image: "img/casa-social-card.png",
            navbar: {
                title: "CASA",
                logo: {
                    alt: "CASA Logo",
                    src: "img/logo.svg",
                },
                items: [
                    {
                        type: "docSidebar",
                        sidebarId: "docs",
                        position: "left",
                        label: "Docs",
                    },
                    {
                        href: "https://github.com/outshift-open/identity-auth-server",
                        label: "GitHub",
                        position: "right",
                    },
                ],
            },
            footer: {
                style: "dark",
                links: [
                    {
                        title: "Docs",
                        items: [
                            { label: "Overview", to: "/overview" },
                            {
                                label: "Quick Start",
                                to: "/installation/prerequisites",
                            },
                            {
                                label: "Architecture",
                                to: "/architecture/architecture-overview",
                            },
                        ],
                    },
                    {
                        title: "Community",
                        items: [
                            {
                                label: "GitHub Issues",
                                href: "https://github.com/outshift-open/identity-auth-server/issues",
                            },
                            {
                                label: "Contributing",
                                to: "/contributing",
                            },
                        ],
                    },
                    {
                        title: "More",
                        items: [
                            {
                                label: "GitHub",
                                href: "https://github.com/outshift-open/identity-auth-server",
                            },
                        ],
                    },
                ],
                copyright: `Copyright © ${new Date().getFullYear()} Cisco Systems, Inc. Built with Docusaurus.`,
            },
            prism: {
                theme: prismThemes.github,
                darkTheme: prismThemes.dracula,
                additionalLanguages: ["bash", "yaml", "go", "python"],
            },
            colorMode: {
                defaultMode: "light",
                disableSwitch: false,
                respectPrefersColorScheme: true,
            },
        }),
};

module.exports = config;
