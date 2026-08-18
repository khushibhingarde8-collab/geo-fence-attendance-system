import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'login_screen.dart';

class ProfileScreen extends StatefulWidget {
  final int empId;

  const ProfileScreen({super.key, required this.empId});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {

  bool loading = false;

  // =========================
  // LOGOUT FUNCTION
  // =========================
  Future<void> logout() async {
    setState(() => loading = true);

    try {
      final prefs = await SharedPreferences.getInstance();

      // CLEAR STORED SESSION
      await prefs.remove("employee_id");

      if (!mounted) return;

      Navigator.pushAndRemoveUntil(
        context,
        MaterialPageRoute(builder: (_) => const LoginScreen()),
        (route) => false,
      );

    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Logout failed")),
      );
    }

    setState(() => loading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Profile"),
        backgroundColor: Colors.blueAccent,
      ),

      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [

              const Icon(Icons.person, size: 90, color: Colors.blue),

              const SizedBox(height: 15),

              Text(
                "Employee ID: ${widget.empId.toString()}",
                style: const TextStyle(fontSize: 18),
              ),

              const SizedBox(height: 30),

              // =========================
              // LOGOUT BUTTON
              // =========================
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton.icon(
                  onPressed: loading ? null : logout,
                  icon: loading
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : const Icon(Icons.logout),

                  label: Text(
                    loading ? "Logging out..." : "Logout",
                  ),

                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}