import typing as t
import string

import datapane as dp


class TimelineEntry(t.TypedDict):
    time: str
    icon: str
    action: str
    name: str
    description: str


# ## Templates and assets
# We can add support for more icons and colors by updating this `dict`.
icon_design = {
    "actor": {
        "color": "bg-slate-400",
        "icon": """<svg class="h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M10 8a3 3 0 100-6 3 3 0 000 6zM3.465 14.493a1.23 1.23 0 00.41 1.412A9.957 9.957 0 0010 18c2.31 0 4.438-.784 6.131-2.1.43-.333.604-.903.408-1.41a7.002 7.002 0 00-13.074.003z" /></svg>""",
    },
    "thumbs-up": {
        "color": "bg-indigo-500",
        "icon": """<svg class="h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M1 8.25a1.25 1.25 0 112.5 0v7.5a1.25 1.25 0 11-2.5 0v-7.5zM11 3V1.7c0-.268.14-.526.395-.607A2 2 0 0114 3c0 .995-.182 1.948-.514 2.826-.204.54.166 1.174.744 1.174h2.52c1.243 0 2.261 1.01 2.146 2.247a23.864 23.864 0 01-1.341 5.974C17.153 16.323 16.072 17 14.9 17h-3.192a3 3 0 01-1.341-.317l-2.734-1.366A3 3 0 006.292 15H5V8h.963c.685 0 1.258-.483 1.612-1.068a4.011 4.011 0 012.166-1.73c.432-.143.853-.386 1.011-.814.16-.432.248-.9.248-1.388z" /></svg>""",
    },
    "code": {
        "color": "bg-amber-500",
        "icon": """<svg class="h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"> <path fill-rule="evenodd" d="M4.25 2A2.25 2.25 0 002 4.25v11.5A2.25 2.25 0 004.25 18h11.5A2.25 2.25 0 0018 15.75V4.25A2.25 2.25 0 0015.75 2H4.25zm4.03 6.28a.75.75 0 00-1.06-1.06L4.97 9.47a.75.75 0 000 1.06l2.25 2.25a.75.75 0 001.06-1.06L6.56 10l1.72-1.72zm4.5-1.06a.75.75 0 10-1.06 1.06L13.44 10l-1.72 1.72a.75.75 0 101.06 1.06l2.25-2.25a.75.75 0 000-1.06l-2.25-2.25z" clip-rule="evenodd" /></svg>""",
    },
    "check": {
        "color": "bg-emerald-500",
        "icon": """<svg class="h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z" clip-rule="evenodd" /></svg>""",
    },
    "cross": {
        "color": "bg-rose-500",
        "icon": """<svg class="h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" /></svg>""",
    },
}


# The template for individual Timeline entries.
template_timeline_children_html = string.Template(
    (
        """
<li>
    <div class="relative pb-8">
        <span class="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200" aria-hidden="true"></span>
        <div class="relative flex space-x-3">
            <div>
                <span class="h-8 w-8 rounded-full ${color} flex items-center justify-center ring-8 ring-white">
                    ${icon}
                </span>
            </div>
            <div class="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                <div>
                    <p class="text-sm text-gray-500">${action} <span class="font-medium text-gray-900">${name}</span></p>
                    <p class="mt-2 text-sm text-gray-500">${description}</p>
                </div>
                <div class="whitespace-nowrap text-right text-sm text-gray-500">
                    <time>${time}</time>
                </div>
            </div>
        </div>
    </div>
</li>
"""
    )
)


# The template for the timeline container. We're including Tailwind CSS too.
template_timeline_parent_html = string.Template(
    (
        """
<script src="https://cdn.tailwindcss.com"></script>
<div class="flow-root max-w-prose">
  <ul role="list" class="-mb-8">
   ${children}
  </ul>
</div>
"""
    )
)


def make_timeline(items: t.List[TimelineEntry]) -> dp.HTML:
    """
    Timeline component

    Return a Timeline for using in a Datapane View

    The Timeline component expects a `list` TimelineEntry `dicts` with the following keys:
    - `time` is a string, so it can be something like a date, a time, "5 days ago", "12h", and more.
    - `icon` changes the icon and its background color, default options are `actor`, `check`, `cross`, `code`, and `thumbs-up`.
    - `action` starts off the timeline entry, e.g. "Completed the interview with".
    - `name` completes the first line of the timeline entry, e.g. "Datapane", which paired with the action will read "Completed the interview with Datapane".
    - `description` allows for more information to be added to the timeline entry. HTML works here too!

    All keys in the dict are optional.

    :param items: List of Timeline Entries
    :return: dp.Block
    """

    timeline_children_html = ""

    for item in items:
        timeline_children_html += template_timeline_children_html.safe_substitute(
            color=icon_design[item.get("icon", "actor")]["color"],
            icon=icon_design[item.get("icon", "actor")]["icon"],
            time=item.get("time", ""),
            action=item.get("action", ""),
            name=item.get("name", ""),
            description=item.get("description", ""),
        )

    timeline_parent_html = template_timeline_parent_html.safe_substitute(children=timeline_children_html)

    return dp.HTML(timeline_parent_html)


def example() -> dp.HTML:
    """Return an example timeline based on sample data"""
    # ## Load data
    #
    # Sample timeline data
    items: t.List[TimelineEntry] = [
        {
            "time": "Jan 1994",
            "icon": "code",
            "action": "Python 1.0 was released by the",
            "name": "Python Software Foundation",
            "description": "The major new features included in this release were the functional programming tools <code>lambda</code>, <code>map</code>, <code>filter</code> and <code>reduce</code>.",
        },
        {
            "time": "Oct 2009",
            "icon": "cross",
            "action": "Regrets were shared by ",
            "name": "Guido van Rossum",
            "description": '"I would not have the feature at all if I had to do it over." (<a class="underline text-gray-600" href="https://mail.python.org/pipermail/python-ideas/2009-October/006157.html">on <code>for-else</code> and <code>while-else</code></a>).',
        },
        {
            "time": "Unknown",
            "icon": "thumbs-up",
            "action": "Python was enjoyed by",
            "name": "Many developers",
            "description": "Python has thrived and been enjoyed by many developers throughout the years!",
        },
        {
            "time": "22h",
            "icon": "check",
            "action": "Completed their journey with",
            "name": "Datapane Timeline",
            "description": "Thank you for joining us on this journey through component demonstration.",
        },
        {
            "time": "Now",
            "icon": "actor",
            "action": "A Datapane user tries the",
            "name": "Datapane Timeline",
            "description": 'Ready to give it a go? <img src="https://uploads-ssl.webflow.com/633eb64a2d33ad2e879f0287/6343097598f0f607ab58508d_6331d1d0412eafd8a9f25f97_code_to_app-p-1080-p-1080.png">',
        },
    ]

    return make_timeline(items)
