import sys
import graphify.cli
import graphify.extract
from graph_spec_design.extractors.custom_rust import extract_rust

def main():
    # Inject our custom extractor to override the default one
    graphify.extract._DISPATCH['.rs'] = extract_rust
    
    # Run the original graphify engine
    sys.exit(graphify.cli.main())

if __name__ == "__main__":
    main()
