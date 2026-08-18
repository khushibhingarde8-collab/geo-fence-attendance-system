import 'package:flutter/material.dart';
import '../api_service.dart';

class ResetPasswordScreen extends StatefulWidget {
  final String email;

  const ResetPasswordScreen({
    super.key,
    required this.email,
  });

  @override
  State<ResetPasswordScreen> createState() =>
      _ResetPasswordScreenState();
}

class _ResetPasswordScreenState
    extends State<ResetPasswordScreen> {

  final newPasswordCtrl = TextEditingController();
  final confirmPasswordCtrl = TextEditingController();

  bool loading = false;

  bool obscure1 = true;
  bool obscure2 = true;

  void resetPassword() async {

    if (newPasswordCtrl.text.isEmpty ||
        confirmPasswordCtrl.text.isEmpty) {

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Fill all fields"),
        ),
      );

      return;
    }

    if (newPasswordCtrl.text !=
        confirmPasswordCtrl.text) {

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Passwords do not match"),
        ),
      );

      return;
    }

    setState(() {
      loading = true;
    });

    try {

      final res = await ApiService.resetPassword(
        widget.email,
        newPasswordCtrl.text,
      );

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(res["message"] ?? ""),
        ),
      );

      if (res["status"] == "success") {

        Navigator.popUntil(
          context,
          (route) => route.isFirst,
        );

      }

    } catch (e) {

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(e.toString()),
        ),
      );

    }

    setState(() {
      loading = false;
    });

  }

  Widget buildField({

    required TextEditingController controller,
    required String label,
    required IconData icon,
    required bool obscure,
    required VoidCallback toggle,

  }) {

    return TextField(

      controller: controller,

      obscureText: obscure,

      decoration: InputDecoration(

        labelText: label,

        prefixIcon: Icon(icon),

        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),

        suffixIcon: IconButton(

          icon: Icon(
            obscure
                ? Icons.visibility
                : Icons.visibility_off,
          ),

          onPressed: toggle,

        ),

      ),

    );

  }

  @override
  Widget build(BuildContext context) {

    return Scaffold(

      body: Container(

        width: double.infinity,

        decoration: const BoxDecoration(

          gradient: LinearGradient(

            colors: [
              Color(0xFF2193B0),
              Color(0xFF6DD5ED),
            ],

            begin: Alignment.topLeft,
            end: Alignment.bottomRight,

          ),

        ),

        child: Center(

          child: SingleChildScrollView(

            child: Padding(

              padding: const EdgeInsets.all(20),

              child: Card(

                elevation: 10,

                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(20),
                ),

                child: Padding(

                  padding: const EdgeInsets.all(20),

                  child: Column(

                    mainAxisSize: MainAxisSize.min,

                    children: [

                      const Text(

                        "Reset Password",

                        style: TextStyle(

                          fontSize: 22,

                          fontWeight: FontWeight.bold,

                          color: Colors.blueAccent,

                        ),

                      ),

                      const SizedBox(height: 15),

                      Text(

                        widget.email,

                        style: const TextStyle(

                          fontSize: 15,

                          color: Colors.black54,

                        ),

                        textAlign: TextAlign.center,

                      ),

                      const SizedBox(height: 25),

                      buildField(

                        controller: newPasswordCtrl,

                        label: "New Password",

                        icon: Icons.lock_outline,

                        obscure: obscure1,

                        toggle: () {

                          setState(() {

                            obscure1 = !obscure1;

                          });

                        },

                      ),

                      const SizedBox(height: 15),

                      buildField(

                        controller: confirmPasswordCtrl,

                        label: "Confirm Password",

                        icon: Icons.lock_reset,

                        obscure: obscure2,

                        toggle: () {

                          setState(() {

                            obscure2 = !obscure2;

                          });

                        },

                      ),

                      const SizedBox(height: 30),

                      SizedBox(

                        width: double.infinity,

                        height: 50,

                        child: ElevatedButton(

                          onPressed:
                              loading ? null : resetPassword,

                          style: ElevatedButton.styleFrom(

                            backgroundColor: Colors.blueAccent,

                            shape: RoundedRectangleBorder(

                              borderRadius:
                                  BorderRadius.circular(12),

                            ),

                          ),

                          child: loading

                              ? const CircularProgressIndicator(
                                  color: Colors.white,
                                )

                              : const Text(

                                  "RESET PASSWORD",

                                  style: TextStyle(
                                    fontSize: 16,
                                  ),

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