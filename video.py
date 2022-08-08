# -*- coding: utf-8 -*-

# Sample Python code for youtube.search.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os
import json

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]


def search(song):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey='AIzaSyD_pABPB4xoVTZFG15ZIFIS-CtI8s5SLJg')

    request = youtube.search().list(
        part="snippet",
        maxResults=25,
        q=song + " song"
    )
    response = request.execute()
    # data = json.loads(str(response))
    return response['items'][0]['id']['videoId']

# print(search('outro m83'))