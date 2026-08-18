import 'package:flutter/material.dart';
import '../api_service.dart';
import 'reset_password_screen.dart';

class OTPVerificationScreen extends StatefulWidget {
  final String email;

  const OTPVerificationScreen({
    super.key,
    required this.email,
  });

  @override
  State<OTPVerificationScreen> createState() =>
      _OTPVerificationScreenState();
}

class _OTPVerificationScreenState
    extends State<OTPVerificationScreen> {

  final otpCtrl = TextEditingController();

  bool loading = false;

  void verifyOTP() async {

    if (otpCtrl.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Enter OTP"),
        ),
      );
      return;
    }

    setState(() {
      loading = true;
    });

    try {

      final res = await ApiService.verifyResetOTP(
        widget.email,
        otpCtrl.text.trim(),
      );

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(res["message"] ?? ""),
        ),
      );

      if (res["status"] == "success") {

        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => ResetPasswordScreen(
              email: widget.email,
            ),
          ),
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
    IconData? icon,
  }) {
    return TextField(
      controller: controller,
      keyboardType: TextInputType.number,
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
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
                        "OTP Verification",
                        style: TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                          color: Colors.blueAccent,
                        ),
                      ),

                      const SizedBox(height: 15),

                      Text(
                        "OTP has been sent to",
                        style: TextStyle(
                          color: Colors.grey.shade700,
                          fontSize: 15,
                        ),
                      ),

                      const SizedBox(height: 5),

                      Text(
                        widget.email,
                        textAlign: TextAlign.center,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Colors.black87,
                          fontSize: 16,
                        ),
                      ),

                      const SizedBox(height: 25),

                      buildField(
                        controller: otpCtrl,
                        label: "Enter OTP",
                        icon: Icons.verified_user,
                      ),

                      const SizedBox(height: 30),

                      SizedBox(

                        width: double.infinity,
                        height: 50,

                        child: ElevatedButton(

                          onPressed:
                              loading ? null : verifyOTP,

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
                                  "VERIFY OTP",
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