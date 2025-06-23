#!/usr/bin/env node

import { EmailDatabase } from './lib/database.js';
import { stringify } from 'csv-stringify/sync';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';
import { slugify, logger } from './lib/utils.js';

// Get __dirname equivalent for ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class TalkExporter {
  private database: EmailDatabase;
  private dataDir: string;

  constructor() {
    this.database = new EmailDatabase();
    this.dataDir = path.join(__dirname, '..', 'data');
  }

  async run() {
    try {
      logger.section('📊 Talk Export Tool');

      // Create data directory if it doesn't exist
      if (!fs.existsSync(this.dataDir)) {
        fs.mkdirSync(this.dataDir, { recursive: true });
        logger.done(`Created data directory: ${this.dataDir}`);
      }

      // Get all talks
      const talks = this.database.getAllTalks();
      logger.debug(`Found ${talks.length} talks to export\n`);

      // Export each talk
      for (const talk of talks) {
        await this.exportTalk(talk);
      }

      logger.success(`\n✅ Export complete! Files saved to: ${this.dataDir}`);

    } catch (error) {
      logger.error(`Error: ${error}`);
      process.exit(1);
    } finally {
      this.database.close();
    }
  }

  private async exportTalk(talk: { talk_title: string; talk_url: string; signup_count: number }) {
    const slug = slugify(talk.talk_title);
    const filename = `${slug}.csv`;
    const filepath = path.join(this.dataDir, filename);

    logger.info(`Exporting: ${talk.talk_title}`);
    logger.debug(`  → ${filename} (${talk.signup_count} signups)`);

    // Get all signups for this talk
    const signups = this.database.getSignupsForTalk(talk.talk_title);

    // Prepare CSV data
    const csvData = signups.map((signup: any) => ({
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
    logger.done(`Exported ${signups.length} emails`);
  }
}

// CLI entry point
if (import.meta.url === `file://${process.argv[1]}`) {
  const exporter = new TalkExporter();
  exporter.run();
}