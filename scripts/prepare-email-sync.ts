#!/usr/bin/env node

import { parse } from 'csv-parse/sync';
import * as fs from 'fs';
import * as path from 'path';
import inquirer from 'inquirer';
import chalk from 'chalk';
import Table from 'cli-table3';
import { EmailDatabase } from './lib/database.js';
import type { EmailRecord, SyncGroup, TalkSignup } from './lib/database.js';

interface CSVRecord {
  'Created At': string;
  'Users → Email': string;
  'Source': string;
  'All Published Instructor Lightning Lessons - Conten_c77416c3 → Title': string;
  'All Published Instructor Lightning Lessons - Conten_c77416c3 → Public Ll URL': string;
}

interface ParsedRecord {
  created_at: string;
  email: string;
  source: string;
  title: string;
  url: string;
}

interface TalkInfo {
  title: string;
  url: string;
  signupCount: number;
  emails: Set<string>;
}

class EmailSyncCLI {
  private database: EmailDatabase;
  private talks: Map<string, TalkInfo> = new Map();
  private records: ParsedRecord[] = [];
  private csvFilename: string = '';

  constructor() {
    this.database = new EmailDatabase();
  }

  async run(csvPath: string | null, options: { dryRun?: boolean; showSample?: number; autoDetect?: boolean } = {}) {
    try {
      console.log(chalk.blue.bold('\n📧 Email Sync Preparation Tool\n'));

      if (options.dryRun) {
        console.log(chalk.yellow('🔍 DRY RUN MODE - No changes will be saved to database\n'));
      }

      // Auto-detect CSV file if needed
      if (!csvPath || options.autoDetect) {
        csvPath = await this.autoDetectCSV();
        if (!csvPath) {
          console.log(chalk.red('No CSV file selected. Exiting.'));
          return;
        }
      }

      // Parse CSV file
      this.parseCSV(csvPath);
      
      // Import all signups to tracking table
      if (!options.dryRun) {
        this.importSignups(csvPath);
      }
      
      // Show talk summary
      this.showTalkSummary();

      // Interactive selection
      const syncGroup = await this.selectTalksForSync();
      
      if (!syncGroup) {
        console.log(chalk.yellow('\nNo sync group created. Exiting.'));
        return;
      }

      // Calculate and show overlap
      const { missingEmails, overlap } = this.calculateMissingEmails(syncGroup);
      
      // Show sample emails if requested
      if (options.showSample && missingEmails.length > 0) {
        this.showSampleEmails(missingEmails, options.showSample);
      }
      
      // Confirm and save
      const confirmed = await this.confirmSync(syncGroup, missingEmails, overlap, options.dryRun);
      
      if (confirmed && !options.dryRun) {
        this.saveSyncGroup(syncGroup, missingEmails, overlap);
        console.log(chalk.green('\n✅ Sync group created successfully!'));
        console.log(chalk.gray(`Run ${chalk.white('npm run stagehand -- --dry-run')} to test the process.`));
        console.log(chalk.gray(`Run ${chalk.white('npm run stagehand')} to actually process the emails.`));
      } else if (confirmed && options.dryRun) {
        console.log(chalk.yellow('\n[DRY RUN] Would have created sync group with:'));
        console.log(chalk.gray(`  - ${missingEmails.length} emails to process`));
        console.log(chalk.gray(`  - ${syncGroup.missing_from_talk1} emails for "${syncGroup.talk1_title}"`));
        console.log(chalk.gray(`  - ${syncGroup.missing_from_talk2} emails for "${syncGroup.talk2_title}"`));
      } else {
        console.log(chalk.yellow('\nSync cancelled.'));
      }

    } catch (error) {
      console.error(chalk.red('Error:'), error);
      process.exit(1);
    } finally {
      this.database.close();
    }
  }

  private async autoDetectCSV(): Promise<string | null> {
    const homeDir = process.env.HOME || process.env.USERPROFILE || '';
    const downloadsDir = path.join(homeDir, 'Downloads');
    
    console.log(chalk.gray(`Searching for Maven CSV files in: ${downloadsDir}`));
    
    // Find all CSV files matching the pattern
    const files = fs.readdirSync(downloadsDir)
      .filter(file => file.includes('lightning_lesson_signups') && file.endsWith('.csv'))
      .map(file => ({
        path: path.join(downloadsDir, file),
        stats: fs.statSync(path.join(downloadsDir, file))
      }))
      .sort((a, b) => b.stats.mtime.getTime() - a.stats.mtime.getTime()); // Sort by modified time, newest first
    
    if (files.length === 0) {
      console.log(chalk.yellow('No Maven CSV files found in Downloads folder.'));
      return null;
    }
    
    // Show recent imports
    const recentImports = this.database.getLatestCSVFiles(5);
    if (recentImports.length > 0) {
      console.log(chalk.blue('\n📄 Recently imported files:'));
      recentImports.forEach((file: any) => {
        console.log(chalk.gray(`  - ${file.csv_filename} (imported ${new Date(file.last_imported).toLocaleDateString()})`));
      });
    }
    
    // Show available files
    console.log(chalk.blue('\n📁 Available CSV files (sorted by most recent):'));
    const choices = files.slice(0, 10).map((file, index) => ({
      name: `${index + 1}. ${path.basename(file.path)} (${new Date(file.stats.mtime).toLocaleDateString()})`,
      value: file.path,
      short: path.basename(file.path)
    }));
    
    const { csvPath } = await inquirer.prompt([
      {
        type: 'list',
        name: 'csvPath',
        message: 'Select a CSV file to import:',
        choices: [
          ...choices,
          new inquirer.Separator(),
          { name: 'Enter path manually', value: 'manual' }
        ]
      }
    ]);
    
    if (csvPath === 'manual') {
      const { manualPath } = await inquirer.prompt([
        {
          type: 'input',
          name: 'manualPath',
          message: 'Enter the full path to the CSV file:',
          validate: (input) => fs.existsSync(input) || 'File not found'
        }
      ]);
      return manualPath;
    }
    
    return csvPath;
  }

  private parseCSV(csvPath: string) {
    console.log(chalk.gray(`Reading CSV file: ${csvPath}`));
    this.csvFilename = path.basename(csvPath);
    
    if (!fs.existsSync(csvPath)) {
      throw new Error(`CSV file not found: ${csvPath}`);
    }

    const fileContent = fs.readFileSync(csvPath, 'utf8');
    const rawRecords = parse(fileContent, {
      columns: true,
      skip_empty_lines: true
    }) as CSVRecord[];

    // Parse and normalize records
    this.records = rawRecords.map(record => ({
      created_at: record['Created At'],
      email: record['Users → Email'],
      source: record['Source'],
      title: record['All Published Instructor Lightning Lessons - Conten_c77416c3 → Title'],
      url: record['All Published Instructor Lightning Lessons - Conten_c77416c3 → Public Ll URL']
    }));

    // Group by talk
    for (const record of this.records) {
      if (!this.talks.has(record.title)) {
        this.talks.set(record.title, {
          title: record.title,
          url: record.url,
          signupCount: 0,
          emails: new Set()
        });
      }
      
      const talk = this.talks.get(record.title)!;
      talk.emails.add(record.email);
      talk.signupCount = talk.emails.size;
    }

    console.log(chalk.green(`✓ Parsed ${this.records.length} records`));
    console.log(chalk.green(`✓ Found ${this.talks.size} unique talks`));
  }

  private importSignups(csvPath: string) {
    console.log(chalk.gray('\nImporting signups to tracking table...'));
    
    const signups: TalkSignup[] = this.records.map(record => ({
      email: record.email,
      talk_title: record.title,
      talk_url: record.url,
      source: record.source,
      created_at: record.created_at,
      csv_filename: this.csvFilename
    }));
    
    const imported = this.database.importTalkSignups(signups);
    console.log(chalk.green(`✓ Imported ${imported} signups (duplicates were skipped)`));
    
    // Show current stats
    const stats = this.database.getTalkSignupStats();
    console.log(chalk.gray(`Total unique emails: ${stats.unique_emails}`));
    console.log(chalk.gray(`Total unique talks: ${stats.unique_talks}`));
    console.log(chalk.gray(`Total signups tracked: ${stats.total_signups}`));
  }

  private showTalkSummary() {
    console.log(chalk.blue.bold('\n📊 Talk Summary\n'));

    const table = new Table({
      head: ['#', 'Talk Title', 'Signups', 'URL'],
      colWidths: [5, 60, 10, 30],
      wordWrap: true
    });

    const sortedTalks = Array.from(this.talks.values())
      .sort((a, b) => b.signupCount - a.signupCount);

    sortedTalks.forEach((talk, index) => {
      table.push([
        index + 1,
        talk.title,
        talk.signupCount,
        talk.url
      ]);
    });

    console.log(table.toString());
  }

  private async selectTalksForSync(): Promise<SyncGroup | null> {
    const talkChoices = Array.from(this.talks.values())
      .sort((a, b) => b.signupCount - a.signupCount)
      .map((talk, index) => ({
        name: `${index + 1}. ${talk.title} (${talk.signupCount} signups)`,
        value: talk.title,
        short: talk.title
      }));

    const { talk1 } = await inquirer.prompt([
      {
        type: 'list',
        name: 'talk1',
        message: 'Select the first talk:',
        choices: talkChoices,
        pageSize: 10
      }
    ]);

    const { talk2 } = await inquirer.prompt([
      {
        type: 'list',
        name: 'talk2',
        message: 'Select the second talk:',
        choices: talkChoices.filter(choice => choice.value !== talk1),
        pageSize: 10
      }
    ]);

    const talk1Info = this.talks.get(talk1)!;
    const talk2Info = this.talks.get(talk2)!;

    return {
      talk1_title: talk1Info.title,
      talk1_url: talk1Info.url,
      talk2_title: talk2Info.title,
      talk2_url: talk2Info.url,
      overlap_count: 0,
      missing_from_talk1: 0,
      missing_from_talk2: 0
    };
  }

  private calculateMissingEmails(syncGroup: SyncGroup) {
    const talk1 = this.talks.get(syncGroup.talk1_title)!;
    const talk2 = this.talks.get(syncGroup.talk2_title)!;

    const talk1Emails = talk1.emails;
    const talk2Emails = talk2.emails;

    // Calculate overlap
    const overlapEmails = new Set<string>();
    for (const email of talk1Emails) {
      if (talk2Emails.has(email)) {
        overlapEmails.add(email);
      }
    }

    // Calculate missing emails
    const missingFromTalk1: EmailRecord[] = [];
    const missingFromTalk2: EmailRecord[] = [];

    // Emails in talk2 but not in talk1 (should get talk1 URL)
    for (const email of talk2Emails) {
      if (!talk1Emails.has(email)) {
        missingFromTalk1.push({
          email,
          maven_url: syncGroup.talk1_url,
          talk_title: syncGroup.talk1_title
        });
      }
    }

    // Emails in talk1 but not in talk2 (should get talk2 URL)
    for (const email of talk1Emails) {
      if (!talk2Emails.has(email)) {
        missingFromTalk2.push({
          email,
          maven_url: syncGroup.talk2_url,
          talk_title: syncGroup.talk2_title
        });
      }
    }

    // Update sync group stats
    syncGroup.overlap_count = overlapEmails.size;
    syncGroup.missing_from_talk1 = missingFromTalk1.length;
    syncGroup.missing_from_talk2 = missingFromTalk2.length;

    return {
      missingEmails: [...missingFromTalk1, ...missingFromTalk2],
      overlap: {
        count: overlapEmails.size,
        percentage1: (overlapEmails.size / talk1Emails.size * 100).toFixed(2),
        percentage2: (overlapEmails.size / talk2Emails.size * 100).toFixed(2)
      }
    };
  }

  private showSampleEmails(missingEmails: EmailRecord[], sampleSize: number) {
    console.log(chalk.blue.bold(`\n📋 Sample Emails (showing ${Math.min(sampleSize, missingEmails.length)} of ${missingEmails.length})\n`));
    
    const table = new Table({
      head: ['Email', 'Will Receive', 'Talk Title'],
      colWidths: [35, 30, 45],
      wordWrap: true
    });

    const sample = missingEmails.slice(0, sampleSize);
    sample.forEach(record => {
      table.push([
        record.email,
        record.maven_url,
        record.talk_title
      ]);
    });

    console.log(table.toString());
  }

  private async confirmSync(syncGroup: SyncGroup, missingEmails: EmailRecord[], overlap: any, isDryRun?: boolean) {
    console.log(chalk.blue.bold('\n📈 Sync Analysis\n'));

    const table = new Table();
    table.push(
      [chalk.bold('Talk 1'), syncGroup.talk1_title],
      [chalk.bold('Talk 2'), syncGroup.talk2_title],
      ['', ''],
      [chalk.bold('Overlap'), `${overlap.count} emails`],
      ['% of Talk 1', `${overlap.percentage1}%`],
      ['% of Talk 2', `${overlap.percentage2}%`],
      ['', ''],
      [chalk.bold('Missing from Talk 1'), `${syncGroup.missing_from_talk1} emails`],
      [chalk.bold('Missing from Talk 2'), `${syncGroup.missing_from_talk2} emails`],
      ['', ''],
      [chalk.bold('Total to sync'), `${missingEmails.length} emails`]
    );

    console.log(table.toString());

    // Check existing database stats
    const dbStats = this.database.getStats();
    if (dbStats.pending > 0) {
      console.log(chalk.yellow(`\n⚠️  Warning: ${dbStats.pending} emails are already pending in the database.`));
    }

    const message = isDryRun 
      ? 'Do you want to simulate creating this sync group? (DRY RUN)'
      : 'Do you want to create this sync group?';

    const { confirm } = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'confirm',
        message,
        default: true
      }
    ]);

    return confirm;
  }

  private saveSyncGroup(syncGroup: SyncGroup, missingEmails: EmailRecord[], overlap: any) {
    console.log(chalk.gray('\nSaving to database...'));

    try {
      // Create sync group
      const syncGroupId = this.database.createSyncGroup(syncGroup);
      
      // Bulk insert missing emails
      this.database.bulkInsertPendingEmails(missingEmails, syncGroupId);

      // Show final stats
      const groupStats = this.database.getSyncGroupStats(syncGroupId);
      console.log(chalk.green(`✓ Created sync group #${syncGroupId}`));
      console.log(chalk.green(`✓ Added ${groupStats.total} emails to process`));
    } catch (error: any) {
      if (error.message.includes('Sync group already exists')) {
        console.log(chalk.red('\n❌ Error: ' + error.message));
        console.log(chalk.yellow('This pair of talks has already been synced.'));
        console.log(chalk.gray('Use a different pair or reset the database with: npm run stagehand -- --reset-db'));
      } else {
        throw error;
      }
    }
  }
}

// CLI entry point
if (import.meta.url === `file://${process.argv[1]}`) {
  const args = process.argv.slice(2);
  
  // Parse command line options
  let csvPath: string | null = null;
  const options: { dryRun?: boolean; showSample?: number; autoDetect?: boolean } = {};
  
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--dry-run') {
      options.dryRun = true;
    } else if (arg === '--show-sample') {
      const nextArg = args[++i];
      options.showSample = parseInt(nextArg || '10');
    } else if (!arg.startsWith('--')) {
      csvPath = arg;
    }
  }
  
  // If no CSV path provided, enable auto-detection
  if (!csvPath) {
    options.autoDetect = true;
  }
  
  const cli = new EmailSyncCLI();
  cli.run(csvPath, options);
}