import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_background_service/flutter_background_service.dart';
import 'package:flutter_background_service_android/flutter_background_service_android.dart';
import 'package:geolocator/geolocator.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../api_service.dart';

Future<void> initializeService() async {
  final service = FlutterBackgroundService();

  await service.configure(
    androidConfiguration: AndroidConfiguration(
      onStart: onStart,
      autoStart: false,
      isForegroundMode: true,
      notificationChannelId: "tracking_channel",
      initialNotificationTitle: "Attendance Tracking",
      initialNotificationContent: "Tracking employee location",
      foregroundServiceNotificationId: 100,
    ),
    iosConfiguration: IosConfiguration(
      autoStart: false,
      onForeground: onStart,
      onBackground: onIosBackground,
    ),
  );
}

@pragma('vm:entry-point')
Future<bool> onIosBackground(ServiceInstance service) async {
  WidgetsFlutterBinding.ensureInitialized();
  return true;
}

Future<void> startBackgroundService() async {
  final service = FlutterBackgroundService();

  bool isRunning = await service.isRunning();

  if (!isRunning) {
    await service.startService();
    debugPrint("Background Service Started");
    }else {
    debugPrint("Background Service Already Running");
  }
}

Future<void> stopBackgroundService() async {
  final service = FlutterBackgroundService();
  service.invoke("stopService");
}

@pragma('vm:entry-point')
void onStart(ServiceInstance service) async {
  WidgetsFlutterBinding.ensureInitialized();

  if (service is AndroidServiceInstance) {
    service.setForegroundNotificationInfo(
      title: "Attendance Tracking",
      content: "Tracking employee location...",
    );
  }

  Timer? timer;

  service.on("stopService").listen((event) {
    timer?.cancel();
    service.stopSelf();
  });

  Future<void> sendLocation() async {
    try {
      if (service is AndroidServiceInstance) {
        if (!await service.isForegroundService()) {
          return;
        }

        service.setForegroundNotificationInfo(
          title: "Attendance Tracking",
          content: "Last Update: ${DateTime.now()}",
        );
      }

      bool enabled = await Geolocator.isLocationServiceEnabled();

     if (!enabled) {
        debugPrint("GPS Disabled");
        return;
      }

      LocationPermission permission =
          await Geolocator.checkPermission();

      if (permission != LocationPermission.always) {
        debugPrint("Background Permission Missing");
        return;
      }

       Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.bestForNavigation,
        timeLimit: const Duration(seconds: 20),
      );

      final prefs = await SharedPreferences.getInstance();

      int? empId = prefs.getInt("emp_id");


      if (empId == null) {
          debugPrint("Employee ID Missing");
          return;
        }

      debugPrint("--------------------------------");
      debugPrint("Employee : $empId");
      debugPrint("Latitude : ${position.latitude}");
      debugPrint("Longitude : ${position.longitude}");

      final response = await ApiService.trackLocation(
          empId,
          position.latitude,
          position.longitude,
        );

      debugPrint("API Response : $response");

       if (response["status"] == "force_checkout" ||
            response["status"] == "already_checked_out") {
          timer?.cancel();
          service.stopSelf();
          return;
        }

        debugPrint("Background Location Sent");
      } catch (e) {
        debugPrint("Background Error: $e");
      }
    }

    await sendLocation();

    timer = Timer.periodic(
    const Duration(minutes: 5),
    (_) async {
      await sendLocation();
    },
  );
}
