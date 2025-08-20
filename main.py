#!/usr/bin/env python3
import sys
import json
import argparse
from src.layer_generator import LayerGenerator
from src.logger import set_verbose


def main():
    parser = argparse.ArgumentParser(
        description='🚀 Generate AWS Lambda layers from Python packages',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "requests"
  %(prog)s "boto3>=1.26.1,requests==2.28.0"
  %(prog)s "pydantic>=2.5.0" --python-version python3.12
  %(prog)s "requests,pydantic" --json --quiet
        """
    )
    parser.add_argument('packages', help='Comma-separated list of packages (e.g., "requests==2.28.0,pydantic")')
    parser.add_argument('--python-version', default='python3.10', 
                       help='Python runtime version (default: python3.10)')
    parser.add_argument('--json', action='store_true', help='Output result as JSON')
    parser.add_argument('--quiet', action='store_true', help='Suppress progress output (JSON mode only)')
    
    args = parser.parse_args()
    
    # Set verbosity based on arguments
    if args.quiet and args.json:
        set_verbose(False)
    
    generator = LayerGenerator()
    result = generator.create_layer(args.packages, args.python_version)
    
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        if result['success']:
            print(f"\n🎯 Final Results:")
            print(f"✅ Layer created successfully!")
            print(f"📦 Layer Name: {result['layer_name']}")
            print(f"🏷️  Layer ARN: {result['layer_arn']}")
            print(f"📝 Description: {result['description']}")
            print(f"🌍 Region: {result['region']}")
            print(f"📊 Packages: {', '.join(result['packages'])}")
        else:
            print(f"❌ Error: {result['error']}")
            sys.exit(1)


if __name__ == '__main__':
    main() 