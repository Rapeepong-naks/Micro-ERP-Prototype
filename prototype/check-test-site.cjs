const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const source = __dirname;
const site = path.join(source, '../dist/user-test-site');
const manifest = JSON.parse(fs.readFileSync(path.join(site, 'build.json'), 'utf8'));
const sha256 = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
for (const [file, expected] of Object.entries(manifest.sourceSha256)) {
  if (sha256(path.join(source, file)) !== expected) {
    throw new Error(`Test site is older than prototype/${file}. Run node prototype/build-test-site.cjs`);
  }
}
for (const file of ['index.html', 'app.js', 'styles.css', 'device.css', 'fonts/NotoSansThai.ttf', 'fonts/OFL-NotoSansThai.txt', 'assets/khonnai-wordmark.png']) {
  if (!fs.statSync(path.join(site, file)).isFile()) throw new Error(`Missing test-site file: ${file}`);
}
if (sha256(path.join(source, 'app.js')) !== sha256(path.join(site, 'app.js'))) {
  throw new Error('Test site app.js differs from the current prototype');
}
console.log(`Current test-site build verified: ${manifest.builtAt}`);
