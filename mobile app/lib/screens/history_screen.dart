import 'package:flutter/material.dart';
import '../api_service.dart';

class HistoryScreen extends StatefulWidget {
  final int empId;

  const HistoryScreen({super.key, required this.empId});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  List<dynamic> history = [];
  bool loading = true;

  @override
  void initState() {
    super.initState();
    loadHistory();
  }

  // =========================
  // LOAD HISTORY FROM API
  // =========================
  Future<void> loadHistory() async {
    try {
      final res = await ApiService.getHistory(
      widget.empId,
    );

      if (!mounted) return;

      setState(() {
        history = res;
        loading = false;
      });
    } catch (e) {
      debugPrint("History Error: $e");

      if (!mounted) return;

      setState(() {
        loading = false;
      });
    }
  }

  // =========================
  // STATUS COLOR (attendance)
  // =========================
  Color getColor(String status) {
    switch (status.toLowerCase()) {
      case "full day":
      case "present":
        return Colors.green;

      case "half day":
        return Colors.orange;

      case "absent":
      case "late":
        return Colors.red;

      case "holiday":
        return Colors.blueGrey;

      default:
        return Colors.grey;
    }
  }

  // =========================
  // CHECKOUT LABEL
  // =========================
  String getCheckoutLabel(String type) {
    switch (type.toLowerCase()) {
      case "force checkout":
      case "auto_force":
        return "System Auto Checkout";

      case "manual":
        return "Manual Checkout";

      default:
        return "-";
    }
  }

  Color getCheckoutColor(String type) {
    switch (type.toLowerCase()) {
      case "force checkout":
      case "auto_force":
        return Colors.red;

      case "manual":
        return Colors.green;

      default:
        return Colors.grey;
    }
  }
  // =========================
  // DATE FORMAT (safe)
  // =========================
  String formatDate(dynamic value) {
    if (value == null) return "-";

    String str = value.toString();
    if (str.contains("T")) {
      return str.split("T")[0];
    }
    return str;
  }

  // =========================
  // DATETIME FORMAT (safe)
  // =========================
  String formatDateTime(dynamic value) {
    if (value == null) return "-";

    String str = value.toString();
    if (str.contains(".")) {
      str = str.split(".")[0];
    }
    return str;
  }
  // ==========================
  // FORMAT WORK HOURS
  // ==========================
  String formatWorkHours(dynamic value) {
    if (value == null) return "-";

    double hours = 0;

    if (value is num) {
      hours = value.toDouble();
    } else {
      hours = double.tryParse(value.toString()) ?? 0;
    }

    int hr = hours.floor();
    int min = ((hours - hr) * 60).round();

    if (min == 60) {
      hr++;
      min = 0;
    }

    if (hr == 0 && min == 0) {
      return "0 min";
    }

    if (hr == 0) {
      return "$min min";
    }

    if (min == 0) {
      return "$hr hr";
    }

    return "$hr hr $min min";
  }
  // =========================
  // UI BUILD
  // =========================
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Attendance History"),
        backgroundColor: Colors.blueAccent,
      ),

      body: loading
          ? const Center(child: CircularProgressIndicator())

          : history.isEmpty
              ? const Center(child: Text("No history found"))

              : RefreshIndicator(
                  onRefresh: loadHistory,
                  child: ListView.builder(
                    itemCount: history.length,
                    itemBuilder: (context, index) {
                      final item = history[index];

                      final status =
                          (item['status'] ?? 'Unknown').toString();

                      final arrivalStatus =
                          (item['arrival_status'] ?? '-').toString();

                      final checkoutType =
                          (item['checkout_type'] ?? '').toString();

                      final overtime =
                          int.tryParse((item['overtime_minutes'] ?? "0").toString()) ?? 0;

                      final isLate =
                          arrivalStatus.toLowerCase() == "late";

                      return Card(
                        margin: const EdgeInsets.symmetric(
                          horizontal: 10,
                          vertical: 6,
                        ),
                        elevation: 3,
                        child: Padding(
                          padding: const EdgeInsets.all(10),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Icon(
                                    Icons.calendar_today,
                                    color: getColor(status),
                                  ),
                                  const SizedBox(width: 8),

                                  Expanded(
                                    child: Text(
                                      formatDate(item['attendance_date']),
                                      style: const TextStyle(
                                        fontWeight: FontWeight.bold,
                                        fontSize: 16,
                                      ),
                                    ),
                                  ),

                                  if (isLate)
                                    const Icon(
                                      Icons.flag,
                                      color: Colors.red,
                                    ),
                                ],
                              ),

                              const Divider(),

                              Text(
                                "Check In: ${formatDateTime(item['check_in'])}",
                              ),

                              Text(
                                "Check Out: ${formatDateTime(item['check_out'])}",
                              ),

                              Text(
                                "Work Hours: ${formatWorkHours(item['work_hours'])}",
                              ),

                              Text(
                                "Arrival Status: $arrivalStatus",
                              ),

                              Text(
                                "Overtime: ${formatWorkHours(item['overtime_hours'])}",
                                style: TextStyle(
                                  color: overtime > 0 ? Colors.green : Colors.grey,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),

                              Text(
                                "Checkout Type: ${getCheckoutLabel(checkoutType)}",
                                style: TextStyle(
                                  color: getCheckoutColor(checkoutType),
                                  fontWeight: FontWeight.bold,
                                ),
                              ),

                              const SizedBox(height: 8),

                              Align(
                                alignment: Alignment.centerRight,
                                child: Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 12,
                                    vertical: 6,
                                  ),
                                  decoration: BoxDecoration(
                                    color: getColor(status),
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  child: Text(
                                    status,
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
    );
  }
}