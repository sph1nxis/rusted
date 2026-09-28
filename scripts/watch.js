const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const root = path.join(__dirname, '..');
const srcDir = path.join(root, 'src');
const languagesDir = path.join(srcDir, 'languages');

let timer = null;
let building = false;
let pending = false;

function timestamp() {
    return new Date().toLocaleTimeString('en-GB', {
        hour12: false
    });
}

function build() {
    if (building) {
        pending = true;
        return;
    }

    building = true;

    const child = spawn(process.execPath, [path.join(__dirname, 'build.js')], {
        stdio: 'inherit'
    });

    child.on('close', () => {
        building = false;

        if (pending) {
            pending = false;
            build();
        }
    });
}

function scheduleBuild() {
    clearTimeout(timer);
    timer = setTimeout(build, 100);
}

function watch(directory) {
    fs.watch(directory, (event, filename) => {
        if (!filename || !filename.endsWith('.json')) {
            return;
        }

        console.log(
            `[${timestamp()}] Changed: ${path.relative(root, path.join(directory, filename))}`
        );

        scheduleBuild();
    });
}

console.log('Watching src/*.json and src/languages/*.json...\n');

build();
watch(srcDir);
watch(languagesDir);
