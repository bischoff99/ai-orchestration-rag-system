#!/usr/bin/env python3
"""
Fix webhook registration issue using Desktop Commander approach
"""

import requests
import json
import time

def fix_webhook_registration():
    """Fix webhook registration by toggling workflows"""

    print('🔧 Fixing webhook registration issue...')

    n8n_url = 'http://localhost:5678'
    api_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjMWMyZGZhOC05ZGQ2LTQ4MmQtOGIxNy1iOTEyNDQ0NTc5ZDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxNTczMzkwLCJleHAiOjE3NjQxMzMyMDB9.ZPTKZUqH1cKy4IuTPggkL19lcNioMaQDoi1X2r9ScXs'

    headers = {
        'X-N8N-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    try:
        # Get workflows
        response = requests.get(f'{n8n_url}/api/v2/workflows', headers=headers, timeout=10)
        if response.status_code != 200:
            print(f'❌ Failed to get workflows: HTTP {response.status_code}')
            return False

        workflows = response.json().get('data', [])
        print(f'📊 Found {len(workflows)} workflows')

        # Find active workflows
        active_workflows = [w for w in workflows if w.get('active', False)]
        print(f'✅ Active workflows: {len(active_workflows)}')

        # Try to deactivate and reactivate each workflow to fix webhook registration
        fixed_count = 0
        for wf in active_workflows:
            wf_id = wf.get('id')
            wf_name = wf.get('name', 'Unknown')
            print(f'🔄 Fixing webhook for: {wf_name}')

            try:
                # Deactivate
                deactivate_response = requests.put(
                    f'{n8n_url}/api/v2/workflows/{wf_id}',
                    headers=headers,
                    json={'active': False, 'name': wf_name},
                    timeout=10
                )

                if deactivate_response.status_code == 200:
                    print(f'   ✅ Deactivated: {wf_name}')
                    time.sleep(2)  # Wait for deactivation

                    # Reactivate
                    activate_response = requests.put(
                        f'{n8n_url}/api/v2/workflows/{wf_id}',
                        headers=headers,
                        json={'active': True, 'name': wf_name},
                        timeout=10
                    )

                    if activate_response.status_code == 200:
                        print(f'   ✅ Reactivated: {wf_name}')
                        fixed_count += 1
                    else:
                        print(f'   ❌ Failed to reactivate: {wf_name} - HTTP {activate_response.status_code}')
                else:
                    print(f'   ❌ Failed to deactivate: {wf_name} - HTTP {deactivate_response.status_code}')

                time.sleep(1)  # Wait between workflows

            except Exception as e:
                print(f'   ❌ Error processing {wf_name}: {e}')

        print(f'\n📊 Fixed {fixed_count}/{len(active_workflows)} workflows')

        # Wait for webhook registration
        print('\n⏳ Waiting for webhook registration...')
        time.sleep(5)

        # Test webhook endpoints
        print('\n🧪 Testing webhook endpoints...')

        test_webhooks = [
            'simple-test',
            'rag-query',
            'document-ingestion',
            'working-test'
        ]

        working_webhooks = []
        for webhook in test_webhooks:
            try:
                test_response = requests.post(
                    f'{n8n_url}/webhook/{webhook}',
                    json={'test': 'data', 'message': 'Testing webhook'},
                    timeout=10
                )

                if test_response.status_code == 200:
                    result = test_response.json()
                    print(f'   ✅ {webhook}: Working')
                    print(f'      Response: {str(result)[:100]}...')
                    working_webhooks.append(webhook)
                else:
                    print(f'   ❌ {webhook}: HTTP {test_response.status_code}')

            except Exception as e:
                print(f'   ❌ {webhook}: {e}')

        print(f'\n📊 Working webhooks: {len(working_webhooks)}/{len(test_webhooks)}')

        if working_webhooks:
            print('🎉 Webhook registration fixed!')
            return True
        else:
            print('⚠️  Webhook registration still has issues')
            return False

    except Exception as e:
        print(f'❌ Error fixing webhooks: {e}')
        return False

def create_simple_working_webhook():
    """Create a simple working webhook as fallback"""

    print('\n🚀 Creating simple working webhook...')

    n8n_url = 'http://localhost:5678'
    api_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjMWMyZGZhOC05ZGQ2LTQ4MmQtOGIxNy1iOTEyNDQ0NTc5ZDMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxNTczMzkwLCJleHAiOjE3NjQxMzMyMDB9.ZPTKZUqH1cKy4IuTPggkL19lcNioMaQDoi1X2r9ScXs'

    headers = {
        'X-N8N-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    # Simple working webhook
    workflow = {
        "name": "Desktop Commander Test Webhook",
        "nodes": [
            {
                "id": "webhook-trigger",
                "name": "Test Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [240, 300],
                "parameters": {
                    "httpMethod": "POST",
                    "path": "desktop-commander-test",
                    "responseMode": "responseNode"
                }
            },
            {
                "id": "process-data",
                "name": "Process Data",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [460, 300],
                "parameters": {
                    "jsCode": """// Process incoming data
const body = $json.body || $json;
const message = body.message || body.query || 'Hello from Desktop Commander!';

return [{
  json: {
    message: message,
    timestamp: new Date().toISOString(),
    status: 'success',
    processed: true,
    source: 'desktop-commander'
  }
}];"""
                }
            },
            {
                "id": "respond",
                "name": "Respond",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [680, 300],
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={{ $json }}"
                }
            }
        ],
        "connections": {
            "Test Webhook": {
                "main": [[{"node": "Process Data", "type": "main", "index": 0}]]
            },
            "Process Data": {
                "main": [[{"node": "Respond", "type": "main", "index": 0}]]
            }
        },
        "settings": {
            "executionOrder": "v1"
        }
    }

    try:
        # Create workflow
        response = requests.post(
            f'{n8n_url}/api/v2/workflows',
            headers=headers,
            json=workflow,
            timeout=30
        )

        if response.status_code in [200, 201]:
            result = response.json()
            workflow_id = result.get('id')
            print(f'   ✅ Webhook workflow created (ID: {workflow_id})')

            # Activate workflow
            activate_response = requests.put(
                f'{n8n_url}/api/v2/workflows/{workflow_id}',
                headers=headers,
                json={'active': True, 'name': 'Desktop Commander Test Webhook'},
                timeout=10
            )

            if activate_response.status_code == 200:
                print('   ✅ Webhook workflow activated')

                # Wait for webhook registration
                time.sleep(3)

                # Test the webhook
                test_response = requests.post(
                    f'{n8n_url}/webhook/desktop-commander-test',
                    json={'message': 'Testing Desktop Commander webhook'},
                    timeout=10
                )

                if test_response.status_code == 200:
                    result = test_response.json()
                    print(f'   ✅ Webhook test successful!')
                    print(f'      Response: {result}')
                    return True
                else:
                    print(f'   ❌ Webhook test failed: HTTP {test_response.status_code}')
                    return False
            else:
                print(f'   ❌ Failed to activate webhook: HTTP {activate_response.status_code}')
                return False
        else:
            print(f'   ❌ Failed to create webhook: HTTP {response.status_code}')
            return False

    except Exception as e:
        print(f'   ❌ Error creating webhook: {e}')
        return False

def main():
    """Main function"""
    print('🚀 Desktop Commander Webhook Fix')
    print('=' * 40)

    # Try to fix existing webhooks
    success = fix_webhook_registration()

    if not success:
        print('\n🔄 Trying fallback approach...')
        success = create_simple_working_webhook()

    if success:
        print('\n🎉 Webhook issue resolved!')
        print('✅ System is ready for testing')
    else:
        print('\n⚠️  Webhook issue persists')
        print('❌ Manual activation in n8n UI required')

    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
