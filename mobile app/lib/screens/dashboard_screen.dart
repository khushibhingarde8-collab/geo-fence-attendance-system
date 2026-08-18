import 'package:flutter/material.dart';
import '../api_service.dart';
import '../services/location_service.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'dart:async';
import 'package:permission_handler/permission_handler.dart';
import 'notification_screen.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/background_service.dart';

class DashboardScreen extends StatefulWidget {
  final int empId;

  const DashboardScreen({super.key, required this.empId});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  Map<String, dynamic>? data;

  double lat = 0;
  double lon = 0;

  bool loading = true;
  bool isLocationCaptured = false;
  bool isLoadingAction = false;

  Timer? _refreshTimer;

  @override
  void initState() {
    super.initState();

    requestPermissions(); // ✅ ADD THIS HERE FIRST

    loadAll();

    LocationService.startTracking(widget.empId);

    // SAFE AUTO REFRESH
    _refreshTimer = Timer.periodic(const Duration(seconds: 10), (timer) {
      if (mounted) {
        loadAll();
      }
    });
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  // =========================
  // LOAD DASHBOARD
  // =========================
  Future<void> loadAll() async {
    try {
      final res = await ApiService.getDashboardSummary(
        widget.empId,
      );

      if (!mounted) return;

      setState(() {
        data = res;
        loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        loading = false;
      });
    }
  }

  Future<void> requestPermissions() async {
    await Permission.location.request();
    await Permission.locationWhenInUse.request();
    await Permission.locationAlways.request();

  }
  // =========================
  // CAPTURE LOCATION
  // =========================
  Future<void> captureLocation() async {
    if (!mounted) return;

    setState(() => loading = true);

    try {
      final pos = await LocationService.getCurrentLocation();

      if (pos != null) {
        lat = pos.latitude;
        lon = pos.longitude;

        print("LAT = $lat");
        print("LON = $lon");

         final response=
            await ApiService.trackLocation(widget.empId, lat, lon);

        print("TRACK RESPONSE=$response");
        final res = await ApiService.getDashboardSummary(widget.empId);

        if (!mounted) return;

        setState(() {
          data = res;
          isLocationCaptured = true;
          loading = false;
        });
        } else {
        if (!mounted) return;

        setState(() => loading = false);
      }
    } catch (e) {
      if (!mounted) return;

      setState(() => loading = false);
    }
  }


  // =========================
  // CHECK IN
  // =========================
  Future<void> checkIn() async {
    if (!isLocationCaptured) {
      _showMessage({
        "status": "warning",
        "message": "Capture location first",
      });
      return;
    }

    if (isLoadingAction) return;

    setState(() => isLoadingAction = true);

    try {
      final res = await ApiService.markAttendance(
        widget.empId,
        lat,
        lon,
        "checkin",
      );

      

      if (res["status"] == "success") {

        _showMessage(res);

          } else if (res["already_checked_in"] == true) {

        _showMessage({
          "status": "warning",
          "message": "Already checked in today",
        });
      } else {

      _showMessage(res);

      }

      await loadAll();
    } catch (e) {
      _showMessage({
        "status": "error",
        "message": "Check in failed",
      });
    }

    if (mounted) {
      setState(() => isLoadingAction = false);
    }
  }

  // =========================
  // CHECK OUT
  // =========================
  Future<void> checkOut() async {
    if (!isLocationCaptured) {
      _showMessage({
        "status": "warning",
        "message": "Capture location first",
      });
      return;
    }

    if (isLoadingAction) return;

    setState(() => isLoadingAction = true);

    try {
      final res = await ApiService.markAttendance(
        widget.empId,
        lat,
        lon,
        "checkout",
      );

      if (res["already_checked_out"] == true) {
        _showMessage({
          "status": "warning",
          "message": "Already checked out today",
        });
      } else {
        _showMessage(res);
      }

      await loadAll();
    } catch (e) {
      _showMessage({
        "status": "error",
        "message": "Check out failed",
      });
    }

    if (mounted) {
      setState(() => isLoadingAction = false);
    }
  }

  // =========================
  // SNACKBAR MESSAGE
  // =========================
  void _showMessage(Map<String, dynamic>? res) {
    if (!mounted || res == null) return;

    String status = res["status"] ?? "error";
    String message = res["message"] ?? "Something went wrong";

    Color color = status == "success"
        ? Colors.green
        : status == "warning"
            ? Colors.orange
            : Colors.red;

    ScaffoldMessenger.of(context).clearSnackBars();

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: color,
      ),
    );
  }

  // =========================
  // CARD WIDGET
  // =========================
  Widget card(String title, String value, Color color, IconData icon) {
    return Expanded(
      child: Container(
        margin: const EdgeInsets.all(6),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: color,
          borderRadius: BorderRadius.circular(15),
        ),
        child: Column(
          children: [
            Icon(icon, color: Colors.white),
            const SizedBox(height: 10),
            Text(
              value,
              style: const TextStyle(
                fontSize: 18,
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              title,
              style: const TextStyle(color: Colors.white),
            ),
          ],
        ),
      ),
    );
  }

  // =========================
  // UI
  // =========================
  @override
  Widget build(BuildContext context) {
    if (loading || data == null) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    double officeLat =
        (data?["office_lat"] as num?)?.toDouble() ?? 0.0;

    double officeLon =
        (data?["office_lon"] as num?)?.toDouble() ?? 0.0;

    return Scaffold(
      appBar: AppBar(
        title: const Text("Employee Dashboard"),
        backgroundColor: Colors.blueAccent,
        actions: [

          IconButton(
            icon: const Icon(Icons.notifications),

            onPressed: () {

              Navigator.push(
              context,
              MaterialPageRoute(
              builder: (_) => NotificationScreen(
              empId: widget.empId,
            ),
          ),
        );

      },
    ),

  ],
      ),



      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                "Welcome, ${data?['employee_name'] ?? 'Employee'}",
                style: const TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                ),
              ),

              Text("Employee ID: ${data?['employee_id'] ?? widget.empId}"),

              const SizedBox(height: 15),

              Row(
                children: [
                  card("Present", "${data?['present'] ?? 0}", Colors.green, Icons.check),
                  card("Absent", "${data?['absent'] ?? 0}", Colors.red, Icons.close),
                ],
              ),

              Row(
                children: [
                  card("Half Day", "${data?['half_day'] ?? 0}", Colors.orange, Icons.timer),
                  card("Leave", "${data?['leave'] ?? 0}", Colors.purple, Icons.event_busy),
                ],
              ),

              Row(
                children: [
                  card("Holidays", "${data?['holidays'] ?? 0}", Colors.blue, Icons.beach_access),
                  const Expanded(child: SizedBox()),
                ],
              ),

              const SizedBox(height: 20),

              Card(
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(15),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(15),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        "Location Status",
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),

                      const SizedBox(height: 10),

                      Text("Office Lat: $officeLat"),
                      Text("Office Lon: $officeLon"),

                      const SizedBox(height: 10),

                      if (isLocationCaptured) ...[
                        Text("Your Lat: $lat"),
                        Text("Your Lon: $lon"),
                        Text(
                          "Distance: ${data?['distance'] ?? '-'} m",
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        Text(
                          data?['inside_geofence'] == true
                              ? "Inside Office"
                              : "Outside Office",
                          style: TextStyle(
                            color: data?['inside_geofence'] == true
                                ? Colors.green
                                : Colors.red,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],

                      const SizedBox(height: 10),

                      Text(
                        "Last Updated: ${data?['last_updated'] ?? '-'}",
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 15),

              ElevatedButton.icon(
                onPressed: captureLocation,
                icon: const Icon(Icons.my_location),
                label: const Text("Capture Location"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue,
                  minimumSize: const Size(double.infinity, 50),
                ),
              ),

              const SizedBox(height: 15),

              Row(
                children: [
                  Expanded(
                    child: ElevatedButton(
                      onPressed: isLoadingAction ? null : checkIn,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green,
                      ),
                      child: const Text("CHECK IN"),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: isLoadingAction ? null : checkOut,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red,
                      ),
                      child: const Text("CHECK OUT"),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 15),

              SizedBox(
                height: 220,
                child: FlutterMap(
                  options: MapOptions(
                    initialCenter: isLocationCaptured
                        ? LatLng(lat, lon)
                        : LatLng(officeLat, officeLon),
                    initialZoom: 15,
                  ),
                  children: [
                    TileLayer(
                      urlTemplate:
                          "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                      userAgentPackageName: 'geo_attendance_app',
                    ),
                    MarkerLayer(
                      markers: [
                        if (isLocationCaptured)
                          Marker(
                            point: LatLng(lat, lon),
                            width: 40,
                            height: 40,
                            child: const Icon(
                              Icons.person_pin_circle,
                              color: Colors.red,
                              size: 35,
                            ),
                          ),
                        Marker(
                          point: LatLng(officeLat, officeLon),
                          width: 40,
                          height: 40,
                          child: const Icon(
                            Icons.location_on,
                            color: Colors.blue,
                            size: 35,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}