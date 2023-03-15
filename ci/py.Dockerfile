ARG PYTHON_VERSION='3.10'

FROM python:${PYTHON_VERSION}
WORKDIR /app/

# Install the App dependencies
# Note: If your requirements.txt file depends on other files,
#       you should change to 'COPY ./ .'.
# If you don't have a requirements.txt file:
#  - remove the below lines
#  - let us know your usecase, so we can improve Datapane!
COPY ./requirements.txt ./requirements-*.txt ./
RUN \
  echo "Installing dependencies from requirements.txt..." \
  && pip install --no-cache-dir -r requirements.txt

# load your files into the image
# To exclude files, setup a .dockerignore
COPY ./ .



# execute your app (what to run on the server)
CMD exec python app.py
