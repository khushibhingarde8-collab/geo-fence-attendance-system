import 'dart:async';
///import 'dart:ffi';
import 'package:geolocator/geolocator.dart';
import '../api_service.dart';

class LocationService {

  // =====================================================
  // GET CURRENT LOCATION (SAFE + IMPROVED)
  // =====================================================
  static Future<Position?> getCurrentLocation() async {
    try {
      bool serviceEnabled =
          await Geolocator.isLocationServiceEnabled();

      print("GPS Enabled: $serviceEnabled");

      if (!serviceEnabled) {
        print("❌ GPS is disabled");
        return null;
      }

      LocationPermission permission =
          await Geolocator.checkPermission();

      print("Permission: $permission");

      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }

      if (permission == LocationPermission.deniedForever) {
        print("❌ Permission denied forever");
        return null;
      }

       print("STEP 3: Getting Current Position");

      Position position =
          await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.best,
        ///timeLimit: const Duration(seconds: 10),
      );

      print("CURRENT LAT = ${position.latitude}");
      print("CURRENT LON = ${position.longitude}");

      return position;

      } catch (e) {

      print("LOCATION ERROR = $e");
      return null;
    }
  }

  // ==========================
  // AUTO TRACKING
  // ========================== 
  static Timer? _timer;

  static Future<void> startTracking(int empId) async {

    if (_timer != null) {
      print("Tracking already running");
      return;
    }

    print("========== TRACKING STARTED ==========");

    // =====================================
    // SEND LOCATION IMMEDIATELY
    // =====================================
    try {

      final pos = await getCurrentLocation();

      if (pos != null) {

        print("Sending Initial Location...");
        print("LAT = ${pos.latitude}");
        print("LON = ${pos.longitude}");

        final res = await ApiService.trackLocation(
          empId,
          pos.latitude,
          pos.longitude,
        );

        print("Initial Server Response = $res");
      }

    } catch (e) {
      print("Initial Tracking Error = $e");
    }


// =====================================
    // CONTINUOUS TRACKING
    // =====================================
    _timer = Timer.periodic(
      const Duration(minutes: 5), // Change to 5 after testing
      (timer) async {

        print("========== AUTO TRACK ==========");

        final pos = await getCurrentLocation();

        if (pos != null) {

          print("Tracking LAT = ${pos.latitude}");
          print("Tracking LON = ${pos.longitude}");

          try {

            final res = await ApiService.trackLocation(
              empId,
              pos.latitude,
              pos.longitude,
            );

            print("Server Response = $res");

          } catch (e) {

            print("API ERROR = $e");
          }

        } else {

          print("Location not available");
        }

        print("================================");
      },
    );
  }

  // ==========================
  // STOP TRACKING
  // ==========================
  static void stopTracking() {

    _timer?.cancel();
    _timer = null;

    print("Tracking stopped");
  }
}





      