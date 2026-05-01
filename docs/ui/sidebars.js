/**
 * Copyright 2026 Cisco Systems, Inc. and its affiliates
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

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  docs: [
    'overview',
    'explorer-ui',
    {
      type: 'category',
      label: 'Architecture',
      items: [
        'architecture/architecture-overview',
        'architecture/runtime',
        'architecture/sidecar',
        'architecture/ebpf',
        'architecture/traces',
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
        'installation/install-runtime',
        'installation/install-demo-mas',
      ],
    },
    {
      type: 'category',
      label: 'Configuration',
      items: [
        'configuration/runtime-values',
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
    {
      type: 'category',
      label: 'Developer',
      items: [
        'dev/local-setup',
      ],
    },
  ],
};

module.exports = sidebars;
