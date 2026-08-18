import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../../api_service.dart';

class LiveMapScreen extends StatefulWidget {
  const LiveMapScreen({super.key});

  @override
  State<LiveMapScreen> createState() => _LiveMapScreenState();
}

class _LiveMapScreenState extends State<LiveMapScreen> {

  final MapController _mapController = MapController();

  List<dynamic> employees = [];
  List<dynamic> filteredEmployees = [];

  bool isLoading = true;

  Timer? timer;

  final TextEditingController searchController =
      TextEditingController();

  @override
  void initState() {
    super.initState();

    loadEmployees();

    timer = Timer.periodic(
      const Duration(seconds: 5),
      (timer) {
        loadEmployees();
      },
    );

    searchController.addListener(searchEmployee);
  }

  @override
  void dispose() {
    timer?.cancel();
    searchController.dispose();
    super.dispose();
  }

  Future<void> loadEmployees() async {

    try {

      final data =
          await ApiService.getLiveMapEmployees();

      setState(() {

        employees = data;

        filteredEmployees = data;

        isLoading = false;

      });

    } catch (e) {

      print(e);

    }
  }

  void searchEmployee() {

    String query =
        searchController.text.toLowerCase();

    setState(() {

      filteredEmployees = employees.where((emp) {

        return emp["full_name"]
            .toString()
            .toLowerCase()
            .contains(query);

      }).toList();

    });

  }

  Color getMarkerColor(String status){

    if(status=="Inside"){
      return Colors.green;
    }

    if(status=="Outside"){
      return Colors.red;
    }

    return Colors.orange;

  }

  IconData getMarkerIcon(String status){

    if(status=="Inside"){
      return Icons.person_pin_circle;
    }

    if(status=="Outside"){
      return Icons.location_off;
    }

    return Icons.person_pin;

  }

    @override
  Widget build(BuildContext context) {

    return Scaffold(

      appBar: AppBar(
        title: const Text("Live Employee Map"),
        backgroundColor: Colors.blue,
      ),

      body: isLoading
          ? const Center(
              child: CircularProgressIndicator(),
            )
          : Column(

              children: [

                // ==========================
                // SEARCH BAR
                // ==========================

                Padding(
                  padding: const EdgeInsets.all(10),
                  child: TextField(

                    controller: searchController,

                    decoration: InputDecoration(

                      hintText: "Search Employee",

                      prefixIcon: const Icon(Icons.search),

                      border: OutlineInputBorder(
                        borderRadius:
                            BorderRadius.circular(12),
                      ),

                    ),

                  ),
                ),

                // ==========================
                // MAP
                // ==========================

                Expanded(

                  child: FlutterMap(

                    mapController: _mapController,

                    options: MapOptions(

                      initialCenter:

                          filteredEmployees.isNotEmpty

                              ? LatLng(

                                  double.parse(
                                      filteredEmployees.first["latitude"]
                                          .toString()),

                                  double.parse(
                                      filteredEmployees.first["longitude"]
                                          .toString()),
                                )

                              : const LatLng(
                                  18.5204,
                                  73.8567,
                                ),

                      initialZoom: 15,

                    ),

                    children: [

                      // =====================
                      // MAP TILE
                      // =====================

                      TileLayer(

                        urlTemplate:
                            "https://tile.openstreetmap.org/{z}/{x}/{y}.png",

                        userAgentPackageName:
                            "com.example.attendance",

                      ),

                      // =====================
                      // GEOFENCE CIRCLES
                      // =====================

                      CircleLayer(

                        circles:

                            filteredEmployees.map((emp) {

                          return CircleMarker(

                            point: LatLng(

                              double.parse(
                                  emp["office_lat"].toString()),

                              double.parse(
                                  emp["office_lon"].toString()),

                            ),

                            radius:

                                double.parse(
                                    emp["radius"].toString()),

                            useRadiusInMeter: true,

                            borderStrokeWidth: 2,

                            borderColor: Colors.blue,

                            color: Colors.blue.withOpacity(0.15),

                          );

                        }).toList(),

                      ),

                      // =====================
                      // MARKERS
                      // =====================

                      MarkerLayer(

                        markers: [

                          // ====================
                          // OFFICE MARKERS
                          // ====================

                          ...filteredEmployees.map((emp) {

                            return Marker(

                              point: LatLng(

                                double.parse(
                                    emp["office_lat"].toString()),

                                double.parse(
                                    emp["office_lon"].toString()),

                              ),

                              width: 110,

                              height: 70,

                              child: Column(

                                children: [

                                  const Icon(

                                    Icons.business,

                                    color: Colors.blue,

                                    size: 34,

                                  ),

                                  Text(

                                    emp["location_name"],

                                    textAlign: TextAlign.center,

                                    style: const TextStyle(

                                      fontSize: 11,

                                      fontWeight: FontWeight.bold,

                                    ),

                                  ),

                                ],

                              ),

                            );

                          }).toList(),

                          // ====================
                          // EMPLOYEE MARKERS
                          // ====================

                          ...filteredEmployees.map((emp) {

                            return Marker(

                              point: LatLng(

                                double.parse(
                                    emp["latitude"].toString()),

                                double.parse(
                                    emp["longitude"].toString()),

                              ),

                              width: 120,

                              height: 90,

                              child: GestureDetector(

                                onTap: () {

                                  showEmployeeDetails(emp);

                                },

                                child: Column(

                                  children: [

                                    Icon(

                                      getMarkerIcon(
                                          emp["location_status"]),

                                      color: getMarkerColor(
                                          emp["location_status"]),

                                      size: 36,

                                    ),

                                    Container(

                                      padding:
                                          const EdgeInsets.symmetric(

                                        horizontal: 6,

                                        vertical: 2,

                                      ),

                                      decoration: BoxDecoration(

                                        color: Colors.white,

                                        borderRadius:
                                            BorderRadius.circular(8),

                                      ),

                                      child: Text(

                                        emp["full_name"],

                                        style: const TextStyle(

                                          fontWeight:
                                              FontWeight.bold,

                                          fontSize: 11,

                                        ),

                                      ),

                                    ),

                                  ],

                                ),

                              ),

                            );

                          }).toList(),

                        ],

                      ),

                    ],

                  ),

                ),

              ],

            ),

    );
  }
    // ==========================
  // EMPLOYEE DETAILS
  // ==========================
  void showEmployeeDetails(dynamic emp) {

    showModalBottomSheet(

      context: context,
      isScrollControlled: true, // <-- ADD THIS

      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(
          top: Radius.circular(20),
        ),
      ),

      builder: (context) {

        return Padding(

          padding: const EdgeInsets.all(20),

          child: Column(

            mainAxisSize: MainAxisSize.min,

            crossAxisAlignment: CrossAxisAlignment.start,

            children: [

              Center(
                child: Container(
                  width: 60,
                  height: 5,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade400,
                    borderRadius: BorderRadius.circular(20),
                  ),
                ),
              ),

              const SizedBox(height: 20),

              Center(
                child: CircleAvatar(
                  radius: 35,
                  backgroundColor:
                      getMarkerColor(emp["location_status"]),
                  child: const Icon(
                    Icons.person,
                    color: Colors.white,
                    size: 35,
                  ),
                ),
              ),

              const SizedBox(height: 20),

              Center(
                child: Text(
                  emp["full_name"],
                  style: const TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),

              const SizedBox(height: 25),

              ListTile(
                leading: const Icon(Icons.badge),
                title: const Text("Employee ID"),
                subtitle: Text(emp["employee_id"].toString()),
              ),

              ListTile(
                leading: const Icon(Icons.business),
                title: const Text("Assigned Office"),
                subtitle: Text(emp["location_name"]),
              ),

              ListTile(
                leading: const Icon(Icons.location_on),
                title: const Text("Current Status"),
                subtitle: Text(emp["location_status"]),
              ),

              ListTile(
                leading: const Icon(Icons.my_location),
                title: const Text("Current Latitude"),
                subtitle: Text(emp["latitude"].toString()),
              ),

              ListTile(
                leading: const Icon(Icons.my_location),
                title: const Text("Current Longitude"),
                subtitle: Text(emp["longitude"].toString()),
              ),

              ListTile(
                leading: const Icon(Icons.access_time),
                title: const Text("Last Updated"),
                subtitle: Text(
                  emp["last_updated"] ?? "-",
                ),
              ),

              const SizedBox(height: 20),

            ],

          ),

        );

      },

    );

  }

}


