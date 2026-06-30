const fs = require('fs');

function parseExports(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    const exports = [];

    lines.forEach(line => {
      const match = line.match(/^(export\s+)?(function|class)\s+([a-zA-Z_][a-zA-Z0-9_]*)/);
      if (match) {
        exports.push(`${match[2]}: ${match[3]}`);
      }
    });

    console.log(`File: ${filePath}`);
    console.log("Exports found:");
    exports.forEach(item => console.log(`  - ${item}`));
  } catch (err) {
    console.error(`Error: ${err.message}`);
  }
}

const args = process.argv.slice(2);
if (args.length < 1) {
  console.error("Usage: node parse.js <file_path>");
  process.exit(1);
}

parseExports(args[0]);
