from typing import Dict, Any

# Handle both relative and absolute imports
try:
    from .package_parser import parse_packages, generate_layer_name, generate_layer_description
    from .layer_builder import LayerBuilder
    from .aws_client import AWSLayerClient
    from .logger import get_logger
except ImportError:
    from package_parser import parse_packages, generate_layer_name, generate_layer_description
    from layer_builder import LayerBuilder
    from aws_client import AWSLayerClient
    from logger import get_logger


class LayerGenerator:
    def __init__(self):
        self.aws_client = AWSLayerClient()
    
    def create_layer(self, packages_str: str, python_version: str = "python3.10") -> Dict[str, Any]:
        """Create a Lambda layer from package specifications."""
        logger = get_logger()
        logger.section("Lambda Layer Generation")
        
        try:
            # Parse input packages
            packages = parse_packages(packages_str)
            
            # Generate layer metadata
            logger.info("Generating layer metadata", step=True)
            layer_name = generate_layer_name(packages)
            description = generate_layer_description(packages, python_version)
            
            # Build the layer
            builder = LayerBuilder(python_version)
            zip_content = builder.create_layer_zip(packages)
            
            # Publish to AWS
            layer_arn = self.aws_client.publish_layer(
                layer_name=layer_name,
                description=description,
                zip_content=zip_content,
                python_version=python_version
            )
            
            # Final summary
            logger.section("Generation Complete")
            logger.success("🎉 Lambda layer created successfully!")
            logger.detail("Final layer ARN", layer_arn)
            logger.detail("Total packages", str(len(packages)))
            logger.detail("Layer size", f"{len(zip_content) / (1024*1024):.2f} MB")
            
            return {
                'success': True,
                'layer_arn': layer_arn,
                'layer_name': layer_name,
                'description': description,
                'packages': [str(pkg) for pkg in packages],
                'python_version': python_version,
                'region': self.aws_client.region
            }
            
        except Exception as e:
            logger.error(f"Layer generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            } 