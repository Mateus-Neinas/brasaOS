"""Create a GitHub release and stream the matching Brasa ISO asset."""
from pathlib import Path
import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

OWNER = 'Mateus-Neinas'
REPO = 'brasaOS'
API = f'https://api.github.com/repos/{OWNER}/{REPO}'

parser = argparse.ArgumentParser()
parser.add_argument('--tag', required=True)
parser.add_argument('--name', required=True)
parser.add_argument('--iso', required=True, type=Path)
parser.add_argument('--notes', required=True, type=Path)
args = parser.parse_args()
iso = args.iso.resolve()
if not iso.is_file():
    raise SystemExit(f'ISO não encontrada: {iso}')
notes = args.notes.read_text(encoding='utf-8')
credential = subprocess.run(['git', 'credential-manager', 'get'], input='protocol=https\nhost=github.com\n\n', text=True, capture_output=True, check=True, timeout=20)
fields = dict(line.split('=', 1) for line in credential.stdout.splitlines() if '=' in line)
token = fields.get('password')
if not token:
    raise SystemExit('Credencial GitHub sem token.')
base_headers = {'Authorization': f'Bearer {token}', 'User-Agent': 'Brasa-release-publisher', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
body = json.dumps({'tag_name': args.tag, 'name': args.name, 'body': notes, 'draft': False, 'prerelease': True, 'make_latest': 'false'}).encode()
request = urllib.request.Request(API + '/releases', data=body, headers={**base_headers, 'Content-Type': 'application/json'}, method='POST')
try:
    with urllib.request.urlopen(request, timeout=60) as response:
        release = json.load(response)
except urllib.error.HTTPError as error:
    detail = error.read(1200).decode('utf-8', 'replace')
    raise SystemExit(f'Criação da release falhou ({error.code}): {detail}')
upload_url = release['upload_url'].split('{', 1)[0] + '?' + urllib.parse.urlencode({'name': iso.name})
asset_request = urllib.request.Request(upload_url, data=iso.open('rb'), headers={**base_headers, 'Accept': 'application/vnd.github+json', 'Content-Type': 'application/octet-stream', 'Content-Length': str(iso.stat().st_size)}, method='POST')
try:
    with urllib.request.urlopen(asset_request, timeout=1800) as response:
        asset = json.load(response)
except urllib.error.HTTPError as error:
    detail = error.read(1200).decode('utf-8', 'replace')
    raise SystemExit(f'Upload do asset falhou ({error.code}); release criada em {release["html_url"]}: {detail}')
print(json.dumps({'tag': release['tag_name'], 'release_url': release['html_url'], 'asset': asset['name'], 'asset_size': asset['size'], 'asset_url': asset['browser_download_url']}, ensure_ascii=False))
