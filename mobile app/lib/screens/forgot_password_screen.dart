import 'package:flutter/material.dart';
import '../api_service.dart';
import 'otp_verification_screen.dart';


class ForgotPasswordScreen extends StatefulWidget {

  const ForgotPasswordScreen({super.key});

  @override
  State<ForgotPasswordScreen> createState() =>
      _ForgotPasswordScreenState();

}


class _ForgotPasswordScreenState
    extends State<ForgotPasswordScreen> {


  final emailCtrl = TextEditingController();

  bool loading = false;



  void sendOTP() async {


    if(emailCtrl.text.trim().isEmpty){

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text("Email required"),
        ),
      );

      return;

    }


    setState(() {
      loading = true;
    });



    try {


      final res = await ApiService.sendResetOTP(
        emailCtrl.text.trim(),
      );



      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            res["message"] ?? "",
          ),
        ),
      );



      if(res["status"] == "success"){


        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) =>
                OTPVerificationScreen(
                  email: emailCtrl.text.trim(),
                ),
          ),
        );


      }



    } catch(e){


      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            "Error: $e",
          ),
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


                shape: RoundedRectangleBorder(

                  borderRadius: BorderRadius.circular(20),

                ),


                elevation: 10,


                child: Padding(

                  padding: const EdgeInsets.all(20),



                  child: Column(


                    mainAxisSize: MainAxisSize.min,



                    children: [



                      const Text(

                        "Forgot Password",

                        style: TextStyle(

                          fontSize: 22,

                          fontWeight: FontWeight.bold,

                          color: Colors.blueAccent,

                        ),

                      ),



                      const SizedBox(height:20),




                      buildField(

                        controller: emailCtrl,

                        label: "Email",

                        icon: Icons.email,

                      ),




                      const SizedBox(height:25),




                      SizedBox(

                        width: double.infinity,

                        height:50,


                        child: ElevatedButton(

                          onPressed:
                              loading ? null : sendOTP,



                          style: ElevatedButton.styleFrom(

                            backgroundColor:
                                Colors.blueAccent,


                            shape:
                            RoundedRectangleBorder(

                              borderRadius:
                              BorderRadius.circular(12),

                            ),

                          ),



                          child: loading

                              ? const CircularProgressIndicator(

                            color: Colors.white,

                          )


                              :

                          const Text(

                            "SEND OTP",

                            style: TextStyle(

                              fontSize:16,

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