import json
import urllib.request
import re

MODEL_ID = "https://13f7-34-16-142-45.ngrok-free.app"

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))

        # Cognitoで認証されたユーザー情報を取得
        user_info = None
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            user_info = event['requestContext']['authorizer']['claims']
            print(f"Authenticated user: {user_info.get('email') or user_info.get('cognito:username')}")

        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])

        print("Processing message:", message)
        print("Calling external API:", MODEL_ID)

        # ユーザーメッセージを追加
        conversation_history.append({
            "role": "user",
            "content": message
        })

        # 外部APIに送信するペイロードを作成
        request_payload = json.dumps({
            "message": message,
            "conversationHistory": conversation_history
        }).encode("utf-8")

        # HTTPリクエスト設定
        req = urllib.request.Request(
            MODEL_ID,
            data=request_payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        # 外部APIへリクエスト送信
        with urllib.request.urlopen(req) as res:
            response_body = json.loads(res.read().decode("utf-8"))
            print("External API response:", response_body)

        # アシスタントの応答を履歴に追加
        assistant_response = response_body.get("response", "")
        conversation_history.append({
            "role": "assistant",
            "content": assistant_response
        })

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": conversation_history
            })
        }

    except Exception as error:
        print("Error:", str(error))

        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }
