"""Model classes."""

import dataclasses
import typing


# Here, we use the dataclasses module from the standard library, which allows us
# to quickly create small, simple classes to store data in a more organized way
# than using dictionaries or tuples.
@dataclasses.dataclass
class Issue:
    """Simple representation of a GitHub issue: only 3 attributes are kept."""

    title: str
    body: str
    url: str

    # Adding a method decorated with @classmethod makes this method callable
    # directly on the class:
    #     Issue.from_dict(...)
    # instead of:
    #     issue = Issue(...)
    #     issue.from_dict(...)
    # This is very useful here as it allows us to offer an alternative constructor.
    # The default constructor is used as follows:
    #     Issue(title="A title", body="A body", url="https://a-url.com")
    # Whereas the constructor we provide here can directly take
    # a dictionary as returned by the GitHub API and create an issue from it.
    @classmethod
    def from_dict(cls, dct: typing.Dict[str, typing.Any]) -> "Issue":
        """Construct an issue from a dict such as one returned by the GitHub API."""
        return Issue(title=dct["title"], body=dct["body"], url=dct["html_url"])
