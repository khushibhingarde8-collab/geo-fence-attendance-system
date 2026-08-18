import 'package:flutter/material.dart';
import 'dart:async';
import '../../api_service.dart';
import 'login_screen.dart';
import 'employee_list_screen.dart';
import 'live_map_screen.dart';
import 'admin_monthly_report_screen.dart';
import 'employee_master_screen.dart';


class AdminHomeScreen extends StatefulWidget {
  const AdminHomeScreen({super.key});

  @override
  State<AdminHomeScreen> createState() => _AdminHomeScreenState();
}

class _AdminHomeScreenState extends State<AdminHomeScreen> {

  Map<String, dynamic> dashboardData = {
    "employees": 0,
    "present": 0,
    "inside": 0,
    "outside": 0,
    "force_out": 0,
    "absent": 0,
  };
  List<dynamic> notifications = [];

  int previousNotificationCount = 0;

  Timer? timer;

  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    loadDashboard();
    loadNotifications();

     timer = Timer.periodic(
    const Duration(seconds: 10),
    (Timer t) {
      loadDashboard();
      loadNotifications();
    },
  );

  }

  Future<void> loadDashboard() async {
    try {
      final data = await ApiService.getAdminDashboard();

      setState(() {
        dashboardData = data;
        isLoading = false;
      });
    } catch (e) {
      debugPrint("Dashboard Error : $e");

      setState(() {
        isLoading = false;
      });
    }
  }

  Future<void> loadNotifications() async {

  try {

    final data = await ApiService.getAdminNotifications();

    // First time loading
    if (previousNotificationCount == 0) {
      previousNotificationCount = data.length;
    }

    // New notification arrived
    else if (data.length > previousNotificationCount) {

      final latest = data.first;

      String message = latest["message"] ?? "";

      // Show popup only for selected notifications
      if (message.contains("Warning") ||
          message.contains("AUTO FORCE CHECKOUT DONE")) {

        showPopup(message);
      }

      previousNotificationCount = data.length;
    }

    setState(() {
      notifications = data;
    });

  } catch (e) {
    debugPrint("Notification Error: $e");
  }
}
  void _logout(BuildContext context) {
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text("Logout"),
        content: const Text(
          "Are you sure you want to logout?",
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(dialogContext);
            },
            child: const Text("Cancel"),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(dialogContext);

              Navigator.pushAndRemoveUntil(
                context,
                MaterialPageRoute(
                  builder: (_) => const LoginScreen(),
                ),
                (route) => false,
              );
            },
            child: const Text("Logout"),
          ),
        ],
      ),
    );
  }
void showNotifications() {

  showModalBottomSheet(
    context: context,
    isScrollControlled: true,

    builder: (context) {

      return SizedBox(
        height: 500,

        child: notifications.isEmpty
            ? const Center(
                child: Text(
                  "No Notifications Today",
                ),
              )

            : ListView.builder(

                itemCount: notifications.length,

                itemBuilder: (context, index) {

                  final item = notifications[index];

                  return ListTile(

                    leading: const Icon(
                      Icons.notifications,
                      color: Colors.blue,
                    ),

                    title: Text(
                      item["message"] ?? "",
                    ),

                    subtitle: Text(
                      item["created_at"] ?? "",
                    ),

                  );
                },
              ),
      );
    },
  );
}
  void showPopup(String message) {

  showDialog(
    context: context,
    builder: (_) => AlertDialog(
      title: const Text("Alert"),
      content: Text(message),
      actions: [
        TextButton(
          onPressed: () {
            Navigator.pop(context);
          },
          child: const Text("OK"),
        ),
      ],
    ),
  );
}


  @override
  Widget build(BuildContext context) {

    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FB),

      appBar: AppBar(
        backgroundColor: Colors.blue,
        elevation: 0,

        title: const Text(
          "Admin Dashboard",
          style: TextStyle(
            fontWeight: FontWeight.bold,
          ),
        ),

        actions: [

          IconButton(
  icon: Stack(
    children: [

      const Icon(Icons.notifications_none),

      if (notifications.isNotEmpty)
        Positioned(
          right: 0,
          top: 0,
          child: Container(
            padding: const EdgeInsets.all(3),
            decoration: const BoxDecoration(
              color: Colors.red,
              shape: BoxShape.circle,
            ),
            constraints: const BoxConstraints(
              minWidth: 18,
              minHeight: 18,
            ),
            child: Text(
              notifications.length.toString(),
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 10,
              ),
            ),
          ),
        ),
    ],
  ),
    onPressed: () {
      showNotifications();
  },
),

          PopupMenuButton<String>(
            onSelected: (value) {

              if (value == "logout") {
                _logout(context);
              }

            },
            itemBuilder: (context) => const [

              PopupMenuItem<String>(
                value: "logout",
                child: Text("Logout"),
              ),

            ],
          ),

        ],
      ),

      body: isLoading
          ? const Center(
              child: CircularProgressIndicator(),
            )
          : SingleChildScrollView(
              child: Column(
                children: [

                  Container(
                    width: double.infinity,
                    margin: const EdgeInsets.all(16),
                    padding: const EdgeInsets.all(20),

                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [
                          Colors.blue,
                          Colors.lightBlueAccent,
                        ],
                      ),
                      borderRadius:
                          BorderRadius.circular(20),
                    ),

                    child: const Column(
                      crossAxisAlignment:
                          CrossAxisAlignment.start,
                      children: [

                        Text(
                          "Welcome Admin 👋",
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 22,
                            fontWeight:
                                FontWeight.bold,
                          ),
                        ),

                        SizedBox(height: 5),

                        Text(
                          "PCE Attendance Management System",
                          style: TextStyle(
                            color: Colors.white70,
                          ),
                        ),

                      ],
                    ),
                  ),

                  const SizedBox(height: 10),

                  Padding(
                    padding:
                        const EdgeInsets.symmetric(
                            horizontal: 16),
                    child: Row(
                      mainAxisAlignment:
                          MainAxisAlignment
                              .spaceBetween,
                      children: const [

                        Text(
                          "Today's Overview",
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight:
                                FontWeight.bold,
                          ),
                        ),

                        Text(
                          "Live",
                          style: TextStyle(
                            color: Colors.grey,
                          ),
                        ),

                      ],
                    ),
                  ),

                  const SizedBox(height: 10),

                                    Padding(
                    padding: const EdgeInsets.all(16),
                    child: GridView.count(
                      shrinkWrap: true,
                      physics:
                          const NeverScrollableScrollPhysics(),
                      crossAxisCount: 2,
                      crossAxisSpacing: 12,
                      mainAxisSpacing: 12,
                      childAspectRatio: 1.1,
                      children: [

                        GestureDetector(
  onTap: () {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => const EmployeeMasterScreen(),
      ),
    );
  },

                          child: DashboardCard(
                          title: "Employees",
                          value: dashboardData["employees"].toString(),
                          icon: Icons.people,
                          color: Colors.blue,
                        ),
                      ),

                        GestureDetector(
                          onTap: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => const EmployeeListScreen(
                                  status: "present",
                                  title: "Present Employees",
                                ),
                              ),
                            );
                          },
                          child: DashboardCard(
                            title: "Present",
                            value: dashboardData["present"].toString(),
                            icon: Icons.check_circle,
                            color: Colors.green,
                          ),
                        ),

                        GestureDetector(
                          onTap: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => const EmployeeListScreen(
                                  status: "inside",
                                  title: "Inside Employees",
                                ),
                              ),
                            );
                          },
                          child: DashboardCard(
                            title: "Inside",
                            value: dashboardData["inside"].toString(),
                            icon: Icons.home_work,
                            color: Colors.teal,
                          ),
                        ),

                        GestureDetector(
                          onTap: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => const EmployeeListScreen(
                                  status: "outside",
                                  title: "Outside Employees",
                                ),
                              ),
                            );
                          },
                          child: DashboardCard(
                            title: "Outside",
                            value: dashboardData["outside"].toString(),
                            icon: Icons.location_off,
                            color: Colors.orange,
                          ),
                        ),

                        GestureDetector(
                          onTap: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => const EmployeeListScreen(
                                  status: "force_out",
                                  title: "Force Checkout Employees",
                                ),
                              ),
                            );
                          },
                          child: DashboardCard(
                            title: "Force Out",
                            value: dashboardData["force_out"].toString(),
                            icon: Icons.logout,
                            color: Colors.red,
                          ),
                        ),

                        GestureDetector(
                          onTap: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => const EmployeeListScreen(
                                  status: "absent",
                                  title: "Absent Employees",
                                ),
                              ),
                            );
                          },
                          child: DashboardCard(
                            title: "Absent",
                            value: dashboardData["absent"].toString(),
                            icon: Icons.cancel,
                            color: Colors.redAccent,
                          ),
                        ),

                        GestureDetector(
                          onTap: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => const LiveMapScreen(),
                              ),
                            );
                          },
                          child: const DashboardCard(
                            title: "Live Map",
                            value: "",
                            icon: Icons.map,
                            color: Colors.deepPurple,
                          ),
                        ),
                        GestureDetector(
                          onTap: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => const AdminMonthlyReportScreen(),
                              ),
                            );
                          },
                          child: const DashboardCard(
                            title: "Monthly Report",
                            value: "",
                            icon: Icons.analytics,
                            color: Colors.indigo,
                          ),
                        ),

                      ],
                    ),
                  ),

                ],
              ),
            ),
    );
  }
  @override
  void dispose() {
    timer?.cancel();
    super.dispose();
}
}

class DashboardCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color color;

  const DashboardCard({
    super.key,
    required this.title,
    required this.value,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: const [
          BoxShadow(
            color: Colors.black12,
            blurRadius: 6,
            offset: Offset(0, 3),
          ),
        ],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          CircleAvatar(
            radius: 26,
            backgroundColor: color.withOpacity(0.15),
            child: Icon(
              icon,
              color: color,
              size: 28,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            value,
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            title,
            style: const TextStyle(
              fontSize: 15,
              color: Colors.grey,
            ),
          ),
        ],
      ),
    );
  }
}