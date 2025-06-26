import Database from 'better-sqlite3';
import * as path from 'path';
import { fileURLToPath } from 'url';

// Get __dirname equivalent for ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export interface EmailRecord {
  email: string;
  maven_url: string;
  talk_title: string;
}

export interface SyncGroup {
  id?: number;
  created_at?: string;
  talk1_title: string;
  talk1_url: string;
  talk2_title: string;
  talk2_url: string;
  overlap_count: number;
  missing_from_talk1: number;
  missing_from_talk2: number;
}

export interface ProcessedEmail {
  id?: number;
  email: string;
  maven_url: string;
  talk_title: string;
  processed_at?: string;
  success: boolean;
  error_message?: string;
  dry_run: boolean;
  sync_group_id?: number;
}

export interface TalkSignup {
  id?: number;
  email: string;
  talk_title: string;
  talk_url: string;
  source: string;
  created_at: string;
  imported_at?: string;
  csv_filename?: string;
}

export class EmailDatabase {
  private db: any;
  private dbPath: string;

  constructor(dbPath?: string) {
    this.dbPath = dbPath || path.join(__dirname, '..', 'email_processing.db');
    this.db = new Database(this.dbPath);
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
        sync_group_id INTEGER,
        UNIQUE(email, maven_url),
        FOREIGN KEY (sync_group_id) REFERENCES sync_groups(id)
      )
    `);

    // Create the sync_groups table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS sync_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        talk1_title TEXT NOT NULL,
        talk1_url TEXT NOT NULL,
        talk2_title TEXT NOT NULL,
        talk2_url TEXT NOT NULL,
        overlap_count INTEGER,
        missing_from_talk1 INTEGER,
        missing_from_talk2 INTEGER,
        status TEXT DEFAULT 'pending'
      )
    `);

    // Create the signups table to track all signups from CSV imports
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS signups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        talk_title TEXT NOT NULL,
        talk_url TEXT NOT NULL,
        source TEXT NOT NULL,
        created_at TEXT NOT NULL,
        imported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        csv_filename TEXT,
        UNIQUE(email, talk_url)
      )
    `);

    // Create indexes for better performance
    this.db.exec(`
      CREATE INDEX IF NOT EXISTS idx_processed_emails_sync_group 
      ON processed_emails(sync_group_id);
      
      CREATE INDEX IF NOT EXISTS idx_signups_email 
      ON signups(email);
      
      CREATE INDEX IF NOT EXISTS idx_signups_talk 
      ON signups(talk_title);
    `);
  }

  // Sync group methods
  createSyncGroup(syncGroup: SyncGroup): number {
    // Check if a sync group already exists for these talks (in either order)
    const existing = this.db.prepare(`
      SELECT id FROM sync_groups 
      WHERE (talk1_title = ? AND talk2_title = ?) 
         OR (talk1_title = ? AND talk2_title = ?)
    `).get(
      syncGroup.talk1_title, syncGroup.talk2_title,
      syncGroup.talk2_title, syncGroup.talk1_title
    );
    
    if (existing) {
      throw new Error(`Sync group already exists for these talks (ID: ${existing.id})`);
    }
    
    const stmt = this.db.prepare(`
      INSERT INTO sync_groups 
      (talk1_title, talk1_url, talk2_title, talk2_url, overlap_count, missing_from_talk1, missing_from_talk2)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `);
    
    const result = stmt.run(
      syncGroup.talk1_title,
      syncGroup.talk1_url,
      syncGroup.talk2_title,
      syncGroup.talk2_url,
      syncGroup.overlap_count,
      syncGroup.missing_from_talk1,
      syncGroup.missing_from_talk2
    );
    
    return result.lastInsertRowid;
  }

  getSyncGroups(): SyncGroup[] {
    return this.db.prepare(`
      SELECT * FROM sync_groups 
      ORDER BY created_at DESC
    `).all();
  }

  // Email processing methods
  isProcessed(email: string, mavenUrl: string): boolean {
    const result = this.db.prepare(`
      SELECT id FROM processed_emails 
      WHERE email = ? AND maven_url = ? AND success = 1
    `).get(email, mavenUrl);
    return !!result;
  }

  markAsProcessed(
    email: string, 
    mavenUrl: string, 
    talkTitle: string, 
    success: boolean, 
    errorMessage?: string, 
    dryRun: boolean = false,
    syncGroupId?: number
  ) {
    try {
      this.db.prepare(`
        INSERT OR REPLACE INTO processed_emails 
        (email, maven_url, talk_title, success, error_message, dry_run, sync_group_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `).run(
        email, 
        mavenUrl, 
        talkTitle, 
        success ? 1 : 0, 
        errorMessage || null, 
        dryRun ? 1 : 0,
        syncGroupId || null
      );
    } catch (error) {
      console.warn(`Failed to mark email as processed: ${error}`);
    }
  }

  // Bulk insert for sync preparation
  bulkInsertPendingEmails(emails: EmailRecord[], syncGroupId: number) {
    const stmt = this.db.prepare(`
      INSERT OR IGNORE INTO processed_emails 
      (email, maven_url, talk_title, success, dry_run, sync_group_id)
      VALUES (?, ?, ?, 0, 0, ?)
    `);

    const insertMany = this.db.transaction((emails: EmailRecord[]) => {
      for (const email of emails) {
        stmt.run(email.email, email.maven_url, email.talk_title, syncGroupId);
      }
    });

    insertMany(emails);
  }

  // Get unprocessed emails for a specific sync group
  getUnprocessedEmails(syncGroupId?: number): EmailRecord[] {
    let query = `
      SELECT email, maven_url, talk_title 
      FROM processed_emails 
      WHERE success = 0 AND dry_run = 0
    `;
    
    if (syncGroupId !== undefined) {
      query += ` AND sync_group_id = ?`;
      return this.db.prepare(query).all(syncGroupId);
    }
    
    return this.db.prepare(query).all();
  }

  getStats() {
    const total = this.db.prepare('SELECT COUNT(*) as count FROM processed_emails').get().count;
    const successful = this.db.prepare('SELECT COUNT(*) as count FROM processed_emails WHERE success = 1').get().count;
    const failed = this.db.prepare('SELECT COUNT(*) as count FROM processed_emails WHERE success = 0').get().count;
    const dryRun = this.db.prepare('SELECT COUNT(*) as count FROM processed_emails WHERE dry_run = 1').get().count;
    const pending = this.db.prepare('SELECT COUNT(*) as count FROM processed_emails WHERE success = 0 AND dry_run = 0').get().count;
    
    return { total, successful, failed, dryRun, pending };
  }

  getSyncGroupStats(syncGroupId: number) {
    const total = this.db.prepare('SELECT COUNT(*) as count FROM processed_emails WHERE sync_group_id = ?').get(syncGroupId).count;
    const successful = this.db.prepare('SELECT COUNT(*) as count FROM processed_emails WHERE sync_group_id = ? AND success = 1').get(syncGroupId).count;
    const failed = this.db.prepare('SELECT COUNT(*) as count FROM processed_emails WHERE sync_group_id = ? AND success = 0 AND dry_run = 0').get(syncGroupId).count;
    const pending = this.db.prepare('SELECT COUNT(*) as count FROM processed_emails WHERE sync_group_id = ? AND success = 0 AND dry_run = 0').get(syncGroupId).count;
    
    return { total, successful, failed, pending };
  }

  reset() {
    this.db.exec('DELETE FROM processed_emails');
    this.db.exec('DELETE FROM sync_groups');
    console.log('Database reset - all records cleared');
  }

  // Talk signup methods
  importTalkSignups(signups: TalkSignup[]) {
    const stmt = this.db.prepare(`
      INSERT OR REPLACE INTO signups 
      (email, talk_title, talk_url, source, created_at, csv_filename)
      VALUES (?, ?, ?, ?, ?, ?)
    `);

    const importMany = this.db.transaction((signups: TalkSignup[]) => {
      let imported = 0;
      for (const signup of signups) {
        try {
          stmt.run(
            signup.email,
            signup.talk_title,
            signup.talk_url,
            signup.source,
            signup.created_at,
            signup.csv_filename
          );
          imported++;
        } catch (error: any) {
          // Skip duplicates silently
          if (!error.message.includes('UNIQUE constraint failed')) {
            console.warn(`Failed to import signup: ${error}`);
          }
        }
      }
      return imported;
    });

    return importMany(signups);
  }

  getTalkSignupStats() {
    const stats = this.db.prepare(`
      SELECT 
        COUNT(DISTINCT email) as unique_emails,
        COUNT(DISTINCT talk_title) as unique_talks,
        COUNT(*) as total_signups,
        COUNT(DISTINCT csv_filename) as csv_files_imported
      FROM signups
    `).get();

    const talkStats = this.db.prepare(`
      SELECT 
        talk_title,
        talk_url,
        COUNT(DISTINCT email) as signup_count
      FROM signups
      GROUP BY talk_title, talk_url
      ORDER BY signup_count DESC
    `).all();

    return { ...stats, talks: talkStats };
  }

  getLatestCSVFiles(limit: number = 5) {
    return this.db.prepare(`
      SELECT DISTINCT csv_filename, MAX(imported_at) as last_imported
      FROM signups
      WHERE csv_filename IS NOT NULL
      GROUP BY csv_filename
      ORDER BY last_imported DESC
      LIMIT ?
    `).all(limit);
  }

  // Get signups for calculating sync groups from the signups table
  getSignupsForTalks(talk1Title: string, talk2Title: string) {
    const talk1Signups = this.db.prepare(`
      SELECT DISTINCT email 
      FROM signups 
      WHERE talk_title = ?
    `).all(talk1Title).map((row: any) => row.email);

    const talk2Signups = this.db.prepare(`
      SELECT DISTINCT email 
      FROM signups 
      WHERE talk_title = ?
    `).all(talk2Title).map((row: any) => row.email);

    return { talk1Signups, talk2Signups };
  }

  // Get all signups for a specific talk
  getSignupsForTalk(talkTitle: string) {
    return this.db.prepare(`
      SELECT 
        email,
        talk_title,
        talk_url,
        source,
        created_at,
        imported_at
      FROM signups 
      WHERE talk_title = ?
      ORDER BY created_at DESC
    `).all(talkTitle);
  }

  // Get all unique talks
  getAllTalks() {
    return this.db.prepare(`
      SELECT DISTINCT 
        talk_title,
        talk_url,
        COUNT(DISTINCT email) as signup_count
      FROM signups
      GROUP BY talk_title, talk_url
      ORDER BY signup_count DESC
    `).all();
  }

  // Get successfully processed emails to exclude from sync preparation
  getSuccessfullyProcessedEmails(): Set<string> {
    const results = this.db.prepare(`
      SELECT DISTINCT email || '|' || maven_url as email_url_pair
      FROM processed_emails
      WHERE success = 1
    `).all();
    
    return new Set(results.map((r: any) => r.email_url_pair));
  }

  // Get comprehensive cross-table statistics
  getCrossTableStats() {
    // Basic counts
    const signupsCount = this.db.prepare('SELECT COUNT(*) as count FROM signups').get().count;
    const processedCount = this.db.prepare('SELECT COUNT(*) as count FROM processed_emails').get().count;
    const successCount = this.db.prepare('SELECT COUNT(*) as count FROM processed_emails WHERE success = 1').get().count;
    const failedCount = this.db.prepare('SELECT COUNT(*) as count FROM processed_emails WHERE success = 0 AND dry_run = 0').get().count;
    const pendingCount = this.db.prepare('SELECT COUNT(*) as count FROM processed_emails WHERE success = 0 AND dry_run = 0').get().count;

    // Cross-reference: signups that have been processed
    const processedSignups = this.db.prepare(`
      SELECT COUNT(DISTINCT s.email || '|' || s.talk_url) as count
      FROM signups s
      INNER JOIN processed_emails p ON s.email = p.email AND s.talk_url = p.maven_url
      WHERE p.success = 1
    `).get().count;

    // Signups not yet in processed_emails at all
    const unprocessedSignups = this.db.prepare(`
      SELECT COUNT(DISTINCT s.email || '|' || s.talk_url) as count
      FROM signups s
      LEFT JOIN processed_emails p ON s.email = p.email AND s.talk_url = p.maven_url
      WHERE p.email IS NULL
    `).get().count;

    // Emails in processed_emails but not in signups (shouldn't happen in normal flow)
    const orphanedProcessed = this.db.prepare(`
      SELECT COUNT(DISTINCT p.email || '|' || p.maven_url) as count
      FROM processed_emails p
      LEFT JOIN signups s ON p.email = s.email AND p.maven_url = s.talk_url
      WHERE s.email IS NULL
    `).get().count;

    return {
      signups: {
        total: signupsCount,
        processed: processedSignups,
        unprocessed: unprocessedSignups
      },
      processed_emails: {
        total: processedCount,
        successful: successCount,
        failed: failedCount,
        pending: pendingCount,
        orphaned: orphanedProcessed
      }
    };
  }

  // Deduplicate processed_emails table (remove duplicates keeping the most recent successful one)
  deduplicateProcessedEmails() {
    // First, get duplicates
    const duplicates = this.db.prepare(`
      SELECT email, maven_url, COUNT(*) as count
      FROM processed_emails
      GROUP BY email, maven_url
      HAVING COUNT(*) > 1
    `).all();

    if (duplicates.length === 0) {
      return { duplicatesFound: 0, removed: 0 };
    }

    let removed = 0;
    const deleteStmt = this.db.prepare(`
      DELETE FROM processed_emails 
      WHERE id IN (
        SELECT id FROM processed_emails 
        WHERE email = ? AND maven_url = ?
        ORDER BY 
          CASE WHEN success = 1 THEN 0 ELSE 1 END,  -- Keep successful ones
          processed_at DESC  -- Keep most recent
        LIMIT -1 OFFSET 1  -- Delete all but the first one
      )
    `);

    const transaction = this.db.transaction(() => {
      for (const dup of duplicates) {
        const result = deleteStmt.run(dup.email, dup.maven_url);
        removed += result.changes;
      }
    });

    transaction();

    return { duplicatesFound: duplicates.length, removed };
  }

  close() {
    this.db.close();
  }
}