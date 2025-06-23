// Generated script for workflow e7cab492-d623-4e14-996a-228aaea207c6
// Generated at 2025-06-23T22:19:31.477Z

import { Stagehand, type ConstructorParams } from "@browserbasehq/stagehand";
import { z } from 'zod';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';
import { EmailDatabase } from './lib/database.js';
import type { EmailRecord } from './lib/database.js';

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
  
  // Database file path (same as prepare-email-sync uses)
  DB_PATH: path.join(__dirname, 'email_processing.db'),
  
  // Sync group to process (if specified)
  SYNC_GROUP_ID: process.argv.find(arg => arg.startsWith('--sync-group='))?.split('=')[1],
  
  // Reset database (clear all processed records)
  RESET_DB: process.argv.includes('--reset-db'),
};


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
    console.log(`Database stats: ${initialStats.total} total, ${initialStats.successful} successful, ${initialStats.failed} failed, ${initialStats.dryRun} dry-run, ${initialStats.pending} pending`);
    
    // Get unprocessed emails from database
    let emailRecords: EmailRecord[];
    if (CONFIG.SYNC_GROUP_ID) {
      const syncGroupId = parseInt(CONFIG.SYNC_GROUP_ID);
      console.log(`Processing emails for sync group #${syncGroupId}`);
      emailRecords = database.getUnprocessedEmails(syncGroupId);
      
      const groupStats = database.getSyncGroupStats(syncGroupId);
      console.log(`Sync group stats: ${groupStats.total} total, ${groupStats.successful} successful, ${groupStats.pending} pending`);
    } else {
      console.log(`Processing all unprocessed emails`);
      emailRecords = database.getUnprocessedEmails();
    }
    
    if (emailRecords.length === 0) {
      console.log("No unprocessed email records found.");
      return { success: true, message: "All emails have been processed" };
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