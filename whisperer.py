#!/usr/bin/env python3

import argparse
import os
import re
import sys
import urllib.error
import urllib.request

# Author: LiranV
# Description: Grab DigitalWhisper issues easily
# Inspired by DigitalDown https://github.com/shrek0/DigitalDown

__VERSION__ = 0.1


class Whisperer(object):

    FIRST_ISSUE_ID = 1

    def __init__(self, options):
        self._options = options
        self._download_queue = set()
        self._last_issue_id_cache = None
        self._overwrite_without_confirmation = options.overwrite
        self._skip_existing_issues = options.skip
        self.set_download_path(options.directory)

    def _generate_issue_url(self, issue_id):
        """Return the URL of the issue pdf"""
        return "http://www.digitalwhisper.co.il/files/Zines/0x%02X/DigitalWhisper%d.pdf" % \
            (issue_id, issue_id)

    def _get_last_issue_id(self):
        """Get the last issue ID"""
        if self._last_issue_id_cache is not None:
            return self._last_issue_id_cache
        print("Fetching latest issue ID...")
        data = str(self._fetch_url_content("https://digitalwhisper.co.il/issues")[0])
        match = re.search("www.digitalwhisper.co.il/issue([0-9]+)", data)
        if match:
            self._last_issue_id_cache = int(match.group(1))
        else:
            print("Error: Can't find last issue ID", file=sys.stderr)
        return self._last_issue_id_cache

    def _fetch_url_content(self, url):
        """Fetch content from given URL and return data and Content-Length header"""
        try:
            with urllib.request.urlopen(url) as response:
                return response.read(), response.getheader("Content-Length")
        except urllib.error.HTTPError as e:
            print("HTTP Error: " + str(e.code) + " " + e.reason, file=sys.stderr)
            raise e
        except urllib.error.URLError as e:
            print("URL Error: " + e.reason, file=sys.stderr)
            raise e
        except Exception as e:
            print("Error: " + str(sys.exc_info()[0]), file=sys.stderr)
            raise e

    def _bytes_to_megabytes(self, size):
        """Convert Bytes to Megabytes"""
        return round(size/1000000, 2)

    def _download_issue(self, issue_id):
        """Download a single issue and save it to a disk"""
        issue_url = self._generate_issue_url(issue_id)
        filename = issue_url[issue_url.rfind('/')+1:]
        out_path = os.path.realpath(self._download_path + "/" + filename)
        # Check if file already exists
        if (not self._overwrite_without_confirmation) and os.path.isfile(out_path):
            if self._skip_existing_issues:
                print("Skipping issue #" + str(issue_id))
                return
            print("File \"" + filename + "\" already exists!")
            overwrite = input("Would you like to overwrite this file? [Y/n] ").lower()
            if overwrite != 'y':
                print("Skipping issue #" + str(issue_id))
                return
        print("Downloading issue #" + str(issue_id) + " < " + filename + " >")
        data = self._fetch_url_content(issue_url)
        with open(out_path, 'wb') as out_file:
            size_in_mb = self._bytes_to_megabytes(int(data[1]))
            filesize = str(size_in_mb) + " MB"
            out_file.write(data[0])
            print("Download successful! (" + filesize + ")")

    def download(self):
        """Download all the issues in the download queue"""
        total = len(self._download_queue)
        counter = 0
        for issue_id in sorted(self._download_queue):
            counter += 1
            print("\nProgress [" + str(counter) + "/" + str(total) + "]")
            try:
                self._download_issue(issue_id)
            except urllib.error.URLError as e:
                print("Error while trying to fetch issue #" + str(issue_id))
                fail_continue = input("Would you like to continue? [Y/n] ").lower()
                if fail_continue != 'y':
                    break

    def add_issue_id(self, issue_id):
        """Add single issue id to the download queue"""
        self._download_queue.add(issue_id)

    def add_issue_id_range(self, issue_id_range):
        """Add a range of issue id's to the download queue"""
        self._download_queue.update(issue_id_range)

    def clear_download_queue(self):
        """Reset download queue"""
        self._download_queue = set()

    def set_download_path(self, path_dir):
        """Set the download path directory"""
        path_dir = os.path.abspath(path_dir)
        if not os.path.isdir(path_dir):
            raise ValueError("Directory " + path_dir + " does not exist!")
        self._download_path = path_dir


def main(options):
    try:
        whisperer = Whisperer(options)
    except ValueError as e:
        print("Error:", e, file=sys.stderr)
        exit(1)

    ranges = options.range.split(',')
    # Add issue ID's
    for issue_range in ranges:
        # Substitute keywords 'last' and 'all'
        if 'all' in issue_range:
            if 'all' == issue_range:
                last_issue_id = whisperer._get_last_issue_id()
                issue_range = str(whisperer.FIRST_ISSUE_ID) + "-" + str(last_issue_id)
            else:
                print("Error: 'all' cannot be used as part of a range", file=sys.stderr)
                exit(1)
        elif 'last' in issue_range:
            last_issue_id = whisperer._get_last_issue_id()
            issue_range = issue_range.replace("last", str(last_issue_id))

        # Expand issue range
        if '-' in issue_range:
            start, finish = issue_range.split('-')
            whisperer.add_issue_id_range(range(int(start), int(finish)+1))
        # Single issue
        else:
            whisperer.add_issue_id(int(issue_range))

    whisperer.download()
    print("All Done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Whisperer - Grab DigitalWhisper Issues Easily")
    parser.add_argument("-d", "--directory", help="Output directory for downloaded issues " +
                        "[Default: current working directory]", type=str, default="./")
    parser.add_argument("-o", "--overwrite", help="Overwrite existing files " +
                        "without confirmation", action="store_true")
    parser.add_argument("-s", "--skip", help="Skip issues that already exist ",
                        action="store_true")
    parser.add_argument("-r", "--range", help="Comma separated list of the following: Issue ID, " +
                        "Range of ID's (Example: 13-last), 'last' (Latest issue), 'all' " +
                        "(From 1 to 'last) [Default: 'last']", type=str,
                        metavar="RANGE_LIST", default="last")
    options = parser.parse_args()

    main(options)
