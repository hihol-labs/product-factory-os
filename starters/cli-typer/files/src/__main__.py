import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("value", nargs="?", default="ready")
    args = parser.parse_args()
    print(f"PFO CLI {args.value}")


if __name__ == "__main__":
    main()

