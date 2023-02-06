import datapane as dp
from rembg import remove
from PIL import Image


def fix_image(params):
    image = Image.open(params["upload"])
    fixed = remove(image)
    image.save("original.png", "PNG")
    fixed.save("fixed.png", "PNG")

    return dp.Group(
        dp.Group(
            "Original Image 📷",
            dp.Media(file="original.png"),
            dp.Attachment(file="original.png"),
        ),
        dp.Group(
            "Fixed Image 🔧", dp.Media(file="fixed.png"), dp.Attachment(file="fixed.png")
        ),
        columns=2,
    )


v = dp.View(
    dp.Group(
        """## Remove the background from your image
🐶 Try uploading an image to watch the background magically removed. Full quality images can be downloaded from the sidebar. This code is open source and available here on GitHub. Special thanks to the <a href="https://github.com/danielgatis/rembg">rembg</a> library 😁""",
        dp.Function(
            fix_image, target="results", controls=dp.Controls(dp.File("upload"))
        ),
        columns=2,
    ),
    dp.Group(fix_image({"upload": open("zebra.jpg", "rb")}), name="results"),
)

dp.serve(v)
