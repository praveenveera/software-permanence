import * as fs from 'fs';
import * as readline from 'readline';

async function verifyExports(filePath: string): Promise<void> {
  const fileStream = fs.createReadStream(filePath);
  const rl = readline.createInterface({
    input: fileStream,
    crlfDelay: Infinity
  });

  for await (const line of rl) {
    const match = line.match(/^(export\s+)?(function|class)\s+([a-zA-Z_][a-zA-Z0-9_]*)/);
    if (match) {
      const type = match[2].toUpperCase();
      const name = match[3];
      console.log(`[${type}] ${name}`);
    }
  }
}

const args = process.argv.slice(2);
if (args.length < 1) {
  console.error("Usage: ts-node verify_exports.ts <file_path>");
  process.exit(1);
}
verifyExports(args[0]).catch(err => console.error(err));
