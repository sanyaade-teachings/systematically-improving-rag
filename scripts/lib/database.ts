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

    // Create an index for better performance
    this.db.exec(`
      CREATE INDEX IF NOT EXISTS idx_processed_emails_sync_group 
      ON processed_emails(sync_group_id)
    `);
  }

  // Sync group methods
  createSyncGroup(syncGroup: SyncGroup): number {
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

  close() {
    this.db.close();
  }
}