import argparse

from scripts.batch_generate_derivatives import batch_generate_derivatives


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("collection_id", help="Collection ID")

    action_args = parser.add_argument_group("actions")
    action_args.add_argument(
        "-d", "--derivatives", dest="actions",
        action="append_const", const="derivatives",
        help="Batch generate derivatives"
    )

    args = parser.parse_args()
    if args.actions:
        actions = set(args.actions)
    else:
        parser.error("Please supply an action.")
    collection_id = args.collection_id

    if "derivatives" in actions:
        batch_generate_derivatives(collection_id)


if __name__ == "__main__":
    main()
