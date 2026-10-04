import os
import json
import google.oauth2.credentials
import googleapiclient.discovery
import googleapiclient.http

def get_authenticated_service():
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        print("YouTube credentials missing in Secrets. Skipping upload.")
        return None

    credentials = google.oauth2.credentials.Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret
    )
    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

def upload_short(video_file="final_short.mp4"):
    payload_raw = os.environ.get("PAYLOAD", "{}")
    payload = json.loads(payload_raw) if payload_raw else {}

    product_name = payload.get("product_name", "話題の神アイテム")
    blog_url = payload.get("blog_url", "https://benrinamonohak.blogspot.com/")

    youtube = get_authenticated_service()
    if not youtube:
        print("YouTube service not available. Video generated locally.")
        return

    title = f"【爆売れ】{product_name}が控えめに言って神すぎた…！ #shorts #便利グッズ #ライフハック"
    description = f"""SNSで大バズり中の「{product_name}」を本音レビュー！

👇 詳しいレビュー＆楽天最安値・在庫はこちら
{blog_url}

#shorts #便利グッズ #掃除 #収納 #ライフハック #買ってよかった"""

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": ["shorts", "便利グッズ", "ライフハック", "掃除", "収納", "楽天"],
            "categoryId": "22"  # People & Blogs
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media = googleapiclient.http.MediaFileUpload(video_file, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    
    print(f"Successfully uploaded to YouTube Shorts! Video ID: {response.get('id')}")

if __name__ == "__main__":
    upload_short()
