#!/usr/bin/env python3

import os
import re
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Tuple


def extract_date_from_filename(filename: str) -> Optional[datetime]:
    """
    Extract the date from a filename in the format GMT20250204-XXXXXX.

    Args:
        filename: The filename to extract the date from

    Returns:
        A datetime object representing the date or None if no date found
    """
    date_match = re.search(r"GMT(\d{8})-?(\d{6})?", filename)
    if not date_match:
        return None

    date_str = date_match.group(1)
    time_str = date_match.group(2) if date_match.group(2) else "000000"

    try:
        # Parse the date from the format YYYYMMDD and time from HHMMSS
        date_obj = datetime.strptime(f"{date_str}{time_str}", "%Y%m%d%H%M%S")
        return date_obj
    except ValueError:
        return None


def determine_week(date: datetime) -> Optional[int]:
    """
    Determine which week a date belongs to based on Tuesday/Thursday sessions only.

    Args:
        date: The date to check

    Returns:
        Week number (1-6) or None if date doesn't fit known weeks
    """
    # Only classify files from Tuesdays and Thursdays
    weekday = date.weekday()
    if weekday != 1 and weekday != 3:  # 1 is Tuesday, 3 is Thursday
        return None

    # Week 1: Feb 4 (Tue), Feb 6 (Thu), 2025
    if date.date() in [datetime(2025, 2, 4).date(), datetime(2025, 2, 6).date()]:
        return 1

    # Week 2: Feb 11 (Tue), Feb 13 (Thu), 2025
    elif date.date() in [datetime(2025, 2, 11).date(), datetime(2025, 2, 13).date()]:
        return 2

    # Week 3: Feb 18 (Tue), Feb 20 (Thu), 2025
    elif date.date() in [datetime(2025, 2, 18).date(), datetime(2025, 2, 20).date()]:
        return 3

    # Week 4: Feb 25 (Tue), Feb 27 (Thu), 2025
    elif date.date() in [datetime(2025, 2, 25).date(), datetime(2025, 2, 27).date()]:
        return 4

    # Week 5: Mar 4 (Tue), Mar 6 (Thu), 2025
    elif date.date() in [datetime(2025, 3, 4).date(), datetime(2025, 3, 6).date()]:
        return 5

    # Week 6: Mar 11 (Tue), Mar 13 (Thu), 2025
    elif date.date() in [datetime(2025, 3, 11).date(), datetime(2025, 3, 13).date()]:
        return 6

    else:
        return None


def generate_clean_filename(filename: str, date_obj: datetime) -> str:
    """
    Generate a clean filename in the format 'MM-DD-YYYY-HHMM.ext'.

    Args:
        filename: Original filename
        date_obj: Datetime object with the date/time information

    Returns:
        A clean filename with date and time information
    """
    # Extract the file extension
    _, ext = os.path.splitext(filename)

    # Format the date/time as MM-DD-YYYY-HHMM
    clean_name = date_obj.strftime("%m-%d-%Y-%H%M")

    # Add session info if in the original name
    session_type = ""
    if "Recording" in filename:
        session_type = "-session"
    elif "merged" in filename:
        session_type = "-merged"
    elif "newChat" in filename:
        session_type = "-chat"

    # Combine the parts
    return f"{clean_name}{session_type}{ext}"


def rename_existing_files_in_week_folders(base_dir: str) -> None:
    """
    Rename files that are already in week folders to the clean format.

    Args:
        base_dir: Base directory where week folders are located
    """
    # Process week folders 1-6
    for week in range(1, 7):
        week_dir = os.path.join(base_dir, f"week{week}")
        if not os.path.exists(week_dir):
            continue

        # Get all files in the week folder
        files = [
            f for f in os.listdir(week_dir) if os.path.isfile(os.path.join(week_dir, f))
        ]

        # Rename each file if it has a date pattern
        for file in files:
            # Skip already renamed files (MM-DD-YYYY format)
            if re.match(r"\d{2}-\d{2}-\d{4}", file):
                continue

            date_obj = extract_date_from_filename(file)
            if date_obj:
                old_path = os.path.join(week_dir, file)
                new_filename = generate_clean_filename(file, date_obj)
                new_path = os.path.join(week_dir, new_filename)

                if old_path != new_path and not os.path.exists(new_path):
                    try:
                        os.rename(old_path, new_path)
                        print(f"Renamed existing file: {file} -> {new_filename}")
                    except Exception as e:
                        print(f"Error renaming {file}: {e}")


def get_transcript_files(directory: str) -> List[str]:
    """
    Get all transcript files from a directory with more flexible matching.

    Args:
        directory: Directory to search for transcript files

    Returns:
        List of filenames that are likely transcripts
    """
    all_files = [
        f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))
    ]

    transcript_files = []

    for file in all_files:
        lower_name = file.lower()
        # More flexible matching of transcript files
        if (
            (
                ("transcript" in lower_name)
                or (
                    "recording" in lower_name
                    and any(ext in lower_name for ext in [".vtt", ".txt", ".srt"])
                )
                or (
                    lower_name.startswith("gmt")
                    and any(ext in lower_name for ext in [".vtt", ".txt", ".srt"])
                )
            )
            and not file.endswith(".mp4")
            and not file.endswith(".mp3")
        ):
            transcript_files.append(file)

    return transcript_files


def organize_files() -> None:
    """
    Organize transcript files into week folders based on Tuesdays and Thursdays only.
    Moves files from both the current directory and downloads directory,
    cleaning up originals after successful move.
    """
    # Get current directory and downloads directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    downloads_dir = os.path.expanduser("~/Downloads")

    # Print all files in downloads for debugging
    print("Files in Downloads directory:")
    all_download_files = os.listdir(downloads_dir)
    for file in sorted(all_download_files):
        if "transcript" in file.lower() or "recording" in file.lower():
            print(f"  - {file}")
    print()

    # First, rename existing files in week folders
    rename_existing_files_in_week_folders(base_dir)

    # Get transcript files with more flexible matching
    curr_files = get_transcript_files(base_dir)
    dl_files = get_transcript_files(downloads_dir)

    print(f"Found {len(curr_files)} transcript files in current directory")
    print(f"Found {len(dl_files)} transcript files in Downloads directory")
    print()

    # Process all files from both directories
    files_by_week: Dict[int, List[Tuple[str, str, Optional[datetime]]]] = {
        1: [],
        2: [],
        3: [],
        4: [],
        5: [],
        6: [],
    }
    unclassified: List[Tuple[str, str, Optional[datetime]]] = []

    # Process current directory files
    for file in curr_files:
        date = extract_date_from_filename(file)
        if not date:
            unclassified.append((file, base_dir, None))
            continue

        week = determine_week(date)
        if not week:
            unclassified.append((file, base_dir, date))
            continue

        files_by_week[week].append((file, base_dir, date))

    # Process downloads directory files
    for file in dl_files:
        date = extract_date_from_filename(file)
        if not date:
            print(f"No date found in filename: {file}")
            unclassified.append((file, downloads_dir, None))
            continue

        week = determine_week(date)
        if not week:
            day_name = date.strftime("%A")
            print(f"File from {day_name} (not Tue/Thu): {file}")
            unclassified.append((file, downloads_dir, date))
            continue

        files_by_week[week].append((file, downloads_dir, date))

    # Move files to their week folders
    for week, file_info_list in files_by_week.items():
        week_dir = os.path.join(base_dir, f"week{week}")
        if not os.path.exists(week_dir):
            os.makedirs(week_dir)

        for file, source_dir, date_obj in file_info_list:
            src = os.path.join(source_dir, file)

            # Generate a cleaner filename if we have date info
            if date_obj:
                new_filename = generate_clean_filename(file, date_obj)
            else:
                new_filename = file

            dst = os.path.join(week_dir, new_filename)

            # Check if destination exists
            if not os.path.exists(dst):
                try:
                    # Move the file instead of copying
                    shutil.move(src, dst)
                    print(f"Moved and renamed {file} -> {new_filename} (Week {week})")
                except Exception as e:
                    print(f"Error moving {file}: {e}")
            else:
                # If destination exists, remove the source file
                try:
                    os.remove(src)
                    print(
                        f"Removed duplicate {file} (already exists as {new_filename})"
                    )
                except Exception as e:
                    print(f"Error removing {file}: {e}")

    # Handle unclassified files
    other_dir = os.path.join(base_dir, "other")
    if unclassified and not os.path.exists(other_dir):
        os.makedirs(other_dir)

    for file, source_dir, date_obj in unclassified:
        src = os.path.join(source_dir, file)

        # Generate a cleaner filename if we have date info
        if date_obj:
            new_filename = generate_clean_filename(file, date_obj)
        else:
            new_filename = file

        dst = os.path.join(other_dir, new_filename)

        if not os.path.exists(dst):
            try:
                shutil.move(src, dst)
                print(
                    f"Moved unclassified file to other folder: {file} -> {new_filename}"
                )
            except Exception as e:
                print(f"Error moving unclassified file {file}: {e}")
        else:
            try:
                os.remove(src)
                print(f"Removed duplicate unclassified file: {file}")
            except Exception as e:
                print(f"Error removing {file}: {e}")

    # Print a summary
    print("\nFile Organization Summary:")
    for week in range(1, 7):
        week_dir = os.path.join(base_dir, f"week{week}")
        if os.path.exists(week_dir):
            files = [
                f
                for f in os.listdir(week_dir)
                if os.path.isfile(os.path.join(week_dir, f))
            ]
            if files:
                print(f"Week {week}: {len(files)} files")
                for file in sorted(files):
                    print(f"  - {file}")

    if os.path.exists(other_dir):
        files = [
            f
            for f in os.listdir(other_dir)
            if os.path.isfile(os.path.join(other_dir, f))
        ]
        if files:
            print(f"\nOther files: {len(files)}")
            for file in sorted(files):
                print(f"  - {file}")


if __name__ == "__main__":
    organize_files()
