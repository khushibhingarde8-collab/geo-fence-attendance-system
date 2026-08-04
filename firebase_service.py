import os
import firebase_admin
from firebase_admin import credentials, messaging

firebase_enabled = False

# Initialize Firebase only if the JSON file exists
if not firebase_admin._apps:
    if os.path.exists("serviceAccountKey.json"):
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
        firebase_enabled = True
        print("Firebase initialized successfully.")
    else:
        print("Firebase disabled - serviceAccountKey.json not found.")


def send_push_notification(token, title, body):
    """
    Send high-priority push notification to a single Android device.
    """

    # Skip notification if Firebase is disabled
    if not firebase_enabled:
        print("Firebase disabled. Notification skipped.")
        return True

    try:
        message = messaging.Message(
            token=token,

            notification=messaging.Notification(
                title=title,
                body=body,
            ),

            android=messaging.AndroidConfig(
                priority="high",
                notification=messaging.AndroidNotification(
                    channel_id="alert_channel",
                    sound="default",
                    default_sound=True,
                    default_vibrate_timings=True,
                ),
            ),

            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound="default",
                    )
                )
            ),
        )

        response = messaging.send(message)

        print("===================================")
        print("Notification Sent Successfully")
        print("Message ID:", response)
        print("===================================")

        return True

    except Exception as e:
        print("===================================")
        print("Notification Error")
        print(e)
        print("===================================")

        return False