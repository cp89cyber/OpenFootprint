from openfootprint.cli import build_parser


def test_cli_has_nameintel_subcommand():
    parser = build_parser()
    args = parser.parse_args(["nameintel", "--first", "John", "--last", "Doe", "--dry-run"])
    assert args.command == "nameintel"

