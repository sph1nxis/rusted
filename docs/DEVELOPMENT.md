# Development Guide

This document describes the structure of the `rusted` project, the theme generation process, and the development workflow.

## Project structure

```text
rusted/
├── assets
│   ├── code-snippets
│   │   ├── go
│   │   │   └── preview.go
│   │   ├── main.rs
│   │   ├── preview.c
│   │   ├── preview.cpp
│   │   ├── preview.py
│   │   └── preview.ts
│   └── images
│       ├── icon.png
│       ├── palette.png
│       ├── preview-c.png
│       ├── preview-cpp.png
│       ├── preview-go.png
│       ├── preview-python.png
│       ├── preview-rust.png
│       └── preview-typescript.png
├── CHANGELOG.md
├── docs
│   └── DEVELOPMENT.md
├── LICENSE
├── package.json
├── README.md
├── scripts
│   ├── build.py
│   └── watch.py
└── src
    ├── languages/
    ├── palette.json
    ├── semantic-tokens.json
    ├── terminal-colors.json
    └── workbench-colors.json

```

### `assets/`

Contains files used for project documentation and preview images.

#### `assets/code-snippets/`

Contains the source code snippets used to generate the screenshots shown in the README and on the VS Code Marketplace.

The snippets are included in the repository so that the preview examples can be reproduced and kept together with the theme source.

#### `assets/images/`

Contains the theme icon, palette preview, and screenshots for supported languages.

### `.vscode/`

Contains VS Code workspace configuration used for extension development.

#### `.vscode/launch.json`

Defines the launch configuration for the **Extension Development Host**, allowing the theme extension to be launched directly from the project with `F5`.

### `src/`

Contains the source files used to generate the final VS Code theme.

#### `src/palette.json`

Defines the color palette used throughout the theme.

Theme components reference palette colors instead of defining the same colors repeatedly. This makes it possible to change a palette color in one place and propagate the change to the generated theme.

#### `src/languages/`

Contains language-specific syntax highlighting definitions.

Each file contains token rules for a particular language. The directory is intentionally kept separate from the main theme definition so that language support can be developed and maintained independently.

`base.json` contains common token rules shared between languages.

#### `src/semantic-tokens.json`

Contains semantic token color definitions.

These definitions are used together with VS Code's semantic highlighting system to provide more precise highlighting where a language server supplies semantic information.

#### `src/terminal-colors.json`

Defines colors used by the integrated terminal.

#### `src/workbench-colors.json`

Defines colors for the VS Code workbench UI, including editors, sidebars, panels, menus, and other interface elements.

### `scripts/`

Contains the Python scripts used during development.

#### `scripts/build.py`

Builds the final VS Code theme from the source files in `src/`.

The build process resolves palette references, combines the language definitions and other theme components, and writes the generated theme to:

```text
themes/rusted.json
```

The generated file is the theme file referenced by `package.json`.

#### `scripts/watch.py`

Runs the build process automatically when source files change.

The watcher monitors the relevant project files and triggers a new build after changes are detected. It uses only the Python standard library and does not require additional Python packages.

## Theme generation

The source files are separated into several components instead of being maintained as one large theme JSON file.

The general flow is:

```text
src/
 ├── palette.json
 ├── language definitions
 ├── semantic-tokens.json
 ├── terminal-colors.json
 └── workbench-colors.json
          │
          ▼
     scripts/build.py
          │
          ▼
   themes/rusted.json
```

`themes/rusted.json` is generated output and should not be edited manually.

Changes to the theme should normally be made in the corresponding source file under `src/`.

## Build

The project uses Python 3 for its build system.

Build the theme with:

```bash
python3 scripts/build.py
```

The generated `themes/rusted.json` will be updated in the project directory.

The project also provides an npm wrapper:

```bash
npm run build
```

The npm command invokes the same Python build script.

## Watch mode

For active theme development, watch mode can be used to rebuild the theme automatically:

```bash
python3 scripts/watch.py
```

or:

```bash
npm run watch
```

The watcher monitors source files and runs the build script when changes are detected.

Watch mode is intended to be used together with the **Extension Development Host**. This allows changes to the generated theme to be previewed directly in a development instance of VS Code.

## Extension Development Host

The project includes a VS Code launch configuration for developing and testing the extension.

Press `F5` while the project is open in VS Code to launch an **Extension Development Host**.

The development host loads `rusted` directly from the project directory rather than from the installed extension directory.

The development workflow can therefore be used as follows:

1. Start the theme watcher.
2. Press `F5` in VS Code.
3. The Extension Development Host opens with the development version of `rusted`.
4. Edit the source files under `src/`.
5. `watch.py` automatically rebuilds `themes/rusted.json`.
6. The changes can be previewed in the Extension Development Host.

This makes it possible to iterate on colors and syntax highlighting without repeatedly packaging and installing a `.vsix` file.

The launch configuration is stored in:

```text
.vscode/launch.json
```

and uses the current project directory as the extension development path.

## Adding language support

Language-specific highlighting rules are stored in `src/languages/`.

To add or extend language support:

1. Create or modify the corresponding language definition in `src/languages/`.
2. Reference colors from `palette.json` where appropriate.
3. Run the build script or start watch mode.
4. Test the resulting theme in the Extension Development Host.
5. Add or update a preview snippet under `assets/code-snippets/` if a new language preview is needed.
6. Add or update the corresponding screenshot under `assets/images/` if necessary.

The generated theme should not be edited directly.

## Packaging

After building the theme, package the extension with VSCE:

```bash
vsce package
```

This creates a `.vsix` package in the project root.

Before packaging a release, make sure the generated theme is up to date and test the extension locally.

A typical local build and packaging workflow is:

```bash
python3 scripts/build.py
vsce package
```

The resulting `.vsix` file can be installed manually in VS Code for testing.

## Development workflow

A typical development cycle is:

```text
Edit source files
      │
      ▼
Run watch.py
      │
      ▼
Press F5
      │
      ▼
Extension Development Host
      │
      ▼
Preview changes
      │
      ▼
Build final theme
      │
      ▼
Package with VSCE
      │
      ▼
Test .vsix
```

For simple changes, `watch.py` can be used during development. Before creating a release package, run a clean build explicitly and verify the generated theme.

## Generated files

The following file is generated by the build system:

```text
themes/rusted.json
```

It is the final VS Code theme definition consumed by the extension.

Source files under `src/` should be treated as the authoritative definitions for the theme. Changes should be made there rather than directly in the generated file.
