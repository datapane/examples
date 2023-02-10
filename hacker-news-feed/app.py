import requests
import datapane as dp

api_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
response = requests.get(api_url)
post_ids = response.json()

posts = []

for post_id in post_ids[0:3]:
    post_url = f"https://hacker-news.firebaseio.com/v0/item/{post_id}.json"
    post_response = requests.get(post_url)
    post = post_response.json()
    posts.append(post)

posts = sorted(posts, key=lambda d: d["score"], reverse=True)

post_big_number = []


def view_post(params):
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
            dp.Function(
                view_post,
                target="view_post",
                submit_label="View",
                controls=dp.Controls(
                    dp.TextBox("post_id", idx, initial=idx),
                ),
            ),
            columns=2,
        )
    )

dp.serve(
    dp.View(
        dp.Group(
            dp.Text("Text", name="view_post"),
            dp.Group(blocks=post_big_number),
            columns=2,
        )
    )
)
