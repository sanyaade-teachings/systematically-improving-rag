#!/usr/bin/env node

import { EmailDatabase } from './lib/database.js';
import { stringify } from 'csv-stringify/sync';
import * as fs from 'fs';
import * as path from 'path';
import chalk from 'chalk';
import { fileURLToPath } from 'url';

// Get __dirname equivalent for ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Function to slugify talk titles
function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '') // Remove special characters
    .replace(/\s+/g, '-')      // Replace spaces with hyphens
    .replace(/-+/g, '-')       // Replace multiple hyphens with single hyphen
    .trim();
}

class TalkExporter {
  private database: EmailDatabase;
  private dataDir: string;

  constructor() {
    this.database = new EmailDatabase();
    this.dataDir = path.join(__dirname, '..', 'data');
  }

  async run() {
    try {
      console.log(chalk.blue.bold('\n📊 Talk Export Tool\n'));

      // Create data directory if it doesn't exist
      if (!fs.existsSync(this.dataDir)) {
        fs.mkdirSync(this.dataDir, { recursive: true });
        console.log(chalk.green(`✓ Created data directory: ${this.dataDir}`));
      }

      // Get all talks
      const talks = this.database.getAllTalks();
      console.log(chalk.gray(`Found ${talks.length} talks to export\n`));

      // Export each talk
      for (const talk of talks) {
        await this.exportTalk(talk);
      }

      console.log(chalk.green.bold(`\n✅ Export complete! Files saved to: ${this.dataDir}`));

    } catch (error) {
      console.error(chalk.red('Error:'), error);
      process.exit(1);
    } finally {
      this.database.close();
    }
  }

  private async exportTalk(talk: { talk_title: string; talk_url: string; signup_count: number }) {
    const slug = slugify(talk.talk_title);
    const filename = `${slug}.csv`;
    const filepath = path.join(this.dataDir, filename);

    console.log(chalk.blue(`Exporting: ${talk.talk_title}`));
    console.log(chalk.gray(`  → ${filename} (${talk.signup_count} signups)`));

    // Get all signups for this talk
    const signups = this.database.getSignupsForTalk(talk.talk_title);

    // Prepare CSV data
    const csvData = signups.map(signup => ({
      email: signup.email,
      talk_title: signup.talk_title,
      talk_url: signup.talk_url,
      source: signup.source,
      created_at: signup.created_at,
      imported_at: signup.imported_at
    }));

    // Generate CSV
    const csv = stringify(csvData, {
      header: true,
      columns: ['email', 'talk_title', 'talk_url', 'source', 'created_at', 'imported_at']
    });

    // Write to file
    fs.writeFileSync(filepath, csv);
    console.log(chalk.green(`  ✓ Exported ${signups.length} emails`));
  }
}

// CLI entry point
if (import.meta.url === `file://${process.argv[1]}`) {
  const exporter = new TalkExporter();
  exporter.run();
}