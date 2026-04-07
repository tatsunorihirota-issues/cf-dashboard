#!/usr/bin/env python3
"""GitHub APIでリポジトリを作成してプッシュ"""
import subprocess
import json
import urllib.request

# GitHub tokenを取得（git credentialから）
result = subprocess.run(
    ['git', 'credential', 'fill'],
    input='protocol=https\nhost=github.com\n',
    capture_output=True, text=True
)
token = None
for line in result.stdout.split('\n'):
    if line.startswith('password='):
        token = line.split('=', 1)[1]
        break

if not token:
    # SSH keyがある場合はSSHで直接push
    print("No token found, trying SSH push...")
    subprocess.run(['git', 'remote', 'add', 'origin',
                    'git@github.com:tatsunorihirota-issues/cf-dashboard.git'],
                   capture_output=True)

    # Create repo via GitHub API using ghapi
    from ghapi.all import GhApi
    import os
    # Try to get token from environment
    gh_token = os.environ.get('GITHUB_TOKEN', '')
    if gh_token:
        api = GhApi(token=gh_token)
        api.repos.create_in_org('tatsunorihirota-issues', name='cf-dashboard', private=True)
    else:
        print("Please create the repo manually: https://github.com/new")
        print("Repo name: cf-dashboard, Private, org: tatsunorihirota-issues")
else:
    # Create repo via API
    req = urllib.request.Request(
        'https://api.github.com/orgs/tatsunorihirota-issues/repos',
        data=json.dumps({'name': 'cf-dashboard', 'private': True}).encode(),
        headers={
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        },
        method='POST'
    )
    try:
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read())
        print(f"Created: {data['html_url']}")
    except Exception as e:
        print(f"Repo may already exist: {e}")

    subprocess.run(['git', 'remote', 'add', 'origin',
                    f'https://x-access-token:{token}@github.com/tatsunorihirota-issues/cf-dashboard.git'],
                   capture_output=True)

# Push
result = subprocess.run(['git', 'push', '-u', 'origin', 'main'], capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0:
    print(result.stderr)
    # Try with SSH
    subprocess.run(['git', 'remote', 'set-url', 'origin',
                    'git@github.com:tatsunorihirota-issues/cf-dashboard.git'],
                   capture_output=True)
    result2 = subprocess.run(['git', 'push', '-u', 'origin', 'main'], capture_output=True, text=True)
    print(result2.stdout, result2.stderr)
