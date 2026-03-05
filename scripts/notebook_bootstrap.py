#!/usr/bin/env python3
"""Small helper to bootstrap notebook sessions consistently."""

from mechelen_parking import get_default_paths


def main() -> None:
    paths = get_default_paths()
    print("Project root:", paths.root)
    print("Data processed:", paths.data_processed)
    print("Figures:", paths.figures)
    print("\nNotebook import block:")
    print("from mechelen_parking import get_train_mask, standardize_columns, get_default_paths")


if __name__ == "__main__":
    main()
