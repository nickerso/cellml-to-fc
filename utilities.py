#!/usr/bin/env python3

import argparse
from pathlib import Path
import sys
from libcellml_python_utils import cellml


def validate_model(file_path, strict_mode):
    model = cellml.parse_model(file_path, strict_mode)
    if model:
        cellml.validate_model(model)
        # del model


def convert_model(file_path, add_ids, output):
    model = cellml.parse_model(file_path, False)
    if model:
        model_string = cellml.print_model(model, add_ids)
        if output:
            with output.open("w") as f:
                f.write(model_string)
        else:
            print(model_string)


def summarize(file_path, verbose):
    size = Path(file_path).stat().st_size
    print(f"File: {file_path}")
    print(f"Size: {size} bytes")
    if verbose:
        print(f"Absolute path: {Path(file_path).resolve()}")


def main():
    parser = argparse.ArgumentParser(description="Perform various actions on a CellML file.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: validate
    parser_validate = subparsers.add_parser("validate", help="Validate the model")
    parser_validate.add_argument("input_file", help='Path to the input CellML file')
    parser_validate.add_argument('-s', '--strict', action='store_true',
                                 help='Validate in strict mode.')

    # Subcommand: convert
    parser_convert = subparsers.add_parser("convert", help="Convert input CellML model to CellML 2")
    parser_convert.add_argument("input_file", help='Path to the input CellML file')
    parser_convert.add_argument("-n", "--num-lines", type=int, default=5, help="Number of lines to show (default: 5)")
    parser_convert.add_argument('-i', '--add-ids', action='store_true',
                                help='If set, make sure all CellML elements have an ID attribute')
    parser_convert.add_argument('-f', '--force', action='store_true',
                                help='Overwrite any existing file at the output location')
    parser_convert.add_argument("-o", "--output", type=Path,
                                help="Path to output file; fallback to stdout if not provided")

    # Subcommand: summarize
    parser_summary = subparsers.add_parser("summarize", help="Print file summary")
    parser_summary.add_argument("input_file", help='Path to the input file')
    parser_summary.add_argument("-v", "--verbose", action="store_true", help="Show additional file details")

    args = parser.parse_args()
    file_path = Path(args.input_file)
    if not file_path.is_file():
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)

    if args.command == "validate":
        validate_model(file_path, args.strict)
    elif args.command == "convert":
        if args.output:
            if args.output.exists():
                if args.force:
                    print(f'Warning: forcing overwrite of existing file {args.output}')
                else:
                    print(f"Error: Output file '{args.output}' already exists. Use a different name or delete it.",
                          file=sys.stderr)
                    sys.exit(1)
        convert_model(file_path, args.add_ids, args.output)
    elif args.command == "summarize":
        summarize(file_path, args.verbose)


if __name__ == "__main__":
    main()
