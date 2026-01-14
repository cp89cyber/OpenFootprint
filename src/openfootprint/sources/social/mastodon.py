from openfootprint.sources.base import RequestSpec, Source
from openfootprint.sources.helpers import HtmlProfileSource


class MastodonSource(HtmlProfileSource):
    def build_requests(self, inputs) -> list[RequestSpec]:
        if not inputs.username or "@" not in inputs.username:
            return []
        user, instance = inputs.username.split("@", 1)
        url = f"https://{instance}/@{user}"
        return [RequestSpec(url=url, input_type="username")]


_helper = MastodonSource("mastodon", "Mastodon", "social", "")
SOURCE = Source(
    source_id="mastodon",
    name="Mastodon",
    category="social",
    supported_inputs={"username"},
    build_requests=_helper.build_requests,
    parse=_helper.parse,
)
