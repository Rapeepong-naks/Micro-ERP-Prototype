const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const source = __dirname;
const output = path.join(source, '../dist/user-test-site');
const fonts = path.join(output, 'fonts');
const assets = path.join(output, 'assets');
fs.mkdirSync(fonts, {recursive: true});
fs.mkdirSync(assets, {recursive: true});
for (const oldFile of ['GoogleSans.ttf', 'OFL.txt']) fs.rmSync(path.join(fonts, oldFile), {force: true});
const sourceFiles = ['index.html', 'app.js', 'styles.css', 'device.css', 'fonts/NotoSansThai.ttf', 'assets/khonnai-wordmark.png'];
for (const file of ['index.html', 'app.js', 'styles.css', 'device.css']) {
  fs.copyFileSync(path.join(source, file), path.join(output, file));
}
fs.copyFileSync(path.join(source, 'fonts/NotoSansThai.ttf'), path.join(fonts, 'NotoSansThai.ttf'));
fs.copyFileSync(path.join(source, 'fonts/OFL-NotoSansThai.txt'), path.join(fonts, 'OFL-NotoSansThai.txt'));
fs.copyFileSync(path.join(source, 'assets/khonnai-wordmark.png'), path.join(assets, 'khonnai-wordmark.png'));
const sha256 = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const sourceSha256 = Object.fromEntries(sourceFiles.map(file => [file, sha256(path.join(source, file))]));
fs.writeFileSync(path.join(output, 'build.json'), JSON.stringify({
  label: 'current user-test build',
  builtAt: new Date().toISOString(),
  source: 'prototype/',
  sourceSha256
}, null, 2));
console.log(`Static user-test site ready: ${output}`);
