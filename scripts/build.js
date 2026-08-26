const fs = require('fs');
const path = require('path');

function loadJSON(filePath) {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function resolveReferences(obj, palette) {
    if (typeof obj === 'string') {
        return resolveString(obj, palette);
    }
    if (Array.isArray(obj)) {
        return obj.map(item => resolveReferences(item, palette));
    }
    if (obj && typeof obj === 'object') {
        const resolved = {};
        for (const [key, value] of Object.entries(obj)) {
            resolved[key] = resolveReferences(value, palette);
        }
        return resolved;
    }
    return obj;
}

function resolveString(str, palette) {
    return str.replace(/\$\{palette\.([^}]+)\}/g, (match, path) => {
        const value = getNestedValue(palette, path);
        if (value === undefined) {
            console.warn(`Warning: Palette reference not found: ${match}`);
            return match;
        }
        return value;
    });
}

function getNestedValue(obj, path) {
    return path.split('.').reduce((current, key) => {
        return current && current[key] !== undefined ? current[key] : undefined;
    }, obj);
}

function loadLanguageTokens(languagesDir) {
    const tokens = [];

    if (!fs.existsSync(languagesDir)) {
        console.warn(`Warning: Languages directory not found: ${languagesDir}`);
        return tokens;
    }

    const files = fs.readdirSync(languagesDir)
        .filter(file => file.endsWith('.json'))
        .sort();

    for (const file of files) {
        const filePath = path.join(languagesDir, file);
        try {
            const languageTokens = loadJSON(filePath);
            const langName = path.basename(file, '.json');
            console.log(`  Loaded language: ${langName} (${languageTokens.length} scopes)`);
            tokens.push(...languageTokens);
        } catch (err) {
            console.error(`  Error loading ${file}: ${err.message}`);
        }
    }

    return tokens;
}

function build() {
    console.log('Building Tomorrow Night Rusty theme...\n');

    const srcDir = path.join(__dirname, '..', 'src');
    const palette = loadJSON(path.join(srcDir, 'palette.json'));
    console.log('Loaded palette');

    const workbenchColors = loadJSON(path.join(srcDir, 'workbench-colors.json'));
    const resolvedWorkbench = resolveReferences(workbenchColors, palette);
    console.log('Resolved workbench colors');

    console.log('\nLoading language tokens:');
    const languagesDir = path.join(srcDir, 'languages');
    const syntaxTokens = loadLanguageTokens(languagesDir);
    const resolvedSyntax = resolveReferences(syntaxTokens, palette);
    console.log(`\nTotal syntax scopes: ${resolvedSyntax.length}`);

    const semanticTokens = loadJSON(path.join(srcDir, 'semantic-tokens.json'));
    const resolvedSemantic = resolveReferences(semanticTokens, palette);
    console.log('Resolved semantic tokens');

    const terminalColors = loadJSON(path.join(srcDir, 'terminal-colors.json'));
    const resolvedTerminal = resolveReferences(terminalColors, palette);
    console.log('Resolved terminal colors');

    const allColors = {
        ...resolvedWorkbench,
        ...resolvedTerminal
    };

    const theme = {
        name: 'Tomorrow Night Rusty',
        type: 'dark',
        semanticHighlighting: true,
        colors: allColors,
        tokenColors: resolvedSyntax,
        semanticTokenColors: resolvedSemantic
    };

    const themesDir = path.join(__dirname, '..', 'themes');
    if (!fs.existsSync(themesDir)) {
        fs.mkdirSync(themesDir, { recursive: true });
    }

    const themePath = path.join(themesDir, 'tomorrow-night-rusty.json');
    fs.writeFileSync(themePath, JSON.stringify(theme, null, 2));

    console.log(`\nTheme built successfully!`);
    console.log(`Output: ${themePath}`);

    const colorCount = Object.keys(allColors).length;
    const semanticCount = Object.keys(resolvedSemantic).length;

    console.log(`\nTheme stats:`);
    console.log(`   • Colors: ${colorCount}`);
    console.log(`   • Syntax scopes: ${resolvedSyntax.length}`);
    console.log(`   • Semantic tokens: ${semanticCount}`);
}

build();

