#!/usr/bin/env python3
"""
Downloader Module

This module provides functionality to download DarwinCore archives and EML files from various sources.
"""

import os
import zipfile
import tempfile
import requests


def download_from_url(url):
    """Download DarwinCore archive from URL"""
    try:
        # Extract the resource ID from the URL
        if 'ipt.vliz.be' in url:
            # For IPT URLs, we need to download the EML file directly
            eml_url = url.replace('/resource?', '/eml.do?')
            print(f"Downloading EML from: {eml_url}")
            response = requests.get(eml_url)
            if response.status_code == 200:
                return response.content
            else:
                raise Exception(f"Failed to download EML from {eml_url}, status code: {response.status_code}")
        else:
            # For other URLs, try to download the archive
            response = requests.get(url)
            if response.status_code == 200:
                return response.content
            else:
                raise Exception(f"Failed to download from {url}, status code: {response.status_code}")
    except Exception as e:
        raise Exception(f"Error downloading from URL: {e}")


def extract_eml_from_archive(archive_content):
    """Extract EML file from DarwinCore archive"""
    try:
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
            tmp_file.write(archive_content)
            tmp_file_path = tmp_file.name
        
        with zipfile.ZipFile(tmp_file_path, 'r') as zip_ref:
            eml_files = [f for f in zip_ref.namelist() if f.endswith('.xml') and 'eml' in f.lower()]
            if not eml_files:
                raise Exception("No EML file found in archive")
            
            eml_content = zip_ref.read(eml_files[0])
        
        # Clean up
        os.unlink(tmp_file_path)
        return eml_content
    
    except Exception as e:
        if 'tmp_file_path' in locals():
            os.unlink(tmp_file_path)
        raise Exception(f"Error extracting EML from archive: {e}")


def get_eml_content(input_source):
    """Get EML content from various input sources"""
    if input_source.startswith('http'):
        print(f"Downloading from URL: {input_source}")
        if 'ipt.vliz.be' in input_source:
            # For IPT URLs, download EML directly
            return download_from_url(input_source)
        else:
            # For other URLs, download archive and extract EML
            archive_content = download_from_url(input_source)
            return extract_eml_from_archive(archive_content)
    else:
        print(f"Reading local file: {input_source}")
        if input_source.endswith('.zip'):
            with open(input_source, 'rb') as f:
                archive_content = f.read()
            return extract_eml_from_archive(archive_content)
        else:
            with open(input_source, 'rb') as f:
                return f.read()
