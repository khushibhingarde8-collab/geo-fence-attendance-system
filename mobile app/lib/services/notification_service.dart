import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:firebase_core/firebase_core.dart';

@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();

  print("Background Notification");
  print(message.notification?.title);
  print(message.notification?.body);
}
class NotificationService {
  final FirebaseMessaging messaging = FirebaseMessaging.instance;

  final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
      FlutterLocalNotificationsPlugin();

  Future<void> initialize() async {
    // Firebase Permission
    NotificationSettings permissionSettings =
    await messaging.requestPermission();

print("Permission: ${permissionSettings.authorizationStatus}");

    String? token = await messaging.getToken();

    print("=================================");
    print("FCM TOKEN:");
    print(token);
    print("=================================");

    const AndroidNotificationChannel channel =
    AndroidNotificationChannel(
      'tracking_channel',
      'Attendance Tracking',
      description: 'Background location tracking',
      importance: Importance.low,
    );

    await flutterLocalNotificationsPlugin
        .resolvePlatformSpecificImplementation<
            AndroidFlutterLocalNotificationsPlugin>()
        ?.createNotificationChannel(channel);

      const AndroidInitializationSettings androidSettings =
        AndroidInitializationSettings('@mipmap/ic_launcher');

    const InitializationSettings settings =
        InitializationSettings(android: androidSettings);

            await flutterLocalNotificationsPlugin.initialize(settings);

const AndroidNotificationChannel alertChannel =
    AndroidNotificationChannel(
      'alert_channel',
      'Geofence Alerts',
      description: 'Warning & Force Checkout Notifications',
      importance: Importance.max,
    );
    
await flutterLocalNotificationsPlugin
    .resolvePlatformSpecificImplementation<
        AndroidFlutterLocalNotificationsPlugin>()
    ?.createNotificationChannel(alertChannel);


    

// Handle notification when app was completely closed
RemoteMessage? initialMessage =
    await FirebaseMessaging.instance.getInitialMessage();

if (initialMessage != null) {
  print("Opened from terminated state");
  print(initialMessage.notification?.title);
  print(initialMessage.notification?.body);

  // Navigate to notification screen if needed
}
    // Foreground Notification
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
  flutterLocalNotificationsPlugin.show(
    message.hashCode,
    message.notification?.title ?? '',
    message.notification?.body ?? '',
    const NotificationDetails(
      android: AndroidNotificationDetails(
        'alert_channel',
        'Geofence Alerts',
        importance: Importance.max,
        priority: Priority.high,
        playSound: true,
        enableVibration: true,

      ),
    ),
  );
});

    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      print("Notification Clicked");
    });
  }
}