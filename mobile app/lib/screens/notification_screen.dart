import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:geo_attendance_app/api_service.dart';

class NotificationScreen extends StatefulWidget {
  final int empId;

  const NotificationScreen({
    super.key,
    required this.empId,
  });

  @override
  State<NotificationScreen> createState() =>
      _NotificationScreenState();
}

class _NotificationScreenState
    extends State<NotificationScreen> {

  List notifications = [];
  bool loading = true;

  @override
  void initState() {
    super.initState();
    loadNotifications();
  }

  Future<void> loadNotifications() async {

    try {

      print("Loading notifications for Employee: ${widget.empId}");

      final response = await http.get(
        Uri.parse(
          "${ApiService.baseUrl}/api/employee_notifications/${widget.empId}",
        ),
      );

      if (response.statusCode == 200) {

        if (mounted) {
          setState(() {
            notifications = jsonDecode(response.body);
            loading = false;
          });
        }

      } else {

        if (mounted) {
          setState(() {
            loading = false;
          });
        }

      }

    } catch (e) {

      print("Notification Error: $e");

      if (mounted) {
        setState(() {
          loading = false;
        });
      }

    }
  }

  @override
  Widget build(BuildContext context) {

    return Scaffold(

      appBar: AppBar(
        title: const Text("Notifications"),
      ),

      body: loading

          ? const Center(
              child: CircularProgressIndicator(),
            )

          : notifications.isEmpty

              ? const Center(
                  child: Text(
                    "No Notifications",
                    style: TextStyle(fontSize: 18),
                  ),
                )

              : RefreshIndicator(
                  onRefresh: loadNotifications,
                  child: ListView.builder(
                    itemCount: notifications.length,

                    itemBuilder: (context, index) {

                      return Card(

                        margin: const EdgeInsets.symmetric(
                          horizontal: 10,
                          vertical: 6,
                        ),

                        child: ListTile(

                          leading: const Icon(
                            Icons.notifications,
                            color: Colors.orange,
                          ),

                          title: Text(
                            notifications[index]["message"] ?? "",
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                            ),
                          ),

                          subtitle: Text(
                            notifications[index]["created_at"] ?? "",
                          ),

                        ),

                      );

                    },

                  ),
                ),

    );

  }
}