#!/usr/bin/env python3
"""
==================================
 Code Combiner with Chunked Output
 + Directory Tree Listing
==================================

Usage:
------
1) **Interactive Mode** (no arguments):
   `python code_combiner.py`
   - Prompts you for directory, output file name, extensions, etc.

2) **Automated Mode**:
   `python code_combiner.py --auto --directory <DIR> --output <OUTPUT_FILE> [--include-tree] [--max-depth N]`
   - Runs automatically with default (None) for file extensions (i.e., all files).
   - If `--include-tree` is present, a directory tree will be included in the output.
   - Use `--max-depth` to limit recursion of the directory tree listing.
"""

import os
import argparse
import sys


def write_directory_tree(search_dir, max_depth=None):
    """
    Walk the directory up to 'max_depth' levels (None = no limit) and return
    a string representation of the directory tree.

    :param search_dir: The root directory to list.
    :param max_depth: Maximum subdirectory depth to recurse (None means unlimited).
    :return: Multi-line string with the directory tree.
    """
    lines = []
    lines.append("=" * 60)
    lines.append(f"DIRECTORY TREE: {search_dir}")
    lines.append("=" * 60)

    # Normalizing just to be safe, removing trailing slash
    root_dir = os.path.abspath(search_dir)

    for root, dirs, files in os.walk(root_dir):
        # Compute the depth by counting separators relative to the root_dir
        depth = root.replace(root_dir, "").count(os.sep)

        # If max_depth is set, skip deeper levels
        if max_depth is not None and depth > max_depth:
            # Stop walking deeper by clearing dirs
            dirs[:] = []
            continue

        indent = "    " * depth
        dir_name = os.path.basename(root)
        if not dir_name:  # If we're at the root, use the root's name or path
            dir_name = root

        lines.append(f"{indent}{dir_name}/")
        for f in files:
            lines.append(f"{indent}    {f}")

    # Add spacing after the tree
    lines.append("")
    return "\n".join(lines)


def combine_code_files(
        search_dir,
        output_file,
        extensions=None,
        skip_extensions=None,
        chunk_size=None,
        include_tree=False,
        max_depth=None
):
    """
    Recursively searches through a directory and combines code files into one or more output files.
    
    :param search_dir: The directory to search.
    :param output_file: The base name of the output file(s).
    :param extensions: List of file extensions to include (None means all).
    :param skip_extensions: List of file or directory suffixes to skip.
    :param chunk_size: Maximum bytes per chunk file (None means write to one file).
    :param include_tree: If True, write a directory tree listing at the top of the file(s).
    :param max_depth: Limit the directory-tree listing to this depth (None = no limit).
    """
    file_count = 0
    chunk_index = 1
    bytes_written = 0

    # Prepare output file handle if chunking is disabled
    main_outfile = None
    if chunk_size is None:
        try:
            main_outfile = open(output_file, 'w', encoding='utf-8')
        except Exception as e:
            print(f"[ERROR] Cannot open output file: {output_file} - {e}")
            return

        # If requested, write the directory tree at top
        if include_tree:
            tree_string = write_directory_tree(search_dir, max_depth=max_depth)
            main_outfile.write(tree_string + "\n\n")

    else:
        # If chunking is enabled but we still want the tree, we'll handle that
        # in the same chunk-based approach below.
        if include_tree:
            tree_string = write_directory_tree(search_dir, max_depth=max_depth)
            # Write in chunk mode
            lines = tree_string.splitlines(keepends=True)
            for line in lines:
                line_bytes = len(line.encode('utf-8'))
                if bytes_written + line_bytes > chunk_size:
                    # Move to next chunk
                    chunk_index += 1
                    bytes_written = 0
                # Compute the current chunk filename
                chunk_file_name = output_file.replace(".txt", f"_chunk_{chunk_index}.txt")
                with open(chunk_file_name, 'a', encoding='utf-8') as chunk_file:
                    chunk_file.write(line)
                bytes_written += line_bytes

            # Add some spacing after tree
            extra_newline = "\n\n"
            line_bytes = len(extra_newline.encode('utf-8'))
            if bytes_written + line_bytes > chunk_size:
                chunk_index += 1
                bytes_written = 0
            chunk_file_name = output_file.replace(".txt", f"_chunk_{chunk_index}.txt")
            with open(chunk_file_name, 'a', encoding='utf-8') as chunk_file:
                chunk_file.write(extra_newline)
            bytes_written += line_bytes

    # Now do the normal walk for code files
    for root, dirs, files in os.walk(search_dir):
        # If skip_extensions is used to skip certain directories, apply logic here
        if skip_extensions:
            dirs[:] = [
                d for d in dirs
                if not any(os.path.join(root, d).endswith(ext) for ext in skip_extensions)
            ]

        for file in files:
            # Skip file if it has one of the skip extensions
            if skip_extensions and any(file.endswith(ext) for ext in skip_extensions):
                continue

            # If user specified extensions, only process matches
            if (extensions is None) or any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except Exception as e:
                    print(f"[ERROR] Reading file: {file_path} - {e}")
                    continue

                # Build a header that identifies this file in the combined output
                header = (
                    f"\n\n{'='*60}\n"
                    f"FILE: {file_path}\n"
                    f"{'='*60}\n\n"
                )

                if chunk_size is None:
                    # Write directly to the main_outfile
                    main_outfile.write(header)
                    main_outfile.write(content)
                else:
                    # Write in chunked mode
                    for block in (header, content):
                        lines = block.splitlines(keepends=True)
                        for line in lines:
                            line_bytes = len(line.encode('utf-8'))
                            # If adding this line exceeds chunk_size, open a new chunk
                            if bytes_written + line_bytes > chunk_size:
                                # Move to next chunk
                                chunk_index += 1
                                bytes_written = 0

                            # Compute the current chunk filename
                            chunk_file_name = output_file.replace(".txt", f"_chunk_{chunk_index}.txt")
                            # Write line to chunk
                            with open(chunk_file_name, 'a', encoding='utf-8') as chunk_file:
                                chunk_file.write(line)
                            bytes_written += line_bytes

                file_count += 1

                # Simple progress indicator
                if file_count > 0 and file_count % 10 == 0:
                    print(f"  Processed {file_count} files...")

    # Close the single outfile if not chunking
    if main_outfile and chunk_size is None:
        main_outfile.close()

    # Summary
    print(f"\n[INFO] Found and processed {file_count} code files.")
    if chunk_size is None:
        print(f"[SUCCESS] Combined code written to: {output_file}")
    else:
        print(f"[SUCCESS] Combined code written to chunked files with base name: "
              f"{output_file.replace('.txt', '_chunk_')}")


def get_user_input():
    """
    Interactively gets user input: directory, output file name, extension filtering, skip list,
    and chunk size if applicable. Also asks if the user wants the directory tree listing
    and a max depth for that tree. Returns all parameters or (None, ...) if canceled.
    """
    print("=" * 40)
    print("  Code Combiner Script (Interactive)")
    print("=" * 40)

    # 1) Directory selection
    while True:
        target_directory = input("Enter the directory to search for code files: ").strip()
        if os.path.isdir(target_directory):
            break
        else:
            print("[ERROR] Invalid directory path. Please enter a valid directory path.")

    # 2) Output filename
    output_filename = input("Enter the name for the output text file (e.g., combined_code.txt): ").strip()
    if not output_filename.endswith(".txt"):
        output_filename += ".txt"

    # 3) Extension preset or custom
    print("\nAvailable file extension presets:")
    print("  1. Python (.py)")
    print("  2. JavaScript (.js)")
    print("  3. Java (.java)")
    print("  4. Common web files (.html, .css, .js)")
    print("  5. All files (no filtering)")
    print("  6. Enter custom comma-separated extensions")

    while True:
        choice = input("Select an extension preset (1-6): ").strip()
        if choice == '1':
            extensions_list = ['.py']
            break
        elif choice == '2':
            extensions_list = ['.js']
            break
        elif choice == '3':
            extensions_list = ['.java']
            break
        elif choice == '4':
            extensions_list = ['.html', '.css', '.js']
            break
        elif choice == '5':
            extensions_list = None
            break
        elif choice == '6':
            custom_extensions = input("Enter comma-separated file extensions (e.g., .cpp,.h): ").strip()
            extensions_list = [ext.strip() for ext in custom_extensions.split(',')]
            break
        else:
            print("[ERROR] Invalid choice. Please enter a number between 1 and 6.")

    # 4) Skip extensions
    skip_extensions_input = input("Enter comma-separated file extensions to skip (e.g., .log,.tmp) or press Enter to skip none: ").strip()
    if skip_extensions_input:
        skip_extensions_list = [ext.strip() for ext in skip_extensions_input.split(',')]
    else:
        skip_extensions_list = None

    # 5) Chunking
    while True:
        chunk_choice = input("\nDo you want to chunk the output file? (yes/no): ").lower().strip()
        if chunk_choice == 'yes':
            while True:
                chunk_size_input = input("Enter the maximum chunk size in bytes: ").strip()
                if chunk_size_input.isdigit() and int(chunk_size_input) > 0:
                    chunk_size_int = int(chunk_size_input)
                    break
                else:
                    print("[ERROR] Invalid chunk size. Please enter a positive integer.")
            break
        elif chunk_choice == 'no':
            chunk_size_int = None
            break
        else:
            print("[ERROR] Invalid choice. Please enter 'yes' or 'no'.")

    # 6) Directory Tree listing
    include_tree_choice = input("\nInclude a directory tree listing? (yes/no): ").lower().strip()
    include_tree = (include_tree_choice == 'yes')

    # 7) If tree listing, optionally ask for max depth
    max_depth_int = None
    if include_tree:
        depth_input = input("Enter max depth for directory tree (0=top-level only, Enter for unlimited): ").strip()
        if depth_input.isdigit():
            max_depth_int = int(depth_input) if int(depth_input) >= 0 else None
        else:
            max_depth_int = None

    # Confirm settings
    print("\n--- Summary ---")
    print(f"Search directory: {target_directory}")
    print(f"Output filename: {output_filename}")
    print(f"File extensions: {extensions_list if extensions_list else 'All files'}")
    print(f"Skip extensions: {skip_extensions_list if skip_extensions_list else 'None'}")
    print(f"Chunking: {'Yes' if chunk_size_int else 'No'}")
    if chunk_size_int:
        print(f"Chunk size: {chunk_size_int} bytes")
    print(f"Include tree listing: {'Yes' if include_tree else 'No'}")
    if include_tree:
        print(f"Max depth for tree: {max_depth_int if max_depth_int is not None else 'Unlimited'}")
    print("-" * 40)

    confirmation = input("Proceed with these settings? (yes/no): ").lower().strip()
    if confirmation == 'yes':
        return (target_directory,
                output_filename,
                extensions_list,
                skip_extensions_list,
                chunk_size_int,
                include_tree,
                max_depth_int)
    else:
        print("[INFO] Operation cancelled by user.")
        return None, None, None, None, None, None, None


def open_file(filename):
    """
    Attempts to open the given file in the default viewer for the OS.
    """
    if os.name == 'nt':        # Windows
        os.system(f'start \"\" \"{filename}\"')
    elif sys.platform.startswith('darwin'):  # macOS
        os.system(f'open \"{filename}\"')
    elif sys.platform.startswith('linux'):   # Linux
        os.system(f'xdg-open \"{filename}\"')
    else:
        print(f"[WARN] Could not open file automatically on this OS: {filename}")


def auto_combine_code(directory, output_filename=None, include_tree=False, max_depth=None):
    """
    For automated runs: combine all files in a directory (no extension filtering),
    unless output_filename is specified. If include_tree=True, prepend a directory
    tree up to max_depth (if set).
    """
    if not output_filename:
        output_filename = "combined_code.txt"

    print("\n[INFO] Starting auto code combination...")
    combine_code_files(
        search_dir=directory,
        output_file=output_filename,
        extensions=None,
        skip_extensions=None,
        chunk_size=None,
        include_tree=include_tree,
        max_depth=max_depth
    )
    print("[INFO] Auto code combination process finished.")

    # Attempt to open the resulting file
    open_file(output_filename)


def main():
    parser = argparse.ArgumentParser(
        description="Combine code files. Use --auto for automated mode, or run without --auto for interactive mode."
    )
    parser.add_argument("--auto", action="store_true",
                        help="Run in automated mode using the --directory and --output arguments.")
    parser.add_argument("--directory", type=str,
                        help="The directory to search for code files in automated mode.")
    parser.add_argument("--output", type=str,
                        help="The name of the output file in automated mode.")
    parser.add_argument("--include-tree", action="store_true",
                        help="Include a directory tree listing at the top of the output.")
    parser.add_argument("--max-depth", type=int, default=None,
                        help="Maximum depth for directory tree listing (use with --include-tree).")

    args = parser.parse_args()

    if args.auto:
        if args.directory:
            auto_combine_code(
                directory=args.directory,
                output_filename=args.output,
                include_tree=args.include_tree,
                max_depth=args.max_depth
            )
        else:
            print("[ERROR] Directory must be specified in auto mode.")
    else:
        # Run in interactive mode
        (target_directory,
         output_filename,
         extensions_list,
         skip_extensions_list,
         chunk_size_int,
         include_tree,
         max_depth_int) = get_user_input()

        # If user canceled, do nothing
        if target_directory is None:
            return

        print("\n[INFO] Starting code combination...")
        combine_code_files(
            search_dir=target_directory,
            output_file=output_filename,
            extensions=extensions_list,
            skip_extensions=skip_extensions_list,
            chunk_size=chunk_size_int,
            include_tree=include_tree,
            max_depth=max_depth_int
        )
        print("[INFO] Code combination process finished.")
        # Optionally open the final file if chunk_size is None
        if chunk_size_int is None:
            open_file(output_filename)


if __name__ == "__main__":
    main()
