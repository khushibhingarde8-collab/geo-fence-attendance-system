import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:firebase_messaging/firebase_messaging.dart';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:open_filex/open_filex.dart';
import 'package:flutter/foundation.dart';

import 'mobile_pdf_download.dart'
    if (dart.library.html) 'web_pdf_download.dart';

class ApiService {

  static const String baseUrl = "https://purchases-valentine-fridge-schedule.trycloudflare.com/api";

  // =====================================================
  // SAFE PARSERS
  // =====================================================
  static int safeInt(dynamic value, [int fallback = 0]) {
    if (value == null) return fallback;
    if (value is int) return value;
    if (value is String) return int.tryParse(value) ?? fallback;
    if (value is double) return value.toInt();
    return fallback;
  }

  static double safeDouble(dynamic value, [double fallback = 0.0]) {
    if (value == null) return fallback;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value) ?? fallback;
    return fallback;
  }

  // =====================================================
// LOGIN
// =====================================================
static Future<Map<String, dynamic>> login(
  String email,
  String password,
) async {
  try {
    // Get FCM token
    String? token = await FirebaseMessaging.instance.getToken();

    final response = await http
        .post(
          Uri.parse("$baseUrl/login"),
          headers: {
            "Content-Type": "application/json",
          },
          body: jsonEncode({
            "email": email,
            "password": password,
            "fcm_token": token,
          }),
        )
        .timeout(const Duration(seconds: 15));

    final data = jsonDecode(response.body);

    return {
      "status": data["status"] ?? "error",
      "employee_id": safeInt(data["employee_id"], 0),
      "employee_name": data["employee_name"] ?? "",
      "first_login": safeInt(data["first_login"], 0),
    };
  } catch (e) {
    return {
      "status": "error",
      "employee_id": 0,
      "employee_name": "",
      "first_login": 0,
      "error": e.toString(),
    };
  }
}
  // =====================================================
  // LOGOUT
  // =====================================================
  static Future<Map<String, dynamic>> logout(int userId) async {
    final response = await http
        .post(
          Uri.parse("$baseUrl/logout"),
          headers: {"Content-Type": "application/json"},
          body: jsonEncode({"user_id": userId}),
        )
        .timeout(const Duration(seconds: 10));

    return jsonDecode(response.body);
  }


  // =====================================================
  // ADMIN LOGIN
  // =====================================================
  static Future<Map<String, dynamic>> adminLogin(
    String email,
    String password,
  ) async {
    try {
      String? token = await FirebaseMessaging.instance.getToken();

      final response = await http
          .post(
            Uri.parse("$baseUrl/admin/login"),
            headers: {
              "Content-Type": "application/json",
            },
            body: jsonEncode({
              "email": email,
              "password": password,
              "fcm_token": token,
            }),
          )
          .timeout(const Duration(seconds: 15));

      return jsonDecode(response.body);

    } catch (e) {
      return {
        "status": "error",
        "message": e.toString(),
      };
    }
  }
  // =====================================================
  // FORGOT PASSWORD
  // =====================================================
  static Future<Map<String, dynamic>> forgotPassword(
    String email,
    String dob,
    String newPassword,
    String confirmPassword,
  ) async {
    final response = await http
        .post(
          Uri.parse("$baseUrl/forgot_password"),
          headers: {"Content-Type": "application/json"},
          body: jsonEncode({
            "email": email,
            "dob": dob,
            "new_password": newPassword,
            "confirm_password": confirmPassword,
          }),
        )
        .timeout(const Duration(seconds: 15));

    return jsonDecode(response.body);
  }

  // =====================================================
  // SEND RESET OTP
  // =====================================================
  static Future<Map<String,dynamic>> sendResetOTP(
      String email
  ) async {

    final response = await http.post(
      Uri.parse("$baseUrl/send_reset_otp"),
      headers:{
        "Content-Type":"application/json"
      },
      body: jsonEncode({
        "email":email
      }),
    ).timeout(
      const Duration(seconds:15)
    );

    return jsonDecode(response.body);
  }

  // =====================================================
  // VERIFY RESET OTP
  // =====================================================
  static Future<Map<String,dynamic>> verifyResetOTP(
      String email,
      String otp
  ) async {

    final response = await http.post(
      Uri.parse("$baseUrl/verify_reset_otp"),
      headers:{
        "Content-Type":"application/json"
      },
      body: jsonEncode({
        "email":email,
        "otp":otp
      }),
    ).timeout(
      const Duration(seconds:15)
    );

    return jsonDecode(response.body);
  }

  // =====================================================
  // RESET PASSWORD
  // =====================================================
  static Future<Map<String,dynamic>> resetPassword(
    String email,
    String newPassword,
  ) async {

    final response = await http.post(
      Uri.parse("$baseUrl/reset_password"),
      headers: {
        "Content-Type": "application/json",
      },
      body: jsonEncode({
        "email": email,
        "new_password": newPassword,
      }),
    ).timeout(
      const Duration(seconds: 15),
    );

    return jsonDecode(response.body);
  }
  // =====================================================
  // CHANGE PASSWORD
  // =====================================================
  static Future<Map<String, dynamic>> changePassword(
    int employeeId,
    String newPassword,
  ) async {
    final response = await http
        .post(
          Uri.parse("$baseUrl/change_password"),
          headers: {"Content-Type": "application/json"},
          body: jsonEncode({
            "employee_id": employeeId,
            "new_password": newPassword,
          }),
        )
        .timeout(const Duration(seconds: 10));

    return jsonDecode(response.body);
  }

  // =====================================================
  // MARK ATTENDANCE (THIS FIXES YOUR ERROR)
  // =====================================================
  static Future<Map<String, dynamic>> markAttendance(
    int employeeId,
    double lat,
    double lon,
    String action,
  ) async {
    final response = await http
        .post(
          Uri.parse("$baseUrl/mark_attendance"),
          headers: {"Content-Type": "application/json"},
          body: jsonEncode({
            "employee_id": employeeId,
            "latitude": lat,
            "longitude": lon,
            "action": action,
          }),
        )
        .timeout(const Duration(seconds: 15));

    final data = jsonDecode(response.body);

    if (data["distance"] != null) {
      data["distance"] = (data["distance"] as num).toDouble();
    }

    return data;
  }

  // =====================================================
  // TRACK LOCATION
  // =====================================================
  static Future<Map<String, dynamic>> trackLocation(
    int employeeId,
    double lat,
    double lon,
  ) async {
    final response = await http
        .post(
          Uri.parse("$baseUrl/track_location"),
          headers: {"Content-Type": "application/json"},
          body: jsonEncode({
            "employee_id": employeeId,
            "latitude": lat,
            "longitude": lon,
          }),
        )
        .timeout(const Duration(seconds: 15));

    return jsonDecode(response.body);
  }

  static Future<List<dynamic>> getDepartments() async {

      try {

        final response = await http.get(
          Uri.parse(
            "$baseUrl/get_departments",
          ),
        );

        print("DEPARTMENTS : ${response.body}");

        if (response.statusCode == 200) {

          return jsonDecode(response.body);

        }

        return [];

      } catch (e) {

        print("Department Error : $e");

        return [];

      }

    }

  static Future<List<dynamic>> getMonthlyReport(

      int month,
      int year,
      String department,
      {
        String? employeeId,
      }

  ) async {


    try {


      String url =
          "$baseUrl/monthly_matrix_report"
          "?month=$month"
          "&year=$year";


      if (department != "All" &&
          department.isNotEmpty) {

        url += "&department=$department";

      }


      if (employeeId != null &&
          employeeId.isNotEmpty) {

        url += "&employee_id=$employeeId";

      }



      print("REQUEST URL : $url");


      final response =
          await http.get(
            Uri.parse(url),
          );


      print("STATUS : ${response.statusCode}");

      print("BODY : ${response.body}");



      if(response.statusCode == 200){


        final json =
        jsonDecode(response.body);



        // YOUR BACKEND RETURNS "data"
        return json["data"] ?? [];


      }



      return [];



    }

    catch(e){

      print(
        "MONTHLY REPORT ERROR : $e"
      );

      return [];

    }


  }
  static Future<Map<String, dynamic>> getEmployeeMonthlyDetail(

    int empId,
    int month,
    int year,

  ) async {

    final response = await http.get(

      Uri.parse(

        "$baseUrl/monthly_detailed_report"
        "?employee_id=$empId"
        "&month=$month"
        "&year=$year",

      ),

    ).timeout(

      const Duration(seconds: 15),

    );

    print("DETAIL STATUS : ${response.statusCode}");
    print("DETAIL BODY : ${response.body}");

    if (response.statusCode == 200) {

      return jsonDecode(response.body);

    }

    throw Exception("Failed to load employee detail");

  }

  // =====================================================
  // DOWNLOAD MONTHLY REPORT PDF
  // =====================================================

  static Future<void> downloadMonthlyReportPDF(
      int month,
      int year,
  ) async {

    final url =
        "$baseUrl/download_monthly_report_pdf"
        "?month=$month"
        "&year=$year";

    print("PDF URL : $url");

    // =========================
    // WEB
    // =========================
    if (kIsWeb) {
      downloadPdfWeb(url);
      return;
    }

    // =========================
    // ANDROID / MOBILE
    // =========================

    final response = await http.get(
      Uri.parse(url),
    );

    print("PDF STATUS : ${response.statusCode}");

    if (response.statusCode == 200) {

      Directory directory =
          await getApplicationDocumentsDirectory();

      String path =
          "${directory.path}/Monthly_Attendance_Report.pdf";

      File file = File(path);

      await file.writeAsBytes(
        response.bodyBytes,
      );

      print("PDF SAVED : $path");

      await OpenFilex.open(path);

    } else {

      throw Exception("PDF Download Failed");
    }
  }
  // =====================================================
  // DASHBOARD
  // =====================================================
  static Future<Map<String, dynamic>> getDashboardSummary(
    int employeeId,
  ) async {
    final response = await http
        .get(Uri.parse("$baseUrl/dashboard_summary/$employeeId"))
        .timeout(const Duration(seconds: 15));

    final raw = jsonDecode(response.body);

    return {
      "employee_id": safeInt(raw["employee_id"]),
      "employee_name": raw["employee_name"] ?? "",
      "present": safeInt(raw["present"]),
      "absent": safeInt(raw["absent"]),
      "half_day": safeInt(raw["half_day"]),
      "leave": safeInt(raw["leave"]),
      "holidays": safeInt(raw["holidays"]),
      "distance": safeDouble(raw["distance"]),
      "office_lat": safeDouble(raw["office_lat"]),
      "office_lon": safeDouble(raw["office_lon"]),
      "inside_geofence": raw["inside_geofence"] ?? false,
      "last_updated": raw["last_updated"] ?? "",
    };
  }

  // =====================================================
  // HISTORY (FIXED MAP BUG)
  // =====================================================
  static Future<List<dynamic>> getHistory(int employeeId) async {
    final res = await http
        .get(Uri.parse("$baseUrl/attendance_history?employee_id=$employeeId"))
        .timeout(const Duration(seconds: 15));

    final data = jsonDecode(res.body);

    final List list = data["data"] ?? [];

    return list.map((e) {
      return {
        "status": e["status"] ?? "Unknown",
        "attendance_date": e["attendance_date"] ?? "",
        "check_in": e["check_in"] ?? "",
        "check_out": e["check_out"] ?? "",
        "work_hours": e["work_hours"] ?? "-",
        "overtime_minutes": e["overtime_minutes"] ?? 0,
        "arrival_status": e["arrival_status"] ?? "-",
        "checkout_type": e["checkout_type"] ?? "",
      };
    }).toList();
  }
  // =====================================================
  // REPORT
  // =====================================================
  static Future<Map<String, dynamic>> getReport(
    int employeeId,
    int month,
    int year,
  ) async {
    final response = await http.post(
      Uri.parse("$baseUrl/attendance_report"),
      headers: {
        "Content-Type": "application/json",
      },
      body: jsonEncode({
        "employee_id": employeeId,
        "month": month,
        "year": year,
      }),
    );

    print("REPORT STATUS : ${response.statusCode}");
    print("REPORT BODY : ${response.body}");

    if (response.statusCode != 200) {
      throw Exception("Failed to load report");
    }

    final raw = jsonDecode(response.body);

    return {
      "present": safeInt(raw["present"] ?? 0),
      "absent": safeInt(raw["absent"] ?? 0),
      "half_day": safeInt(raw["half_day"] ?? 0),
      "leave": safeInt(raw["leave"] ?? 0),
      "total_work_hours": safeDouble(raw["total_work_hours"] ?? 0),
      "attendance_percent": safeDouble(raw["attendance_percent"] ?? 0),
    };
  }
  // =====================================================
  // CAPTURE LOCATION
  // =====================================================
  static Future<Map<String, dynamic>> captureLocation(
    int employeeId,
    double lat,
    double lon,
  ) async {
    final response = await http
        .post(
          Uri.parse("$baseUrl/track_location"),
          headers: {"Content-Type": "application/json"},
          body: jsonEncode({
            "employee_id": employeeId,
            "latitude": lat,
            "longitude": lon,
          }),
        )
        .timeout(const Duration(seconds: 15));

    final data = jsonDecode(response.body);

    if (data["distance"] != null) {
      data["distance"] = (data["distance"] as num).toDouble();
    }

    return data;
  }



  // ==========================
  // ADMIN DASHBOARD
  // ==========================
  static Future<Map<String, dynamic>> getAdminDashboard() async {
    final response = await http.get(
      Uri.parse("$baseUrl/admin_dashboard"),
      headers: {
        "Content-Type": "application/json",
      },
    ).timeout(const Duration(seconds: 10));

    print("ADMIN DASHBOARD RESPONSE: ${response.body}");

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Failed to load admin dashboard");
    }
  }

  // =====================================================
  // EMPLOYEE NOTIFICATIONS
  // =====================================================
  static Future<List<dynamic>> getEmployeeNotifications(
    int employeeId,
  ) async {

    final response = await http.get(
      Uri.parse("$baseUrl/employee_notifications/$employeeId"),
    ).timeout(const Duration(seconds: 10));

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Failed to load employee notifications");
    }
  }

  // =====================================================
  // EMPLOYEE LIST BY STATUS
  // =====================================================
  static Future<List<dynamic>> getEmployeesByStatus(
    String status,
  ) async {

    final response = await http.get(
      Uri.parse("$baseUrl/admin/employees/$status"),
    ).timeout(const Duration(seconds: 10));

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Failed to load employee list");
    }
  }

  // ==========================
// ALL EMPLOYEES
// ==========================
static Future<List<dynamic>> getAllEmployees() async {

  final response = await http.get(
    Uri.parse("$baseUrl/employees"),
  );

  print("ALL EMPLOYEES RESPONSE: ${response.body}");

  if (response.statusCode == 200) {
    return jsonDecode(response.body);
  } else {
    throw Exception("Failed to load employees");
  }
}


  // =====================================================
  // LIVE MAP EMPLOYEES
  // =====================================================
  static Future<List<dynamic>> getLiveMapEmployees() async {

    final response = await http.get(
      Uri.parse("$baseUrl/admin/live_map"),
    ).timeout(const Duration(seconds: 10));

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Failed to load live map");
    }
  }

  // ==========================
  // ADMIN NOTIFICATIONS
  // ==========================
  static Future<List<dynamic>> getAdminNotifications() async {

    final response = await http.get(
      Uri.parse("$baseUrl/all_notifications"),
      headers: {
        "Content-Type": "application/json",
      },
    );

    print("ADMIN NOTIFICATIONS: ${response.body}");

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Failed to load notifications");
    }
  }

  // SAVE FCM TOKEN
  static Future<void> saveFCMToken(
    int employeeId,
) async {

  String? token = await FirebaseMessaging.instance.getToken();

  if (token == null) return;

  await http.post(
    Uri.parse("$baseUrl/save_fcm_token"),
    headers: {
      "Content-Type": "application/json"
    },
    body: jsonEncode({
      "emp_id": employeeId,
      "token": token,
    }),
  );

  print("FCM TOKEN SAVED: $token");
}}