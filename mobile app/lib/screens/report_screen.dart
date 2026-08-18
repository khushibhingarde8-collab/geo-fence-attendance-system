import 'package:flutter/material.dart';
import '../api_service.dart';
import '../services/pdf_service.dart';

const List<String> months = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December"
];

class ReportScreen extends StatefulWidget {
  final int empId;

  const ReportScreen({
    Key? key,
    required this.empId,
  }) : super(key: key);

  @override
  State<ReportScreen> createState() => _ReportScreenState();
}

class _ReportScreenState extends State<ReportScreen> {
  int month = DateTime.now().month;
  int year = DateTime.now().year;

  Map<String, dynamic>? report;
  bool loading = false;

  @override
  void initState() {
    super.initState();
    loadReport();
  }

  Future<void> loadReport() async {
    setState(() {
      loading = true;
    });

    try {
      final res = await ApiService.getReport(
        widget.empId,
        month,
        year,
      );

      print("REPORT RESPONSE = $res");

      setState(() {
        report = res;
        loading = false;
      });
    } catch (e) {
      print("REPORT ERROR = $e");

      setState(() {
        loading = false;
      });
    }
  }

  Widget card(String title, String value, Color color) {
    return Card(
      elevation: 4,
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: Icon(
          Icons.bar_chart,
          color: color,
        ),
        title: Text(
          title,
          style: const TextStyle(
            fontWeight: FontWeight.w600,
          ),
        ),
        trailing: Text(
          value,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }

  void downloadReportPDF() {
    if (report != null && report!.isNotEmpty) {
      PDFService.generateReportPDF(report!);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Monthly Report"),
        backgroundColor: Colors.blueAccent,
      ),
      body: loading
          ? const Center(
              child: CircularProgressIndicator(),
            )
          : Padding(
              padding: const EdgeInsets.all(15),
              child: Column(
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: DropdownButton<int>(
                          value: month,
                          isExpanded: true,
                          items: List.generate(
                            12,
                            (i) => DropdownMenuItem(
                              value: i + 1,
                              child: Text(months[i]),
                            ),
                          ),
                          onChanged: (val) {
                            setState(() {
                              month = val!;
                            });
                            loadReport();
                          },
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: DropdownButton<int>(
                          value: year,
                          isExpanded: true,
                          items: List.generate(
                            5,
                            (i) {
                              int y = DateTime.now().year + i;
                              return DropdownMenuItem(
                                value: y,
                                child: Text("$y"),
                              );
                            },
                          ),
                          onChanged: (val) {
                            setState(() {
                              year = val!;
                            });
                            loadReport();
                          },
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),

                  if (report != null && report!.isNotEmpty) ...[
                    card(
                      "Present",
                      "${report!['present']}",
                      Colors.green,
                    ),
                    card(
                      "Absent",
                      "${report!['absent']}",
                      Colors.red,
                    ),
                    card(
                      "Half Day",
                      "${report!['half_day']}",
                      Colors.orange,
                    ),
                    card(
                      "Leave",
                      "${report!['leave']}",
                      Colors.purple,
                    ),
                    card(
                      "Total Hours",
                      "${report!['total_work_hours']}",
                      Colors.blue,
                    ),

                    const SizedBox(height: 10),

                    Card(
                      color: Colors.grey.shade300,
                      child: ListTile(
                        title: const Text(
                          "Attendance Percentage",
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        trailing: Text(
                          "${report!['attendance_percent']}%",
                          style: const TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),

                    const SizedBox(height: 25),

                    ElevatedButton.icon(
                      onPressed: downloadReportPDF,
                      icon: const Icon(Icons.download),
                      label: const Text("Download PDF"),
                    ),
                  ] else
                    const Expanded(
                      child: Center(
                        child: Text(
                          "No report available",
                          style: TextStyle(
                            fontSize: 18,
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),
    );
  }
}