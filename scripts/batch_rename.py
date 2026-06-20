"""
Batch File Renamer - Rename thousands of files with patterns
Usage: python batch_rename.py --dir ./photos --pattern "IMG_{n:04d}" --ext jpg
       python batch_rename.py --dir ./docs --find "old" --replace "new"

Features:
- Pattern-based renaming with counters
- Find & replace in filenames
- Add prefix/suffix
- Change case (upper/lower/title)
- Preview mode (dry run)
"""

import os
import argparse
import re

def batch_rename(directory, pattern=None, find=None, replace=None, 
                 prefix=None, suffix=None, case=None, ext_filter=None, dry_run=True):
    files = sorted(os.listdir(directory))
    if ext_filter:
        files = [f for f in files if f.lower().endswith(f'.{ext_filter.lower()}')]
    
    renamed = 0
    for i, filename in enumerate(files):
        filepath = os.path.join(directory, filename)
        if not os.path.isfile(filepath):
            continue
        
        name, ext = os.path.splitext(filename)
        new_name = name
        
        if pattern:
            new_name = pattern.format(n=i+1, name=name, ext=ext[1:])
        if find:
            new_name = new_name.replace(find, replace)
        if prefix:
            new_name = prefix + new_name
        if suffix:
            new_name = new_name + suffix
        if case == 'upper':
            new_name = new_name.upper()
        elif case == 'lower':
            new_name = new_name.lower()
        elif case == 'title':
            new_name = new_name.title()
        
        new_name = new_name + ext
        new_path = os.path.join(directory, new_name)
        
        if new_name != filename:
            if dry_run:
                print(f"  [DRY RUN] {filename} → {new_name}")
            else:
                os.rename(filepath, new_path)
                print(f"  {filename} → {new_name}")
            renamed += 1
    
    mode = "Would rename" if dry_run else "Renamed"
    print(f"\n{mode} {renamed} of {len(files)} files")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Batch File Renamer')
    parser.add_argument('--dir', required=True, help='Target directory')
    parser.add_argument('--pattern', help='Rename pattern: {n:04d}, {name}, {ext}')
    parser.add_argument('--find', help='Find string in filename')
    parser.add_argument('--replace', default='', help='Replace with')
    parser.add_argument('--prefix', help='Add prefix')
    parser.add_argument('--suffix', help='Add suffix')
    parser.add_argument('--case', choices=['upper', 'lower', 'title'])
    parser.add_argument('--ext', help='Filter by extension')
    parser.add_argument('--execute', action='store_true', help='Actually rename (default is dry run)')
    args = parser.parse_args()
    
    batch_rename(args.dir, args.pattern, args.find, args.replace,
                 args.prefix, args.suffix, args.case, args.ext, dry_run=not args.execute)
