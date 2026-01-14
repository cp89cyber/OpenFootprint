from openfootprint.sources.helpers import make_html_profile_source


SOURCE = make_html_profile_source("hackernews", "Hacker News", "social", "https://news.ycombinator.com/user?id={username}")
