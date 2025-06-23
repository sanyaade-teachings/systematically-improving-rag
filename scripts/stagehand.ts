// Generated script for workflow e7cab492-d623-4e14-996a-228aaea207c6
// Generated at 2025-06-23T22:19:31.477Z

import { Stagehand, type ConstructorParams } from "@browserbasehq/stagehand";
import { z } from 'zod';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';
import Database from 'better-sqlite3';

// Get __dirname equivalent for ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration options
const CONFIG = {
  // Set to true to do a dry run (no actual form submissions)
  DRY_RUN: process.env.DRY_RUN === 'true' || process.argv.includes('--dry-run'),
  
  // Limit number of emails to process (set to 0 for no limit)
  LIMIT: process.env.LIMIT ? parseInt(process.env.LIMIT) : (process.argv.includes('--test') ? 3 : 0),
  
  // Delay between requests in milliseconds
  DELAY_MS: process.env.DELAY_MS ? parseInt(process.env.DELAY_MS) : 2000,
  
  // Database file path
  DB_PATH: path.join(__dirname, 'email_processing.db'),
  
  // Reset database (clear all processed records)
  RESET_DB: process.argv.includes('--reset-db'),
};

// Define the structure of each email record
interface EmailRecord {
  email: string;
  maven_url: string;
  talk_title: string;
}

// Database functions
class EmailDatabase {
  private db: any;

  constructor(dbPath: string) {
    this.db = new Database(dbPath);
    this.initDatabase();
  }

  private initDatabase() {
    // Create the processed_emails table if it doesn't exist
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS processed_emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        maven_url TEXT NOT NULL,
        talk_title TEXT NOT NULL,
        processed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        success BOOLEAN NOT NULL,
        error_message TEXT,
        dry_run BOOLEAN DEFAULT FALSE,
        UNIQUE(email, maven_url)
      )
    `);
  }

  isProcessed(email: string, mavenUrl: string): boolean {
    const result = this.db.prepare(`
      SELECT id FROM processed_emails 
      WHERE email = ? AND maven_url = ? AND success = 1
    `).get(email, mavenUrl);
    return !!result;
  }

  markAsProcessed(email: string, mavenUrl: string, talkTitle: string, success: boolean, errorMessage?: string, dryRun: boolean = false) {
    try {
      this.db.prepare(`
        INSERT OR REPLACE INTO processed_emails 
        (email, maven_url, talk_title, success, error_message, dry_run)
        VALUES (?, ?, ?, ?, ?, ?)
      `).run(email, mavenUrl, talkTitle, success ? 1 : 0, errorMessage || null, dryRun ? 1 : 0);
    } catch (error) {
      console.warn(`Failed to mark email as processed: ${error}`);
    }
  }

  getStats() {
    const total = this.db.prepare('SELECT COUNT(*) as count FROM processed_emails').get().count;
    const successful = this.db.prepare('SELECT COUNT(*) as count FROM processed_emails WHERE success = 1').get().count;
    const failed = this.db.prepare('SELECT COUNT(*) as count FROM processed_emails WHERE success = 0').get().count;
    const dryRun = this.db.prepare('SELECT COUNT(*) as count FROM processed_emails WHERE dry_run = 1').get().count;
    
    return { total, successful, failed, dryRun };
  }

  reset() {
    this.db.exec('DELETE FROM processed_emails');
    console.log('Database reset - all processed email records cleared');
  }

  close() {
    this.db.close();
  }
}

// Stagehand configuration
const stagehandConfig = (): ConstructorParams => {
  return {
    env: 'BROWSERBASE',
    verbose: 1,
    modelName: 'google/gemini-2.5-flash-preview-05-20',
    modelClientOptions: {
      apiKey: process.env.GOOGLE_API_KEY,
    },
  };
};

// Function to read and parse the JSONL file
function readEmailRecords(filePath: string): EmailRecord[] {
  try {
    const fileContent = fs.readFileSync(filePath, 'utf8');
    const lines = fileContent.trim().split('\n');
    const records: EmailRecord[] = [];
    
    for (const line of lines) {
      if (line.trim()) {
        try {
          const record = JSON.parse(line) as EmailRecord;
          records.push(record);
        } catch (parseError) {
          console.warn(`Failed to parse line: ${line}`, parseError);
        }
      }
    }
    
    return records;
  } catch (error) {
    console.error(`Failed to read file ${filePath}:`, error);
    return [];
  }
}

async function processEmailRecord(stagehand: Stagehand | null, record: EmailRecord, database: EmailDatabase): Promise<boolean> {
  try {
    console.log(`Processing email: ${record.email} for talk: ${record.talk_title}`);
    
    // Check if already processed
    if (database.isProcessed(record.email, record.maven_url)) {
      console.log(`  ✓ Already processed: ${record.email} - skipping`);
      return true;
    }

    if (CONFIG.DRY_RUN) {
      console.log(`  [DRY RUN] Would process: ${record.email}`);
      console.log(`  [DRY RUN] Would navigate to: ${record.maven_url}`);
      console.log(`  [DRY RUN] Would fill email and click submit`);
      
      // Mark as processed in dry run mode
      database.markAsProcessed(record.email, record.maven_url, record.talk_title, true, undefined, true);
      
      // Simulate some processing time
      await new Promise(resolve => setTimeout(resolve, 500));
      console.log(`  [DRY RUN] Successfully simulated: ${record.email}`);
      return true;
    }

    // Real processing (non-dry run)
    if (!stagehand) {
      throw new Error("Stagehand instance required for non-dry run mode");
    }

    const page = stagehand.page;
    if (!page) {
      throw new Error("Failed to get page instance from Stagehand");
    }

    console.log(`  → Navigating to: ${record.maven_url}`);
    await page.goto(record.maven_url);
    
    console.log(`  → Typing email: ${record.email}`);
    await page.act({
      description: `type '${record.email}' into the email input`,
      method: "fill",
      arguments: [record.email],
      selector: "xpath=/html[1]/body[1]/div[1]/div[2]/main[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[3]/div[1]/div[1]/div[2]/div[3]/div[1]/div[1]/div[1]/input[1]"
    });
    
    console.log(`  → Clicking Sign up for free button`);
    await page.act({
      description: "click the Sign up for free button",
      method: "click",
      arguments: [],
      selector: "xpath=/html[1]/body[1]/div[1]/div[2]/main[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[3]/div[1]/div[1]/div[2]/div[3]/div[1]/button[1]"
    });
    
    // Wait between requests
    await new Promise(resolve => setTimeout(resolve, CONFIG.DELAY_MS));
    
    console.log(`  ✓ Successfully processed: ${record.email}`);
    database.markAsProcessed(record.email, record.maven_url, record.talk_title, true);
    return true;
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error(`  ✗ Failed to process email ${record.email}:`, errorMessage);
    database.markAsProcessed(record.email, record.maven_url, record.talk_title, false, errorMessage, CONFIG.DRY_RUN);
    return false;
  }
}

async function runWorkflow() {
  let stagehand: Stagehand | null = null;
  let database: EmailDatabase | null = null;
  
  try {
    // Initialize database
    console.log(`Initializing database: ${CONFIG.DB_PATH}`);
    database = new EmailDatabase(CONFIG.DB_PATH);
    
    // Reset database if requested
    if (CONFIG.RESET_DB) {
      database.reset();
    }
    
    // Show current database stats
    const initialStats = database.getStats();
    console.log(`Database stats: ${initialStats.total} total, ${initialStats.successful} successful, ${initialStats.failed} failed, ${initialStats.dryRun} dry-run`);
    
    // Read email records from JSONL file
    const jsonlPath = path.join(__dirname, 'missing_emails.jsonl');
    console.log(`Reading email records from: ${jsonlPath}`);
    const emailRecords = readEmailRecords(jsonlPath);
    
    if (emailRecords.length === 0) {
      console.log("No email records found or file could not be read.");
      return { success: false, error: "No email records to process" };
    }
    
    // Apply limit if specified
    const recordsToProcess = CONFIG.LIMIT > 0 ? emailRecords.slice(0, CONFIG.LIMIT) : emailRecords;
    console.log(`Found ${emailRecords.length} email records total`);
    console.log(`Will process ${recordsToProcess.length} records${CONFIG.LIMIT > 0 ? ` (limited to ${CONFIG.LIMIT})` : ''}`);
    
    // Show configuration
    console.log(`\nConfiguration:`);
    console.log(`  - DRY_RUN: ${CONFIG.DRY_RUN}`);
    console.log(`  - LIMIT: ${CONFIG.LIMIT || 'No limit'}`);
    console.log(`  - DELAY_MS: ${CONFIG.DELAY_MS}ms`);
    console.log(`  - DB_PATH: ${CONFIG.DB_PATH}`);
    
    // Initialize Stagehand only if not dry run
    if (!CONFIG.DRY_RUN) {
      console.log("\nInitializing Stagehand...");
      stagehand = new Stagehand(stagehandConfig());
      await stagehand.init();
      console.log("Stagehand initialized successfully.");
    } else {
      console.log("\n[DRY RUN MODE] Skipping Stagehand initialization");
    }
    
    // Process each email record
    let successCount = 0;
    let failureCount = 0;
    let skippedCount = 0;
    
    console.log(`\n${'='.repeat(50)}`);
    console.log(`Starting processing...`);
    console.log(`${'='.repeat(50)}`);
    
    for (let i = 0; i < recordsToProcess.length; i++) {
      const record = recordsToProcess[i];
      if (!record) continue;
      
      console.log(`\n[${i + 1}/${recordsToProcess.length}] ${record.email}`);
      
      // Check if already processed (this is also checked in processEmailRecord, but good to show stats)
      if (database.isProcessed(record.email, record.maven_url)) {
        skippedCount++;
        continue;
      }
      
      const success = await processEmailRecord(stagehand, record, database);
      if (success) {
        successCount++;
      } else {
        failureCount++;
      }
    }
    
    // Final stats
    const finalStats = database.getStats();
    console.log(`\n${'='.repeat(50)}`);
    console.log(`Workflow completed!`);
    console.log(`${'='.repeat(50)}`);
    console.log(`This run: ${successCount} successful, ${failureCount} failed, ${skippedCount} skipped`);
    console.log(`Database totals: ${finalStats.successful} successful, ${finalStats.failed} failed, ${finalStats.dryRun} dry-run`);
    
    return { 
      success: true, 
      successCount, 
      failureCount,
      skippedCount,
      totalProcessed: recordsToProcess.length,
      databaseStats: finalStats
    };
  } catch (error) {
    console.error("Workflow failed:", error);
    return { success: false, error };
  } finally {
    // Clean up
    if (database) {
      database.close();
    }
    if (stagehand) {
      console.log("Closing Stagehand connection.");
      try {
        await stagehand.close();
      } catch (err) {
        console.error("Error closing Stagehand:", err);
      }
    }
  }
}

// Single execution
runWorkflow().then((result) => {
  console.log('Execution result:', result);
  process.exit(result.success ? 0 : 1);
});