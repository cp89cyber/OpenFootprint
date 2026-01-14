import argparse

from openfootprint.core.config import load_config
from openfootprint.core.inputs import LookupInputs
from openfootprint.core.pipeline import run_lookup
from openfootprint.sources.registry import SourceRegistry
from openfootprint.sources.developer.github import SOURCE as GITHUB
from openfootprint.sources.developer.gitlab import SOURCE as GITLAB
from openfootprint.sources.developer.codeberg import SOURCE as CODEBERG
from openfootprint.sources.social.reddit import SOURCE as REDDIT
from openfootprint.sources.social.hackernews import SOURCE as HN
from openfootprint.sources.social.mastodon import SOURCE as MASTODON
from openfootprint.sources.blogs.devto import SOURCE as DEVTO
from openfootprint.sources.blogs.medium import SOURCE as MEDIUM
from openfootprint.sources.blogs.wordpress import SOURCE as WORDPRESS
from openfootprint.sources.directories.wikidata import SOURCE as WIKIDATA
from openfootprint.sources.directories.orcid import SOURCE as ORCID
from openfootprint.sources.directories.openalex import SOURCE as OPENALEX

from . import __version__


def _registry() -> SourceRegistry:
    return SourceRegistry(
        [
            GITHUB,
            GITLAB,
            CODEBERG,
            REDDIT,
            HN,
            MASTODON,
            DEVTO,
            MEDIUM,
            WORDPRESS,
            WIKIDATA,
            ORCID,
            OPENALEX,
        ]
    )

def _filtered_registry(config: dict) -> SourceRegistry:
    sources_cfg = config.get("sources", {})
    enabled = list(sources_cfg.get("enabled", []))
    disabled = list(sources_cfg.get("disabled", []))
    return _registry().filtered(enabled, disabled)


def _cmd_lookup(args) -> int:
    config = load_config(args.config)
    if args.output:
        config["output"]["runs_dir"] = args.output
    inputs = LookupInputs.from_raw(args.username, args.email, args.phone, args.name)
    result = run_lookup(inputs, _filtered_registry(config), config)
    print(result["console"])
    return 0


def _cmd_sources_list(_args) -> int:
    for source in _registry().list_sources():
        print(f"{source.source_id}\t{source.name}\t{source.category}")
    return 0


def _cmd_sources_info(args) -> int:
    source = _registry().get(args.source_id)
    if not source:
        print("Source not found")
        return 1
    inputs = ", ".join(sorted(source.supported_inputs))
    print(f"{source.source_id} - {source.name}\nCategory: {source.category}\nInputs: {inputs}")
    return 0


def _cmd_plan(args) -> int:
    from openfootprint.core.plan import build_plan

    config = load_config(args.config)
    inputs = LookupInputs.from_raw(args.username, args.email, args.phone, args.name)
    plan = build_plan(inputs, _filtered_registry(config))
    for item in plan:
        print(f"{item.source_id}\t{item.input_type}\t{item.url}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="openfootprint", description="Public-source OSINT lookup tool")
    parser.add_argument("--version", action="version", version=__version__)

    subparsers = parser.add_subparsers(dest="command")

    lookup = subparsers.add_parser("lookup", help="Run a public-source lookup")
    lookup.add_argument("--username")
    lookup.add_argument("--email")
    lookup.add_argument("--phone")
    lookup.add_argument("--name")
    lookup.add_argument("--config")
    lookup.add_argument("--output")
    lookup.set_defaults(func=_cmd_lookup)

    sources = subparsers.add_parser("sources", help="List or inspect sources")
    sources_sub = sources.add_subparsers(dest="sources_command")
    sources_list = sources_sub.add_parser("list", help="List available sources")
    sources_list.set_defaults(func=_cmd_sources_list)
    sources_info = sources_sub.add_parser("info", help="Show details for a source")
    sources_info.add_argument("source_id")
    sources_info.set_defaults(func=_cmd_sources_info)

    plan = subparsers.add_parser("plan", help="Show a dry-run query plan")
    plan.add_argument("--username")
    plan.add_argument("--email")
    plan.add_argument("--phone")
    plan.add_argument("--name")
    plan.add_argument("--config")
    plan.set_defaults(func=_cmd_plan)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    return int(args.func(args))
