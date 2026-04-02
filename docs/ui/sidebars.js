// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  docs: [
    'overview',
    {
      type: 'category',
      label: 'Architecture',
      items: [
        'architecture/architecture-overview',
        'architecture/control-plane',
        'architecture/sidecar',
        'architecture/ebpf',
      ],
    },
    {
      type: 'category',
      label: 'Concepts',
      items: [
        'concepts/mas',
        'concepts/crds',
        'concepts/token-flow',
        'concepts/deterministic-checks',
        'concepts/semantic-checks',
      ],
    },
    {
      type: 'category',
      label: 'Installation',
      items: [
        'installation/prerequisites',
        'installation/install-control-plane',
        'installation/install-demo-mas',
      ],
    },
    {
      type: 'category',
      label: 'Configuration',
      items: [
        'configuration/control-plane-values',
        'configuration/mas-values',
        'configuration/crds-reference',
      ],
    },
    {
      type: 'category',
      label: 'Deployment Modes',
      items: [
        'deployment-modes/istio',
        'deployment-modes/cilium',
      ],
    },
    {
      type: 'category',
      label: 'Demo',
      items: [
        'demo/walkthrough',
      ],
    },
    {
      type: 'category',
      label: 'Operations',
      items: [
        'operations/troubleshooting',
        'operations/upgrade',
      ],
    },
    {
      type: 'category',
      label: 'Contributing',
      items: [
        'contributing/contributing',
      ],
    },
  ],
};

module.exports = sidebars;
