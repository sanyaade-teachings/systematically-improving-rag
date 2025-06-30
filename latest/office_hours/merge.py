import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime


def find_matching_files() -> Dict[str, Dict[str, List[str]]]:
    """
    Find all transcript and chat files in office-hours/week* directories.
    Works with the new naming format: MM-DD-YYYY-HHMM-type.ext

    Returns:
        Dictionary mapping week directories to a dictionary of date IDs to lists of files.
    """
    base_dir = Path(__file__).parent
    result = {}

    # Find all week directories
    week_dirs = list(base_dir.glob("week*"))

    for week_dir in week_dirs:
        result[str(week_dir)] = {}

        # Group files by recording ID (date-time)
        for file_path in week_dir.glob("*"):
            if not file_path.is_file():
                continue

            # Extract the date-time from filename in new format (MM-DD-YYYY-HHMM)
            match = re.match(r"(\d{2}-\d{2}-\d{4}-\d{4})", file_path.name)
            if match:
                recording_id = match.group(1)  # e.g., "02-18-2025-1349"
                if recording_id not in result[str(week_dir)]:
                    result[str(week_dir)][recording_id] = []
                result[str(week_dir)][recording_id].append(str(file_path))

    return result


def extract_datetime(recording_id: str) -> Tuple[str, str]:
    """
    Extract date and time from recording ID in new format.

    Args:
        recording_id: ID like "02-18-2025-1349"

    Returns:
        Tuple of (date_string, time_string)
    """
    # Parse the MM-DD-YYYY-HHMM format
    match = re.match(r"(\d{2})-(\d{2})-(\d{4})-(\d{2})(\d{2})", recording_id)

    if match:
        month, day, year, hour, minute = match.groups()

        # Format date as YYYY-MM-DD
        formatted_date = f"{year}-{month}-{day}"

        # Format time as HH:MM:00
        formatted_time = f"{hour}:{minute}:00"

        return formatted_date, formatted_time

    return "unknown-date", "unknown-time"


def merge_files(files: List[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Find and read the transcript and chat files based on file extensions.
    .vtt files contain the conversation transcript
    .txt files contain the chat messages

    Args:
        files: List of file paths for a single recording

    Returns:
        Tuple of (transcript_content, chat_content)
    """
    transcript_content = None
    chat_content = None

    # Sort files to prioritize certain file types if there are multiple options
    sorted_files = sorted(files)

    for file_path in sorted_files:
        path = Path(file_path)

        # Skip already merged files
        if "-merged" in file_path.lower():
            continue

        # .vtt files are the conversation transcripts
        if path.suffix.lower() == ".vtt":
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                transcript_content = f.read()

        # .txt files are the chat logs
        elif path.suffix.lower() == ".txt" and "-merged" not in file_path.lower():
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                chat_content = f.read()

    return transcript_content, chat_content


def wrap_in_xml(transcript: Optional[str], chat: Optional[str]) -> str:
    """
    Wrap transcript and chat content in XML tags.

    Args:
        transcript: Content of the transcript file
        chat: Content of the chat file

    Returns:
        Combined content wrapped in XML tags
    """
    result = ""

    if transcript:
        result += "<transcript>\n" + transcript + "\n</transcript>\n\n"

    if chat:
        result += "<chat>\n" + chat + "\n</chat>\n"

    return result


def wrap_in_recording_xml(recording_id: str, content: str) -> str:
    """
    Wrap merged content in recording XML tags with date and time.

    Args:
        recording_id: Recording ID
        content: Merged content

    Returns:
        Content wrapped in recording tags with date and time
    """
    date_str, time_str = extract_datetime(recording_id)

    result = f'<recording id="{recording_id}" date="{date_str}" time="{time_str}">\n'
    result += content
    result += "\n</recording>\n\n"

    return result


def save_merged_content(week_dir: str, recording_id: str, content: str) -> str:
    """
    Save the merged content to a text file using the new naming format.

    Args:
        week_dir: Week directory path
        recording_id: Recording ID (MM-DD-YYYY-HHMM)
        content: Merged content to save

    Returns:
        Path to the created file
    """
    output_path = Path(week_dir) / f"{recording_id}-merged.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created {output_path}")
    return str(output_path)


def create_master_file(all_merged_files: Dict[str, Dict[str, str]]):
    """
    Create a master file containing all merged content.

    Args:
        all_merged_files: Dictionary mapping week directories to recording IDs to merged content
    """
    base_dir = Path(__file__).parent
    master_path = base_dir / "master.txt"

    with open(master_path, "w", encoding="utf-8") as f:
        f.write("<recordings>\n\n")

        for week_dir, recordings in all_merged_files.items():
            week_name = Path(week_dir).name
            f.write(f'<week id="{week_name}">\n\n')

            for recording_id, content in recordings.items():
                wrapped_content = wrap_in_recording_xml(recording_id, content)
                f.write(wrapped_content)

            f.write("</week>\n\n")

        f.write("</recordings>\n")

    print(f"Created master file at {master_path}")


def create_week_summary(week_dir: str, recordings: Dict[str, str]):
    """
    Create a summary markdown file for a week of recordings.

    Args:
        week_dir: Week directory path
        recordings: Dictionary mapping recording IDs to merged content
    """
    week_name = Path(week_dir).name
    summary_path = Path(week_dir) / f"{week_name}-summary.md"

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"# {week_name.capitalize()} Summary\n\n")

        for recording_id, _ in recordings.items():
            date_str, time_str = extract_datetime(recording_id)
            # Convert to more readable format
            try:
                date_obj = datetime.strptime(
                    f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S"
                )
                readable_date = date_obj.strftime("%A, %B %d, %Y at %I:%M %p")
            except ValueError:
                readable_date = f"{date_str} {time_str}"

            f.write(f"## Session on {readable_date}\n\n")
            f.write(f"- [View merged transcript]({recording_id}-merged.txt)\n")

            # Check if we have separate files for this recording
            session_file = Path(week_dir) / f"{recording_id}-session.vtt"
            chat_file = Path(week_dir) / f"{recording_id}-chat.txt"

            if session_file.exists():
                f.write(f"- [View transcript only]({recording_id}-session.vtt)\n")

            if chat_file.exists():
                f.write(f"- [View chat only]({recording_id}-chat.txt)\n")

            f.write("\n")

    print(f"Created {summary_path}")


def main():
    """Main function to process and merge files."""
    file_groups = find_matching_files()
    all_merged_content = {}

    for week_dir, recordings in file_groups.items():
        print(f"Processing {week_dir}...")
        all_merged_content[week_dir] = {}

        for recording_id, files in recordings.items():
            print(f"  Merging files for {recording_id}")
            print(f"    Found files: {[Path(f).name for f in files]}")
            transcript, chat = merge_files(files)

            if transcript or chat:
                merged_content = wrap_in_xml(transcript, chat)
                save_merged_content(week_dir, recording_id, merged_content)
                all_merged_content[week_dir][recording_id] = merged_content
            else:
                print(f"  No content found for {recording_id}")

        # Create a summary for this week
        if recordings:
            create_week_summary(week_dir, all_merged_content[week_dir])

    # Create master file
    create_master_file(all_merged_content)

    print("\nMerge completed successfully!")
    print("Files created:")
    print("1. Individual merged files in each week folder")
    print("2. Week summary files (week*-summary.md)")
    print("3. Master file with all transcripts (master.txt)")


if __name__ == "__main__":
    main()
