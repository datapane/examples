import typing as t

import requests
import datapane as dp

api_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
print("Connecting to HN feed...")
response = requests.get(api_url, timeout=30)
post_ids = response.json()

posts = []

for post_id in post_ids[0:3]:
    post_url = f"https://hacker-news.firebaseio.com/v0/item/{post_id}.json"
    post_response = requests.get(post_url)
    post = post_response.json()
    posts.append(post)

posts = sorted(posts, key=lambda d: d["score"], reverse=True)

post_big_number = []


def view_post(params: t.Dict):
    global posts
    post = posts[int(params["post_id"])]

    if post.get("url"):
        return dp.Text(post["url"], name="view_post")
    else:
        return dp.Text(post["text"], name="view_post")


for idx, post in enumerate(posts):
    post_big_number.append(
        dp.Group(
            dp.BigNumber(heading=post["title"], value=post["score"]),
            dp.Form(
                on_submit=view_post,
                target="view_post",
                submit_label="View",
                controls=dict(post_id=dp.TextBox(idx, initial=idx)),
            ),
            columns=2,
        )
    )

dp.serve_app(
    dp.Group(
        dp.Text("Text", name="view_post"),
        dp.Group(blocks=post_big_number),
        columns=2,
    )
)
