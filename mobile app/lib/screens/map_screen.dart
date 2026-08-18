import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

class MapScreen extends StatefulWidget {
  final double? officeLat;
  final double? officeLon;
  final double? userLat;
  final double? userLon;

  const MapScreen({
    super.key,
    this.officeLat,
    this.officeLon,
    this.userLat,
    this.userLon,
  });

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  @override
  Widget build(BuildContext context) {
    final officeLat = widget.officeLat ?? 19.8762;
    final officeLon = widget.officeLon ?? 75.3433;

    final hasUserLocation =
        widget.userLat != null && widget.userLon != null;

    final userLat = widget.userLat ?? 0.0;
    final userLon = widget.userLon ?? 0.0;

    return Scaffold(
      appBar: AppBar(
        title: const Text("Geo Attendance Map"),
        backgroundColor: Colors.blueAccent,
      ),

      body: FlutterMap(
        options: MapOptions(
          initialCenter: LatLng(officeLat, officeLon),
          initialZoom: 15,
        ),

        children: [
          // =========================
          // MAP TILE LAYER
          // =========================
          TileLayer(
            urlTemplate: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
            userAgentPackageName: 'com.example.geo_attendance_app',
          ),

          // =========================
          // MARKERS
          // =========================
          MarkerLayer(
            markers: [
              // OFFICE MARKER
              Marker(
                point: LatLng(officeLat, officeLon),
                width: 50,
                height: 50,
                child: const Icon(
                  Icons.location_on,
                  color: Colors.blue,
                  size: 40,
                ),
              ),

              // USER MARKER (ONLY IF AVAILABLE)
              if (hasUserLocation)
                Marker(
                  point: LatLng(userLat, userLon),
                  width: 50,
                  height: 50,
                  child: const Icon(
                    Icons.person_pin_circle,
                    color: Colors.red,
                    size: 40,
                  ),
                ),
            ],
          ),
        ],
      ),

      // =========================
      // LEGEND (BOTTOM INFO)
      // =========================
      bottomNavigationBar: Container(
        padding: const EdgeInsets.all(12),
        color: Colors.white,
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: const [
            Row(
              children: [
                Icon(Icons.location_on, color: Colors.blue),
                SizedBox(width: 5),
                Text("Office"),
              ],
            ),
            Row(
              children: [
                Icon(Icons.person_pin_circle, color: Colors.red),
                SizedBox(width: 5),
                Text("You"),
              ],
            ),
          ],
        ),
      ),
    );
  }
}