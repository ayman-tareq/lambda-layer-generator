import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Dict, Any
from pathlib import Path

# Handle both relative and absolute imports
try:
    from .logger import get_logger
except ImportError:
    from logger import get_logger

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class AWSLayerClient:
    def __init__(self):
        logger = get_logger()
        logger.info("Initializing AWS client", step=True)
        
        self._load_env_file()
        self.region = self._get_aws_region()
        self.client = self._create_lambda_client()
        
        logger.success(f"AWS client initialized for region: {self.region}")
    
    def _load_env_file(self):
        """Load environment variables from .env file in project root."""
        logger = get_logger()
        
        try:
            # Get project root directory (parent of src directory)
            current_dir = Path(__file__).parent
            project_root = current_dir.parent
            env_file = project_root / '.env'
            
            if env_file.exists():
                logger.info("Found .env file, loading configuration")
                
                if DOTENV_AVAILABLE:
                    # Use python-dotenv if available for better parsing
                    load_dotenv(env_file)
                    logger.detail("Environment loader", "python-dotenv")
                else:
                    # Fallback to manual parsing
                    logger.detail("Environment loader", "manual parsing")
                    with open(env_file, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                # Remove quotes if present
                                value = value.strip().strip('"').strip("'")
                                os.environ[key.strip()] = value
                
                logger.success("Environment variables loaded from .env file")
            else:
                logger.info("No .env file found, using system environment variables")
        except Exception as e:
            logger.warning(f"Could not load .env file: {str(e)}")
            # Silently continue if .env file cannot be loaded
            pass
    
    def _get_aws_region(self) -> str:
        """Get AWS region from environment variables."""
        logger = get_logger()
        
        region = os.getenv('AWS_DEFAULT_REGION') or os.getenv('AWS_REGION')
        if not region:
            logger.error("AWS region not found in environment variables")
            raise ValueError("AWS region not found. Set AWS_DEFAULT_REGION or AWS_REGION environment variable")
        
        logger.detail("AWS Region", region)
        return region
    
    def _create_lambda_client(self):
        """Create AWS Lambda client with error handling."""
        logger = get_logger()
        
        try:
            logger.progress("Connecting to AWS Lambda service")
            client = boto3.client('lambda', region_name=self.region)
            logger.success("AWS Lambda client created successfully")
            return client
        except NoCredentialsError:
            logger.error("AWS credentials not found in environment")
            raise ValueError("AWS credentials not found. Configure AWS credentials via environment variables")
    
    def publish_layer(self, layer_name: str, description: str, zip_content: bytes, 
                     python_version: str) -> str:
        """Publish a Lambda layer and return its ARN."""
        logger = get_logger()
        logger.info("Publishing layer to AWS", step=True)
        
        logger.detail("Layer name", layer_name)
        logger.detail("Python runtime", python_version)
        logger.detail("Content size", f"{len(zip_content) / (1024*1024):.2f} MB")
        
        try:
            logger.progress("Uploading layer to AWS Lambda")
            
            response = self.client.publish_layer_version(
                LayerName=layer_name,
                Description=description,
                Content={'ZipFile': zip_content},
                CompatibleRuntimes=[python_version],
                CompatibleArchitectures=['x86_64', 'arm64']
            )
            
            layer_arn = response['LayerVersionArn']
            version = response['Version']
            
            logger.success(f"Layer published successfully!")
            logger.detail("Layer ARN", layer_arn)
            logger.detail("Layer version", str(version))
            
            return layer_arn
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = e.response['Error']['Message']
            
            logger.error(f"AWS API error: {error_code}")
            
            if error_code == 'InvalidParameterValueException':
                raise ValueError(f"Invalid layer parameters: {error_msg}")
            elif error_code == 'TooManyRequestsException':
                raise RuntimeError("Rate limit exceeded. Please try again later")
            elif error_code == 'ResourceConflictException':
                raise RuntimeError(f"Layer conflict: {error_msg}")
            else:
                raise RuntimeError(f"AWS error ({error_code}): {error_msg}")
    
    def get_layer_info(self, layer_arn: str) -> Dict[str, Any]:
        """Get information about a specific layer version."""
        try:
            # Extract layer name and version from ARN
            arn_parts = layer_arn.split(':')
            layer_name = arn_parts[6]
            version = int(arn_parts[7])
            
            response = self.client.get_layer_version(
                LayerName=layer_name,
                VersionNumber=version
            )
            
            return {
                'arn': response['LayerVersionArn'],
                'description': response.get('Description', ''),
                'created_date': response['CreatedDate'],
                'compatible_runtimes': response.get('CompatibleRuntimes', []),
                'compatible_architectures': response.get('CompatibleArchitectures', [])
            }
            
        except ClientError as e:
            raise RuntimeError(f"Failed to get layer info: {e.response['Error']['Message']}") 