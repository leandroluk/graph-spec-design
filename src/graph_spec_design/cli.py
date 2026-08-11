import os
import sys

# Define a variável ANTES de importar a engine do graphify
if "GRAPHIFY_OUT" not in os.environ:
    os.environ["GRAPHIFY_OUT"] = ".specs/graph"

import graphify.__main__
import graphify.extract
from graph_spec_design.extractors.custom_rust import extract_rust

def main():
    # Inject our custom extractor to override the default one
    graphify.extract._DISPATCH['.rs'] = extract_rust
    
    # Run the original graphify engine
    sys.exit(graphify.__main__.main())

if __name__ == "__main__":
    main()
