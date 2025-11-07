#!/usr/bin/env python3
"""
Client Onboarding Tool

Creates a new client from a requirements document, generates test script,
and helps debug until stable.

Usage:
    python onboard_client.py clients/requirements/new_client_requirements.md
"""

import asyncio
import json
import os
import sys
from pathlib import Path
import yaml

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load .env
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

from playwright_client import PlaywrightClient
from together_ai.togetherai import TogetherAIClient


def load_requirements(requirements_file: Path) -> dict:
    """Load client requirements from markdown file."""

    with open(requirements_file, 'r') as f:
        content = f.read()

    # Parse the requirements file
    # Expected format:
    # # Client: <name>
    # ## Website: <url>
    # ## Workflow:
    # 1. Step 1
    # 2. Step 2
    # ## Selectors (if known):
    # - search_box: #search

    requirements = {
        'client_name': '',
        'website_url': '',
        'workflow_steps': [],
        'known_selectors': {},
        'notes': ''
    }

    lines = content.split('\n')
    current_section = None

    for line in lines:
        line = line.strip()

        if line.startswith('# Client:'):
            requirements['client_name'] = line.replace('# Client:', '').strip()
        elif line.startswith('## Website:'):
            requirements['website_url'] = line.replace('## Website:', '').strip()
        elif line.startswith('## Workflow:'):
            current_section = 'workflow'
        elif line.startswith('## Selectors'):
            current_section = 'selectors'
        elif line.startswith('## Notes'):
            current_section = 'notes'
        elif current_section == 'workflow' and line and line[0].isdigit():
            # Workflow step
            step = line.split('.', 1)[1].strip() if '.' in line else line
            requirements['workflow_steps'].append(step)
        elif current_section == 'selectors' and line.startswith('-'):
            # Selector
            if ':' in line:
                key_val = line[1:].strip().split(':', 1)
                if len(key_val) == 2:
                    requirements['known_selectors'][key_val[0].strip()] = key_val[1].strip()
        elif current_section == 'notes':
            requirements['notes'] += line + '\n'

    return requirements


def generate_test_script(requirements: dict, output_file: Path):
    """Generate initial test script from requirements."""

    client_id = requirements['client_name'].lower().replace(' ', '_').replace('.', '_')

    script = f'''#!/usr/bin/env python3
"""
Test script for {requirements['client_name']}

Auto-generated from requirements. Edit as needed during debugging.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path (go up 2 levels: clients/<client_id>/ -> root/)
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env
env_file = Path(__file__).parent.parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

from playwright_client import PlaywrightClient
from together_ai.togetherai import TogetherAIClient


async def main():
    print("=" * 70)
    print("Testing: {requirements['client_name']}")
    print("=" * 70)

    api_key = os.getenv('TOGETHER_API_KEY')
    if not api_key:
        print("❌ TOGETHER_API_KEY not set in .env")
        return 1

    llm = TogetherAIClient(api_key=api_key)

    async with PlaywrightClient(headless=True) as browser:
        screenshot_dir = Path("./test_screenshots/{client_id}")
        screenshot_dir.mkdir(parents=True, exist_ok=True)

'''

    # Add workflow steps
    for i, step in enumerate(requirements['workflow_steps'], 1):
        script += f'''
        # Step {i}: {step}
        print("\\n📍 Step {i}: {step}")

        # TODO: Implement this step
        # See reference implementations:
        # - test_amazon_real.py: basic navigation, clicking, form filling
        # - clients/[sandbar]/test_[sandbar].py: auth caching, keyboard shortcuts, LLM decisions
        #
        # Common patterns (see CLAUDE.md for details):
        # - Navigate: await browser.navigate("https://url.com")
        # - Dynamic selectors: await browser.evaluate("(...JS to find element...)")
        # - Fill forms: await browser.page.fill('input[name="field"]', 'value')
        # - Click: element.click() inside browser.evaluate()
        # - Keyboard: await browser.page.keyboard.press('Enter')
        # - Wait: await asyncio.sleep(seconds)

        await browser.screenshot("step_{i:02d}", path=screenshot_dir / "step_{i:02d}.png", save_metadata=True)
        await asyncio.sleep(1)
'''

    script += '''

        print("\\n" + "=" * 70)
        print("✅ Workflow complete")
        print("=" * 70)
        print(f"\\nScreenshots saved to: {screenshot_dir}")

        return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
'''

    with open(output_file, 'w') as f:
        f.write(script)

    os.chmod(output_file, 0o755)
    print(f"✅ Generated test script: {output_file}")


def generate_client_config(requirements: dict, output_file: Path):
    """Generate YAML client configuration."""

    client_id = requirements['client_name'].lower().replace(' ', '_').replace('.', '_')

    config = {
        'client_id': client_id,
        'client_name': requirements['client_name'],
        'environment': 'staging',  # Start with staging
        'enabled': False,  # Not enabled until tested
        'website': {
            'base_url': requirements['website_url'],
            'rate_limit': {
                'requests_per_minute': 10,
                'burst_capacity': 5
            },
            'selectors': requirements['known_selectors']
        },
        'workflows': [
            {
                'name': 'main_workflow',
                'enabled': False,
                'description': 'Auto-generated from requirements',
                'timeout_seconds': 300,
                'steps': [
                    {
                        'action': 'navigate',
                        'url': requirements['website_url'],
                        'screenshot': 'homepage'
                    }
                    # More steps added during debugging
                ]
            }
        ],
        'notes': requirements['notes']
    }

    with open(output_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    print(f"✅ Generated config: {output_file}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python onboard_client.py <requirements_file.md>")
        print("\\nExample:")
        print("  python onboard_client.py clients/requirements/chase_bank.md")
        return 1

    requirements_file = Path(sys.argv[1])

    if not requirements_file.exists():
        print(f"❌ Requirements file not found: {requirements_file}")
        return 1

    print("=" * 70)
    print("Client Onboarding Tool")
    print("=" * 70)
    print(f"\\nLoading requirements from: {requirements_file}")

    # Load requirements
    requirements = load_requirements(requirements_file)

    print(f"\\n✅ Client: {requirements['client_name']}")
    print(f"✅ Website: {requirements['website_url']}")
    print(f"✅ Workflow steps: {len(requirements['workflow_steps'])}")
    print(f"✅ Known selectors: {len(requirements['known_selectors'])}")

    # Generate files
    client_id = requirements['client_name'].lower().replace(' ', '_').replace('.', '_')

    # Create client directory structure
    client_dir = Path("clients") / client_id
    client_dir.mkdir(parents=True, exist_ok=True)

    test_script = client_dir / f"test_{client_id}.py"
    config_file = client_dir / f"{client_id}.yml"

    generate_test_script(requirements, test_script)
    generate_client_config(requirements, config_file)

    print(f"\\n" + "=" * 70)
    print("Next Steps:")
    print("=" * 70)
    print(f"\\n1. Review generated files:")
    print(f"   - Test script: {test_script}")
    print(f"   - Config: {config_file}")
    print(f"\\n2. Run the test script:")
    print(f"   python {test_script}")
    print(f"\\n3. Debug and iterate:")
    print(f"   - Update test script with working selectors")
    print(f"   - Add error handling")
    print(f"   - Update config file")
    print(f"\\n4. When stable, enable in config:")
    print(f"   - Set 'enabled: true'")
    print(f"   - Set 'environment: production'")

    return 0


if __name__ == "__main__":
    sys.exit(main())
