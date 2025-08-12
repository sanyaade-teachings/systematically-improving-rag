# Cohort 2 Office Hours Transcript Organization

This directory contains organized transcripts from the Cohort 2 office hours sessions.

## Organization Structure

Transcripts are organized into weekly folders based on session dates:

- `week1/`: February 4 (Tuesday) and February 6 (Thursday), 2025
- `week2/`: February 11 (Tuesday) and February 13 (Thursday), 2025
- `week3/`: February 18 (Tuesday) and February 20 (Thursday), 2025
- `week4/`: February 25 (Tuesday) and February 27 (Thursday), 2025
- `week5/`: March 4 (Tuesday) and March 6 (Thursday), 2025
- `week6/`: March 11 (Tuesday) and March 13 (Thursday), 2025
- `other/`: Files from non-Tuesday/Thursday dates or files without date information

## Generating Summary Files Using Cursor

You can use Cursor's AI capabilities to generate summary files from the transcript files. These summaries organize the content into a Q&A format for easier reference.

### Steps to Generate a Summary:

1. **Open Cursor and navigate to the repository**

2. **Open the transcript files for the week you want to summarize**
   - For example, to create a Week 1 summary, open the transcript files from the `week1/` folder

3. **Create a new file**
   - Create `week#-summary.md` in the office-hours directory (e.g., `week1-summary.md`)

4. **Use Cursor's AI composer (CTRL+K or CMD+K)**
   - In the composer, enter a prompt like:

   ```
   @[transcript-file-1] @[transcript-file-2] @[transcript-file-3]

   Create a summary file that extracts all Q&A pairs from these transcripts in the same format as the existing summary files.
   ```

   - For example:

   ```
   @02-04-2025-1353-merged.txt @02-04-2025-1744-merged.txt @02-06-2025-1854-merged.txt

   Create a summary file that extracts all Q&A pairs from these transcripts in the same format as week3-summary.md
   ```

5. **Review and edit the generated content**
   - Cursor may need multiple attempts to generate all content
   - You can ask it to "check if anything is missing and add that back" to ensure comprehensive coverage

6. **Save the file**
   - The completed summary will be saved in the format consistent with other summary files

### Tips for Better Summaries:

- Reference an existing summary file (like `week3-summary.md`) as a format example
- Be specific about including all questions and answers from the transcripts
- If the summary seems incomplete, ask Cursor to review specific portions of the transcripts again
- Organize questions thematically when possible for easier reference

## File Naming Convention

Files are renamed using a consistent format:

```
MM-DD-YYYY-HHMM-type.ext
```

Where:

- `MM-DD-YYYY`: Month, day, and year of the session
- `HHMM`: Hour and minute of the session (24-hour format)
- `type`: Type of file (session, merged, chat)
- `ext`: File extension (.vtt, .txt, etc.)

Examples:

- `02-04-2025-1353-session.vtt`: Transcript from February 4, 2025 at 1:53 PM
- `02-18-2025-1349-merged.txt`: Merged transcript from February 18, 2025 at 1:49 PM
- `02-20-2025-1857-session.txt`: Transcript from February 20, 2025 at 6:57 PM

## Types of Files

- **session**: Original recording transcripts (VTT or TXT format)
- **chat**: Chat messages from the session
- **merged**: Combined transcript of recording and chat

## Using the Transcript Organization Script

The `move-files.py` script handles organizing and renaming transcript files. It:

1. Checks both current directory and Downloads folder for transcript files
2. Extracts date and time information from filenames
3. Determines which week each file belongs to
4. Renames files to the consistent naming format
5. Moves files to the appropriate week folder
6. Places non-Tuesday/Thursday files in the "other" folder

To run the script:

```bash
python3 move-files.py
```

The script will:

- Show which files were found and where they were moved
- Remove duplicate files
- Print a summary of files in each week folder

## Adding New Transcripts

When new transcripts are downloaded:

1. Save them to your Downloads folder
2. Run the `move-files.py` script
3. The script will automatically organize and rename all new transcript files

The script handles various transcript file formats and naming patterns, including:

- Files with "transcript" in the name
- Files with "recording" in the name (ending with .vtt, .txt, .srt)
- Files starting with "GMT" followed by a date (ending with .vtt, .txt, .srt)

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

[Enroll in the Free 6-Day Email Course](https://improvingrag.com/){ .md-button .md-button--primary }

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
