import argparse

from . import __version__


def _cmd_stub(_args):
    print("Not implemented yet")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="openfootprint", description="Public-source OSINT lookup tool")
    parser.add_argument("--version", action="version", version=__version__)

    subparsers = parser.add_subparsers(dest="command")

    lookup = subparsers.add_parser("lookup", help="Run a public-source lookup")
    lookup.set_defaults(func=_cmd_stub)

    sources = subparsers.add_parser("sources", help="List or inspect sources")
    sources_sub = sources.add_subparsers(dest="sources_command")
    sources_list = sources_sub.add_parser("list", help="List available sources")
    sources_list.set_defaults(func=_cmd_stub)
    sources_info = sources_sub.add_parser("info", help="Show details for a source")
    sources_info.add_argument("source_id")
    sources_info.set_defaults(func=_cmd_stub)

    plan = subparsers.add_parser("plan", help="Show a dry-run query plan")
    plan.set_defaults(func=_cmd_stub)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    return int(args.func(args))
