import os
import sys
import graphify.__main__
import graphify.extract
from graph_spec_design.extractors.custom_rust import extract_rust

def main():
    # Default to .specs/graph for TLC Spec-Driven compatibility
    if "GRAPHIFY_OUT" not in os.environ:
        os.environ["GRAPHIFY_OUT"] = ".specs/graph"

    # Inject our custom extractor to override the default one
    graphify.extract._DISPATCH['.rs'] = extract_rust
    
    # Run the original graphify engine
    sys.exit(graphify.__main__.main())

if __name__ == "__main__":
    main()
