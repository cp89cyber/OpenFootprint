from openfootprint.nameintel.sherlock_validate import summarize_sherlock_findings


def test_summarize_sherlock_findings_shapes_output():
    summary = summarize_sherlock_findings(
        [
            {
                "entity": {
                    "profile_urls": ["https://github.com/johndoe"],
                    "display_name": "johndoe",
                }
            }
        ]
    )
    assert summary[0]["url"] == "https://github.com/johndoe"

