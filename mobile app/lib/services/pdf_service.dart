import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:printing/printing.dart';

class PDFService {
  static Future<void> generateReportPDF(
      Map<String, dynamic> data) async {
    final pdf = pw.Document();

    String safe(dynamic v) => (v == null || v.toString().isEmpty) ? "-" : v.toString();

    final now = DateTime.now();
    final formattedDate =
        "${now.day.toString().padLeft(2, '0')}-${now.month.toString().padLeft(2, '0')}-${now.year}";

    pdf.addPage(
      pw.Page(
        pageFormat: PdfPageFormat.a4,
        margin: const pw.EdgeInsets.all(25),
        build: (pw.Context context) {
          return pw.Column(
            crossAxisAlignment: pw.CrossAxisAlignment.start,
            children: [

              // =========================
              // HEADER
              // =========================
              pw.Container(
                width: double.infinity,
                padding: const pw.EdgeInsets.all(15),
                decoration: pw.BoxDecoration(
                  color: PdfColors.blue800,
                  borderRadius: pw.BorderRadius.circular(8),
                ),
                child: pw.Column(
                  children: [
                    pw.Text(
                      "ATTENDANCE MANAGEMENT SYSTEM",
                      style: pw.TextStyle(
                        color: PdfColors.white,
                        fontSize: 18,
                        fontWeight: pw.FontWeight.bold,
                      ),
                    ),
                    pw.SizedBox(height: 5),
                    pw.Text(
                      "Monthly Attendance Report",
                      style: const pw.TextStyle(
                        color: PdfColors.white,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),

              pw.SizedBox(height: 20),

              // =========================
              // EMPLOYEE DETAILS
              // =========================
              pw.Container(
                padding: const pw.EdgeInsets.all(12),
                decoration: pw.BoxDecoration(
                  border: pw.Border.all(color: PdfColors.grey400),
                  borderRadius: pw.BorderRadius.circular(6),
                ),
                child: pw.Column(
                  crossAxisAlignment: pw.CrossAxisAlignment.start,
                  children: [
                    pw.Text(
                      "Employee Details",
                      style: pw.TextStyle(
                        fontSize: 14,
                        fontWeight: pw.FontWeight.bold,
                        color: PdfColors.blue800,
                      ),
                    ),
                    pw.Divider(),

                    pw.Text("Employee ID : ${safe(data['emp_id'])}"),
                    pw.Text("Employee Name : ${safe(data['employee_name'])}"),
                    pw.Text("Month : ${safe(data['month'])}"),
                    pw.Text("Year : ${safe(data['year'])}"),
                  ],
                ),
              ),

              pw.SizedBox(height: 20),

              // =========================
              // SUMMARY TITLE
              // =========================
              pw.Text(
                "Attendance Summary",
                style: pw.TextStyle(
                  fontSize: 15,
                  fontWeight: pw.FontWeight.bold,
                  color: PdfColors.blue800,
                ),
              ),

              pw.SizedBox(height: 10),

              // =========================
              // TABLE
              // =========================
              pw.Table(
                border: pw.TableBorder.all(color: PdfColors.grey500),
                children: [

                  _row("Metric", "Value", isHeader: true),

                  _row("Present", safe(data['present'])),
                  _row("Absent", safe(data['absent'])),
                  _row("Half Day", safe(data['half_day'])),
                  _row("Leave", safe(data['leave'])),
                  _row("Total Work Hours", safe(data['total_work_hours'])),

                ],
              ),

              pw.SizedBox(height: 20),

              // =========================
              // ATTENDANCE %
              // =========================
              pw.Container(
                width: double.infinity,
                padding: const pw.EdgeInsets.all(15),
                decoration: pw.BoxDecoration(
                  color: PdfColors.green100,
                  borderRadius: pw.BorderRadius.circular(8),
                  border: pw.Border.all(color: PdfColors.green700),
                ),
                child: pw.Column(
                  children: [
                    pw.Text(
                      "Attendance Percentage",
                      style: pw.TextStyle(
                        fontSize: 14,
                        fontWeight: pw.FontWeight.bold,
                      ),
                    ),
                    pw.SizedBox(height: 5),
                    pw.Text(
                      "${safe(data['attendance_percent'])}%",
                      style: pw.TextStyle(
                        fontSize: 24,
                        fontWeight: pw.FontWeight.bold,
                        color: PdfColors.green800,
                      ),
                    ),
                  ],
                ),
              ),

              pw.Spacer(),

              // =========================
              // FOOTER
              // =========================
              pw.Divider(),

              pw.Center(
                child: pw.Text(
                  "Generated on $formattedDate",
                  style: const pw.TextStyle(
                    fontSize: 10,
                    color: PdfColors.grey700,
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );

    await Printing.layoutPdf(
      onLayout: (format) async => pdf.save(),
    );
  }

  // =========================
  // TABLE ROW BUILDER
  // =========================
  static pw.TableRow _row(String a, String b, {bool isHeader = false}) {
    return pw.TableRow(
      decoration: isHeader
          ? const pw.BoxDecoration(color: PdfColors.blue100)
          : null,
      children: [
        _cell(a, isHeader),
        _cell(b, isHeader),
      ],
    );
  }

  // =========================
  // CELL WIDGET
  // =========================
  static pw.Widget _cell(String text, bool header) {
    return pw.Padding(
      padding: const pw.EdgeInsets.all(8),
      child: pw.Text(
        text,
        style: pw.TextStyle(
          fontWeight: header ? pw.FontWeight.bold : pw.FontWeight.normal,
        ),
      ),
    );
  }
}