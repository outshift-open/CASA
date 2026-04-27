# CASA Explorer UI

Modern UI for the CASA (Continuous Agent Semantic Authorization) Authorization Server built with React, TypeScript, and shadcn/ui.

## Tech Stack

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Yarn v2** - Package manager
- **shadcn/ui** - UI component library with green theme
- **TanStack Query** - Data fetching and caching
- **Axios** - HTTP client
- **Tailwind CSS** - Styling

## Prerequisites

- Node.js 20.19+ or 22.12+
- Yarn v2

## Getting Started

### Local Development

1. Install dependencies:

```bash
yarn install
```

2. Copy the environment file:

```bash
cp .env.sample .env
```

3. Update the `.env` file with your API base URL:

```
VITE_API_BASE_URL=http://127.0.0.1:8000
```

4. Start the development server:

```bash
yarn dev
```

The application will be available at `http://localhost:5173`.

### Docker

You can run the UI with Docker using the provided Dockerfile:

```bash
# Build the image
docker build -f deployments/docker/Dockerfile.ui -t casa-explorer-ui .

# Run the container
docker run -p 1234:80 casa-explorer-ui
```

The application will be available at `http://localhost:1234`.

### Docker Compose

Run the UI with Docker Compose:

```bash
cd deployments/docker-compose
docker-compose -f docker-compose.ui.yml up
```

Make sure you have the UI environment file configured:

- `casa-explorer-ui/.env` for the UI configuration

The UI will be available at http://localhost:1234 and will connect to the API server configured in your `.env` file.

## Available Scripts

- `yarn dev` - Start development server
- `yarn build` - Build for production
- `yarn preview` - Preview production build
- `yarn lint` - Run ESLint

## Features

- **Application Management** - Create, read, update, and delete applications (agents, clients, MCP servers)
- **Responsive Sidebar** - Collapsible navigation with icon mode
- **Modern UI** - Clean, accessible design with shadcn/ui components
- **Real-time Updates** - Automatic cache invalidation with TanStack Query
- **Type Safety** - Full TypeScript support

## License

Copyright © 2026 Cisco

```js
export default defineConfig([
    globalIgnores(['dist']),
    {
        files: ['**/*.{ts,tsx}'],
        extends: [
            // Other configs...

            // Remove tseslint.configs.recommended and replace with this
            tseslint.configs.recommendedTypeChecked,
            // Alternatively, use this for stricter rules
            tseslint.configs.strictTypeChecked,
            // Optionally, add this for stylistic rules
            tseslint.configs.stylisticTypeChecked

            // Other configs...
        ],
        languageOptions: {
            parserOptions: {
                project: ['./tsconfig.node.json', './tsconfig.app.json'],
                tsconfigRootDir: import.meta.dirname
            }
            // other options...
        }
    }
]);
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x';
import reactDom from 'eslint-plugin-react-dom';

export default defineConfig([
    globalIgnores(['dist']),
    {
        files: ['**/*.{ts,tsx}'],
        extends: [
            // Other configs...
            // Enable lint rules for React
            reactX.configs['recommended-typescript'],
            // Enable lint rules for React DOM
            reactDom.configs.recommended
        ],
        languageOptions: {
            parserOptions: {
                project: ['./tsconfig.node.json', './tsconfig.app.json'],
                tsconfigRootDir: import.meta.dirname
            }
            // other options...
        }
    }
]);
```
