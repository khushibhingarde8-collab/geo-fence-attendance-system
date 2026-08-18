import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';

import '../api_service.dart';
import 'change_password_screen.dart';
import 'forgot_password_screen.dart';
import 'home_screen.dart';
import 'admin_home_screen.dart';

import 'package:shared_preferences/shared_preferences.dart';
import '../services/background_service.dart';
import 'package:geolocator/geolocator.dart';
import 'package:firebase_messaging/firebase_messaging.dart';


class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginState();
}

class _LoginState extends State<LoginScreen> {

  final emailCtrl = TextEditingController();
  final passCtrl = TextEditingController();

  bool loading = false;
  bool obscurePassword = true;


  // =====================================================
  // LOGIN
  // =====================================================

  Future<void> loginUser() async {

    setState(() => loading = true);

    try {

      // =====================================================
      // EMPLOYEE LOGIN
      // =====================================================

      Map<String, dynamic> res = await ApiService.login(
        emailCtrl.text.trim(),
        passCtrl.text.trim(),
      );


      // =====================================================
      // IF EMPLOYEE LOGIN FAILS -> TRY ADMIN LOGIN
      // =====================================================

      if (res["status"] != "success") {

        res = await ApiService.adminLogin(
          emailCtrl.text.trim(),
          passCtrl.text.trim(),
        );

        print("ADMIN LOGIN RESPONSE: $res");
      }


      print("LOGIN RESPONSE: $res");


      // =====================================================
      // INVALID LOGIN
      // =====================================================

      if (res["status"] != "success") {

        if (!mounted) return;

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("Invalid credentials"),
          ),
        );

        return;
      }


      // =====================================================
      // ADMIN LOGIN
      // =====================================================

      if ((res["role"] ?? "").toString().toLowerCase() == "admin") {

        final prefs = await SharedPreferences.getInstance();

        await prefs.setBool("isLoggedIn", true);
        await prefs.setString("role", "admin");


        if (!mounted) return;

        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => const AdminHomeScreen(),
          ),
        );

        return;
      }


      // =====================================================
      // EMPLOYEE ID
      // =====================================================

      final int empId = int.tryParse(
            res["employee_id"]?.toString() ?? "",
          ) ??
          -1;


      print("DEBUG empId: $empId");


      if (empId == -1) {

        if (!mounted) return;

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              "Employee ID missing from server",
            ),
          ),
        );

        return;
      }


      // =====================================================
      // LOCATION SERVICE CHECK
      // =====================================================

      bool serviceEnabled =
          await Geolocator.isLocationServiceEnabled();


      if (!serviceEnabled) {

        if (!mounted) return;

        setState(() => loading = false);

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              "Please turn ON Location.",
            ),
          ),
        );

        return;
      }


      // =====================================================
      // CHECK LOCATION PERMISSION
      // =====================================================

      LocationPermission permission =
          await Geolocator.checkPermission();


      // -----------------------------------------------------
      // ASK FOR LOCATION PERMISSION IF DENIED
      // -----------------------------------------------------

      if (permission == LocationPermission.denied) {

        permission =
            await Geolocator.requestPermission();
      }


      // -----------------------------------------------------
      // PERMISSION DENIED FOREVER
      // -----------------------------------------------------

      if (permission ==
          LocationPermission.deniedForever) {

        if (!mounted) return;

        setState(() => loading = false);

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              "Please enable location permission from Settings.",
            ),
          ),
        );

        return;
      }


      // -----------------------------------------------------
      // PERMISSION STILL DENIED
      // -----------------------------------------------------

      if (permission == LocationPermission.denied) {

        if (!mounted) return;

        setState(() => loading = false);

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              "Please allow location permission.",
            ),
          ),
        );

        return;
      }


      // =====================================================
      // ANDROID ONLY
      // REQUIRE "ALLOW ALL THE TIME"
      // =====================================================
      //
      // IMPORTANT:
      //
      // Web does NOT enter this block.
      //
      // Android still requires "Allow all the time"
      // for your background location tracking.
      //
      // =====================================================

      if (!kIsWeb &&
          defaultTargetPlatform == TargetPlatform.android) {

        if (permission != LocationPermission.always) {

          permission =
              await Geolocator.requestPermission();


          if (permission !=
              LocationPermission.always) {

            if (!mounted) return;

            setState(() => loading = false);

            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text(
                  "Please select 'Allow all the time' for background tracking.",
                ),
              ),
            );

            return;
          }
        }
      }


      // =====================================================
      // SAVE LOGIN INFORMATION
      // =====================================================

      final prefs =
          await SharedPreferences.getInstance();


      await prefs.setBool(
        "isLoggedIn",
        true,
      );


      await prefs.setInt(
        "emp_id",
        empId,
      );


      await prefs.setString(
        "role",
        "employee",
      );


      // =====================================================
      // SAVE FCM TOKEN
      // =====================================================

      await ApiService.saveFCMToken(
        empId,
      );


      // =====================================================
      // FIRST LOGIN CHECK
      // =====================================================

      final bool isFirstLogin =
          res["first_login"] == 1;


      if (!mounted) return;


      // =====================================================
      // FIRST LOGIN -> CHANGE PASSWORD
      // =====================================================

      if (isFirstLogin) {

        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) =>
                ChangePasswordScreen(
              empId: empId,
            ),
          ),
        );

      }

      // =====================================================
      // NORMAL EMPLOYEE LOGIN
      // =====================================================

      else {

        // =================================================
        // START BACKGROUND SERVICE ONLY ON MOBILE
        // =================================================
        //
        // Web:
        // No flutter_background_service
        //
        // Android:
        // Background tracking starts
        //
        // iOS:
        // Existing service configuration remains available
        //
        // =================================================

        if (!kIsWeb) {

          await Future.delayed(
            const Duration(
              seconds: 1,
            ),
          );

          await initializeService();

          await startBackgroundService();

        }


        // =================================================
        // GO TO EMPLOYEE HOME
        // =================================================

        if (!mounted) return;

        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) =>
                HomeScreen(
              empId: empId,
            ),
          ),
        );
      }

    }

    // =====================================================
    // ERROR
    // =====================================================

    catch (e) {

      print("LOGIN ERROR: $e");


      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            "Error: $e",
          ),
        ),
      );
    }

    // =====================================================
    // STOP LOADING
    // =====================================================

    finally {

      if (mounted) {

        setState(
          () => loading = false,
        );
      }
    }
  }


  // =====================================================
  // UI
  // =====================================================

  @override
  Widget build(
    BuildContext context,
  ) {

    return Scaffold(

      body: Container(

        decoration: const BoxDecoration(

          gradient: LinearGradient(

            colors: [
              Colors.blue,
              Colors.blueAccent,
            ],

            begin:
                Alignment.topCenter,

            end:
                Alignment.bottomCenter,
          ),
        ),


        child: Center(

          child: SingleChildScrollView(

            child: Padding(

              padding:
                  const EdgeInsets.all(20),


              child: Card(

                shape:
                    RoundedRectangleBorder(

                  borderRadius:
                      BorderRadius.circular(20),
                ),


                child: Padding(

                  padding:
                      const EdgeInsets.all(20),


                  child: Column(

                    children: [

                      // =================================================
                      // TITLE
                      // =================================================

                      const Text(

                        "Login",

                        style: TextStyle(

                          fontSize: 22,

                          fontWeight:
                              FontWeight.bold,
                        ),
                      ),


                      const SizedBox(
                        height: 20,
                      ),


                      // =================================================
                      // EMAIL
                      // =================================================

                      TextField(

                        controller:
                            emailCtrl,

                        decoration:
                            const InputDecoration(

                          labelText:
                              "Email",

                          prefixIcon:
                              Icon(
                            Icons.person,
                          ),
                        ),
                      ),


                      const SizedBox(
                        height: 10,
                      ),


                      // =================================================
                      // PASSWORD
                      // =================================================

                      TextField(

                        controller:
                            passCtrl,

                        obscureText:
                            obscurePassword,

                        decoration:
                            InputDecoration(

                          labelText:
                              "Password",

                          prefixIcon:
                              const Icon(
                            Icons.lock,
                          ),


                          suffixIcon:
                              IconButton(

                            icon: Icon(

                              obscurePassword
                                  ? Icons.visibility
                                  : Icons.visibility_off,
                            ),

                            onPressed: () {

                              setState(() {

                                obscurePassword =
                                    !obscurePassword;
                              });
                            },
                          ),
                        ),
                      ),


                      const SizedBox(
                        height: 15,
                      ),


                      // =================================================
                      // FORGOT PASSWORD
                      // =================================================

                      Align(

                        alignment:
                            Alignment.centerRight,

                        child:
                            TextButton(

                          onPressed: () {

                            Navigator.push(

                              context,

                              MaterialPageRoute(

                                builder: (_) =>
                                    ForgotPasswordScreen(),
                              ),
                            );
                          },

                          child:
                              const Text(
                            "Forgot Password?",
                          ),
                        ),
                      ),


                      const SizedBox(
                        height: 10,
                      ),


                      // =================================================
                      // LOGIN BUTTON
                      // =================================================

                      SizedBox(

                        width:
                            double.infinity,

                        height:
                            50,


                        child:
                            ElevatedButton(

                          onPressed:
                              loading
                                  ? null
                                  : loginUser,


                          style:
                              ElevatedButton.styleFrom(

                            backgroundColor:
                                Colors.blue,
                          ),


                          child:

                              loading

                                  ? const CircularProgressIndicator(
                                      color:
                                          Colors.white,
                                    )

                                  : const Text(
                                      "LOGIN",
                                    ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}