import 'package:flutter/material.dart';
import '../../api_service.dart';

class EmployeeMasterScreen extends StatefulWidget {
  const EmployeeMasterScreen({super.key});

  @override
  State<EmployeeMasterScreen> createState() =>
      _EmployeeMasterScreenState();
}

class _EmployeeMasterScreenState
    extends State<EmployeeMasterScreen> {
  List<dynamic> employees = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    loadEmployees();
  }

  Future<void> loadEmployees() async {
    try {
      final data = await ApiService.getAllEmployees();

      setState(() {
        employees = data;
        isLoading = false;
      });
    } catch (e) {
      debugPrint("Employee Error: $e");

      setState(() {
        isLoading = false;
      });
    }
  }

  Widget buildEmployeeCard(dynamic emp) {
    return Card(
      margin: const EdgeInsets.symmetric(
        horizontal: 12,
        vertical: 8,
      ),
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(15),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment:
              CrossAxisAlignment.start,
          children: [

            /// Employee Name
            Row(
              children: [
                CircleAvatar(
                  radius: 24,
                  backgroundColor:
                      Colors.blue.shade100,
                  child: const Icon(
                    Icons.person,
                    color: Colors.blue,
                  ),
                ),

                const SizedBox(width: 12),

                Expanded(
                  child: Text(
                    emp["full_name"] ?? "",
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight:
                          FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),

            const Divider(height: 25),

            Row(
              children: [
                const Icon(
                  Icons.badge,
                  color: Colors.blue,
                  size: 20,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    "Employee ID : ${emp["employee_id"]}",
                    style: const TextStyle(
                      fontSize: 15,
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 10),

            Row(
              children: [
                const Icon(
                  Icons.confirmation_number,
                  color: Colors.deepPurple,
                  size: 20,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    "Employee Code : ${emp["employee_code"] ?? "-"}",
                    style: const TextStyle(
                      fontSize: 15,
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 10),

            Row(
              crossAxisAlignment:
                  CrossAxisAlignment.start,
              children: [
                const Icon(
                  Icons.email,
                  color: Colors.green,
                  size: 20,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    "Email : ${emp["email"] ?? "-"}",
                    style: const TextStyle(
                      fontSize: 15,
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 10),

            Row(
              crossAxisAlignment:
                  CrossAxisAlignment.start,
              children: [
                const Icon(
                  Icons.location_on,
                  color: Colors.orange,
                  size: 20,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    "Assigned Office : ${emp["location_name"] ?? "Not Assigned"}",
                    style: const TextStyle(
                      fontSize: 15,
                    ),
                  ),
                ),
              ],
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
        title: const Text("Employees"),
        backgroundColor: Colors.blue,
      ),

      body: isLoading
          ? const Center(
              child:
                  CircularProgressIndicator(),
            )
          : employees.isEmpty
              ? const Center(
                  child: Text(
                    "No Employees Found",
                    style: TextStyle(
                      fontSize: 18,
                    ),
                  ),
                )
              : RefreshIndicator(
                  onRefresh: loadEmployees,
                  child: ListView.builder(
                    itemCount: employees.length,
                    itemBuilder:
                        (context, index) {
                      return buildEmployeeCard(
                        employees[index],
                      );
                    },
                  ),
                ),
    );
  }
}