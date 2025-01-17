---
title: Haystack Application with Streamlit
emoji: 👑
colorFrom: indigo
colorTo: indigo
sdk: streamlit
sdk_version: 1.41.1
app_file: app.py
pinned: false
---

# Template for Haystack Apps with Streamlit

This template [Streamlit](https://docs.streamlit.io/) app is set up for simple [Haystack](https://haystack.deepset.ai/) applications. The template is ready to do **Retrievel Augmented Generation** on example files.

See the ['How to use this template'](#how-to-use-this-template) instructions below to create a simple UI for your own Haystack search pipelines.

Below you will also find instructions on how you could [push this to Hugging Face Spaces 🤗](#pushing-to-hugging-face-spaces-).

## Installation and Running
To run the bare application:
1. Install requirements: `pip install -r requirements.txt`
2. Include all environment variable in a `.env` file
  Example `.env`
  ```
  WEAVIATE_API_KEY="YOUR_KEY"
  MISTRAL_API_KEY="YOUR_KEY" # this demo uses Mistral models by default
  ```
3. Decide on the files and the method to populate your database (Check out instructions in `haystack.py`)
4. Run the streamlit app: `streamlit run app.py`

This will start up the app on `localhost:8501` where you will find a simple search bar. 

## How to use this template
1. Create a new repository from this template or simply open it in a codespace to start playing around 💙
2. Make sure your `requirements.txt` file includes the Haystack (`haystack-ai`) and Streamlit versions you would like to use.
3. Change the code in `utils/haystack.py` if you would like a different pipeline. 
4. Create a `.env` file with all of your configuration settings.
5. Make any UI edits if you'd like to.
6. Run the app as show in [installation and running](#installation-and-running)

### Repo structure
- `./utils`: This is where we have 2 files: 
    - `haystack.py`: Here you will find some functions already set up for you to start creating your Haystack search pipeline. It includes 2 main functions called `start_haystack_pipeline()` which is what we use to create a pipeline and cache it, and `query()` which is the function called by `app.py` once a user query is received.
    - `ui.py`: Use this file for any UI and initial value setups.
- `app.py`: This is the main Streamlit application file that we will run. In its current state it has a sidebar, a simple search bar, a 'Run' button, and a response.
- `./files`: You can use this folder to store files to be indexed.

### What to edit?
There are default pipelines both in `start_document_store()` and `start_haystack_pipeline()`. Change the pipelines to use different document stores, embedding and generative models or update the pipelines as you need. Check out [📚 Useful Resources](#-useful-resources) section for details.

### 📚 Useful Resources
* [Get Started](https://haystack.deepset.ai/overview/quick-start)
* [Docs](https://docs.haystack.deepset.ai/docs/intro)
    * [Creating Custom Components](https://docs.haystack.deepset.ai/docs/custom-components)
* [Tutorials](https://haystack.deepset.ai/tutorials)
* [Integrations](https://haystack.deepset.ai/integrations)
    * [Mistral](https://haystack.deepset.ai/integrations/mistral)
    * [Weaviate](https://haystack.deepset.ai/integrations/weaviate-document-store)

## Pushing to Hugging Face Spaces 🤗

Below is an example GitHub action that will let you push your Streamlit app straight to the Hugging Face Hub as a Space.

A few things to pay attention to:

1. Create a New Space on Hugging Face with the Streamlit SDK.
2. Create a Hugging Face token on your HF account.
3. Create a secret on your GitHub repo called `HF_TOKEN` and put your Hugging Face token here.
4. If you're using DocumentStores or APIs that require some keys/tokens, make sure these are provided as a secret for your HF Space too!
5. This readme is set up to tell HF spaces that it's using streamlit and that the app is running on `app.py`, make any changes to the frontmatter of this readme to display the title, emoji etc you desire.
6. Create a file in `.github/workflows/hf_sync.yml`. Here's an example that you can change with your own information, and an [example workflow](https://github.com/TuanaCelik/should-i-follow/blob/main/.github/workflows/hf_sync.yml) working for the [Should I Follow demo](https://huggingface.co/spaces/deepset/should-i-follow)

```yaml
name: Sync to Hugging Face hub
on:
  push:
    branches: [main]

  # to run this workflow manually from the Actions tab
  workflow_dispatch:

jobs:
  sync-to-hub:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
        with:
          fetch-depth: 0
          lfs: true
      - name: Push to hub
        env:
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
        run: git push --force https://{YOUR_HF_USERNAME}:$HF_TOKEN@{YOUR_HF_SPACE_REPO} main
```
