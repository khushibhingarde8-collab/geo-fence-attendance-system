import 'package:flutter/material.dart';
import '../../api_service.dart';

class EmployeeListScreen extends StatefulWidget {
  final String status;
  final String title;

  const EmployeeListScreen({
    super.key,
    required this.status,
    required this.title,
  });

  @override
  State<EmployeeListScreen> createState() => _EmployeeListScreenState();
}

class _EmployeeListScreenState extends State<EmployeeListScreen> {
  List<dynamic> employees = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    loadEmployees();
  }

  Future<void> loadEmployees() async {
    try {
      final data =
          await ApiService.getEmployeesByStatus(widget.status);

      setState(() {
        employees = data;
        isLoading = false;
      });
    } catch (e) {
      print(e);

      setState(() {
        isLoading = false;
      });
    }
  }

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

  if (hr == 0 && min == 0) return "0 min";
  if (hr == 0) return "$min min";
  if (min == 0) return "$hr hr";

  return "$hr hr $min min";
}

  Widget buildCard(dynamic emp) {
    return Card(
      elevation: 4,
      margin: const EdgeInsets.symmetric(
        horizontal: 12,
        vertical: 8,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(15),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [

            Row(
              children: [

                const CircleAvatar(
                  radius: 22,
                  child: Icon(Icons.person),
                ),

                const SizedBox(width: 12),

                Expanded(
                  child: Text(
                    emp["full_name"] ?? "",
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 18,
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 15),

            Row(
              children: [
                const Icon(Icons.badge,
                    size: 18,
                    color: Colors.blue),
                const SizedBox(width: 8),
                Text(
                  "Employee ID : ${emp["employee_id"]}",
                ),
              ],
            ),

            const SizedBox(height: 8),

            if (emp["check_in"] != null)
              Row(
                children: [
                  const Icon(Icons.login,
                      size: 18,
                      color: Colors.green),
                  const SizedBox(width: 8),
                  Text(
                    "Check In : ${emp["check_in"]}",
                  ),
                ],
              ),

            if (emp["check_out"] != null)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Row(
                  children: [
                    const Icon(Icons.logout,
                        size: 18,
                        color: Colors.red),
                    const SizedBox(width: 8),
                    Text(
                      "Check Out : ${emp["check_out"]}",
                    ),
                  ],
                ),
              ),

              if (emp["work_hours"] != null)
  Padding(
    padding: const EdgeInsets.only(top: 8),
    child: Row(
      children: [
        const Icon(
          Icons.schedule,
          size: 18,
          color: Colors.blue,
        ),
        const SizedBox(width: 8),
        Text(
          "Work Hours : ${formatWorkHours(emp["work_hours"])}",
        ),
      ],
    ),
  ),

  if (emp["overtime_hours"] != null)
  Padding(
    padding: const EdgeInsets.only(top: 8),
    child: Row(
      children: [
        const Icon(
          Icons.timer,
          size: 18,
          color: Colors.deepPurple,
        ),
        const SizedBox(width: 8),
        Text(
          "Overtime : ${formatWorkHours(emp["overtime_hours"])}",
        ),
      ],
    ),
  ),

              if (emp["status"] != null)
                Padding(
                  padding: const EdgeInsets.only(top: 8),
                  child: Row(
                    children: [
                      const Icon(
                        Icons.assignment_turned_in,
                        size: 18,
                        color: Colors.green,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        "Attendance : ${emp["status"]}",
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),

            if (emp["location_status"] != null)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Row(
                  children: [
                    const Icon(Icons.location_on,
                        size: 18,
                        color: Colors.orange),
                    const SizedBox(width: 8),
                    Text(
                      "Status : ${emp["location_status"]}",
                    ),
                  ],
                ),
              ),

            if (emp["outside_count"] != null)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Row(
                  children: [
                    const Icon(Icons.warning,
                        color: Colors.red),
                    const SizedBox(width: 8),
                    Text(
                      "Outside Count : ${emp["outside_count"]}",
                    ),
                  ],
                ),
              ),

            if (emp["checkout_type"] != null)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Row(
                  children: [
                    const Icon(Icons.info,
                        color: Colors.deepOrange),
                    const SizedBox(width: 8),
                    Text(
                      emp["checkout_type"],
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
  Widget build(BuildContext context) {

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
        backgroundColor: Colors.blue,
      ),

      body: isLoading
          ? const Center(
              child: CircularProgressIndicator(),
            )
          : employees.isEmpty
              ? const Center(
                  child: Text(
                    "No Employees Found",
                    style: TextStyle(fontSize: 18),
                  ),
                )
              : RefreshIndicator(
                  onRefresh: loadEmployees,
                  child: ListView.builder(
                    itemCount: employees.length,
                    itemBuilder: (context, index) {
                      return buildCard(
                        employees[index],
                      );
                    },
                  ),
                ),
    );
  }
}