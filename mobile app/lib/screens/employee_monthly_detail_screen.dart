import 'package:flutter/material.dart';
import '../api_service.dart';


class EmployeeMonthlyDetailScreen extends StatefulWidget {


  final int employeeId;
  final String employeeName;
  final int month;
  final int year;


  const EmployeeMonthlyDetailScreen({

    super.key,

    required this.employeeId,

    required this.employeeName,

    required this.month,

    required this.year,

  });


  @override
  State<EmployeeMonthlyDetailScreen> createState()
      => _EmployeeMonthlyDetailScreenState();

}



class _EmployeeMonthlyDetailScreenState
    extends State<EmployeeMonthlyDetailScreen>{


  Map<String,dynamic>? report;

  bool loading=true;



  @override
  void initState(){

    super.initState();

    fetchReport();

  }



  Future<void> fetchReport() async {

    try {

      final result =
      await ApiService.getEmployeeMonthlyDetail(
        widget.employeeId,
        widget.month,
        widget.year,
      );


      final emp = result["data"][0];


      List records = emp["records"] ?? [];


      int present = 0;
      int halfDay = 0;
      int absent = 0;
      int leave = 0;
      int holiday = 0;
      int weeklyOff = 0;


      for(var r in records){

        switch(r["status"]){

          case "Present":
          case "Full Day":
            present++;
            break;


          case "Half Day":
            halfDay++;
            break;


          case "Absent":
            absent++;
            break;


          case "Leave":
            leave++;
            break;


          case "Holiday":
            holiday++;
            break;


          case "Weekly Off":
            weeklyOff++;
            break;

        }

      }



      setState(() {

        report = {

          "employee_name":
          emp["employee_name"],


          "department":
          emp["department"],


          "records":
          records,


          "summary":{

            "present":present,

            "half_day":halfDay,

            "absent":absent,

            "leave":leave,

            "holiday":holiday,

            "weekly_off":weeklyOff

          }

        };


        loading=false;


      });


    }
    catch(e){

      print("DETAIL ERROR : $e");


      setState((){

        loading=false;

      });


      ScaffoldMessenger.of(context)
          .showSnackBar(

        SnackBar(
            content:
            Text("Failed to load report")
        ),

      );

    }

  }





  @override
  Widget build(BuildContext context){


    return Scaffold(


      backgroundColor: Colors.grey.shade100,


      appBar: AppBar(

        backgroundColor: Colors.blue,

        foregroundColor: Colors.white,


        title: Column(

          crossAxisAlignment:
          CrossAxisAlignment.start,

          children: [


            Text(
              widget.employeeName,
              style: const TextStyle(
                  fontSize:18,
                  fontWeight:FontWeight.bold
              ),
            ),


            const Text(

              "Monthly Attendance Report",

              style:TextStyle(
                  fontSize:12
              ),

            )


          ],

        ),

      ),



      body:


      loading

          ?

      const Center(
          child:CircularProgressIndicator()
      )


          :

      buildContent(),



    );


  }






  Widget buildContent(){


    return SingleChildScrollView(


      padding:
      const EdgeInsets.all(12),


      child:Column(

        crossAxisAlignment:
        CrossAxisAlignment.start,


        children:[



          employeeCard(),


          const SizedBox(height:15),



          Text(

            "Totals for ${monthName(widget.month)} ${widget.year}",

            style:
            const TextStyle(

                fontSize:18,

                fontWeight:
                FontWeight.bold

            ),

          ),



          const SizedBox(height:12),



          summaryGrid(),



          const SizedBox(height:20),



          attendanceCard(),



          const SizedBox(height:20),



          legend(),



        ],


      ),


    );


  }






  Widget employeeCard(){


    return Card(


      elevation:3,

      shape:
      RoundedRectangleBorder(

          borderRadius:
          BorderRadius.circular(15)

      ),


      child:Padding(

        padding:
        const EdgeInsets.all(16),


        child:Row(

          children:[



            CircleAvatar(

              radius:35,

              backgroundColor:
              Colors.blue,

              child:

              Text(

                widget.employeeName
                    .substring(0,1)
                    .toUpperCase(),

                style:
                const TextStyle(

                    color:Colors.white,

                    fontSize:30,

                    fontWeight:
                    FontWeight.bold

                ),

              ),

            ),



            const SizedBox(width:15),



            Column(

              crossAxisAlignment:
              CrossAxisAlignment.start,


              children:[



                Text(

                  report?["employee_name"]
                      ??
                      widget.employeeName,


                  style:
                  const TextStyle(

                      fontSize:18,

                      fontWeight:
                      FontWeight.bold

                  ),

                ),



                Text(

                  "Employee ID : ${widget.employeeId}",

                  style:
                  TextStyle(

                      color:
                      Colors.grey.shade700

                  ),

                ),



                Text(

                  report?["department"]
                      ??
                      "Department",

                  style:
                  TextStyle(

                      color:
                      Colors.grey.shade700

                  ),

                )



              ],


            )


          ],


        ),

      ),

    );


  }








  Widget summaryGrid(){


    return GridView.count(


      shrinkWrap:true,

      physics:
      const NeverScrollableScrollPhysics(),


      crossAxisCount:2,


      childAspectRatio:1.8,


      crossAxisSpacing:12,

      mainAxisSpacing:12,



      children:[



        statCard(
            "Present",
            report?["summary"]?["present"] ?? 0,
            Colors.green
        ),



        statCard(
            "Half Day",
            report?["summary"]?["half_day"] ?? 0,
            Colors.orange
        ),



        statCard(
            "Absent",
            report?["summary"]?["absent"] ?? 0,
            Colors.red
        ),



        statCard(
            "Leave",
            report?["summary"]?["leave"] ?? 0,
            Colors.blue
        ),



        statCard(
            "Holiday",
            report?["summary"]?["holiday"] ?? 0,
            Colors.amber
        ),



        statCard(
            "Weekly Off",
            report?["summary"]?["weekly_off"] ?? 0,
            Colors.purple
        ),


      ],


    );


  }






  Widget statCard(
    String title,
    dynamic value,
    Color color,
  ) {
    Color background;

    if (color == Colors.green) {
      background = const Color(0xFFE8F5E9);
    } else if (color == Colors.orange) {
      background = const Color(0xFFFFF3E0);
    } else if (color == Colors.red) {
      background = const Color(0xFFFFEBEE);
    } else if (color == Colors.blue) {
      background = const Color(0xFFE3F2FD);
    } else if (color == Colors.amber) {
      background = const Color(0xFFFFFDE7);
    } else {
      background = const Color(0xFFF3E5F5);
    }

    return Card(
      elevation: 6,
      shadowColor: color.withOpacity(0.25),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(18),
        side: BorderSide(
          color: color.withOpacity(0.7),
          width: 1.5,
        ),
      ),
      child: Container(
        decoration: BoxDecoration(
          color: background,
          borderRadius: BorderRadius.circular(18),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              title,
              style: TextStyle(
                color: color,
                fontSize: 18,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 10),
            Text(
              value.toString(),
              style: TextStyle(
                color: color,
                fontSize: 34,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }





  Widget attendanceCard(){


    List attendance =
    report?["records"] ?? [];



    return Card(


      elevation:3,


      shape:
      RoundedRectangleBorder(

          borderRadius:
          BorderRadius.circular(15)

      ),



      child:Padding(

        padding:
        const EdgeInsets.all(12),


        child:Column(

          crossAxisAlignment:
          CrossAxisAlignment.start,


          children:[



            const Text(

              "Attendance Details",

              style:
              TextStyle(

                  fontSize:18,

                  fontWeight:
                  FontWeight.bold

              ),

            ),



            const Divider(),




            ListView.builder(

              shrinkWrap:true,

              physics:
              const NeverScrollableScrollPhysics(),


              itemCount:
              attendance.length,


              itemBuilder:
                  (context,index){



                var item =
                attendance[index];



                return ListTile(

                  contentPadding:
                  EdgeInsets.zero,


                  title:Text(

                      item["date"]
                          .toString()

                  ),



                  trailing:
                  statusChip(

                      item["status"]
                          .toString()

                  ),


                );


              },

            )



          ],


        ),

      ),


    );


  }






  Widget statusChip(String status){


    Color color;


    switch(status){

      case "Present":

        color=Colors.green;

        break;


      case "Half Day":

        color=Colors.orange;

        break;


      case "Absent":

        color=Colors.red;

        break;


      case "Leave":

        color=Colors.blue;

        break;


      case "Holiday":

        color=Colors.amber;

        break;


      case "Weekly Off":

        color=Colors.purple;

        break;


      default:

        color=Colors.grey;

    }



    return Container(

      padding:
      const EdgeInsets.symmetric(
          horizontal:12,
          vertical:6
      ),


      decoration:
      BoxDecoration(

          color:
          color.withOpacity(.15),


          borderRadius:
          BorderRadius.circular(20)

      ),


      child:Text(

        status.toUpperCase(),


        style:
        TextStyle(

            color:color,

            fontWeight:
            FontWeight.bold,

            fontSize:12

        ),

      ),

    );


  }








  Widget legend(){


    return Card(

      child:Padding(

        padding:
        const EdgeInsets.all(12),


        child:Wrap(

          spacing:15,

          runSpacing:10,


          children:[


            legendItem(
                "P",
                "Present",
                Colors.green
            ),


            legendItem(
                "HD",
                "Half Day",
                Colors.orange
            ),


            legendItem(
                "A",
                "Absent",
                Colors.red
            ),


            legendItem(
                "L",
                "Leave",
                Colors.blue
            ),


            legendItem(
                "H",
                "Holiday",
                Colors.amber
            ),


            legendItem(
                "WO",
                "Weekly Off",
                Colors.purple
            ),



          ],


        ),


      ),

    );


  }







  Widget legendItem(
      String short,
      String text,
      Color color
      ){


    return Row(

      mainAxisSize:
      MainAxisSize.min,


      children:[


        CircleAvatar(

          radius:12,

          backgroundColor:
          color,


          child:Text(

            short,

            style:
            const TextStyle(

                fontSize:9,

                color:Colors.white

            ),

          ),

        ),


        const SizedBox(width:5),


        Text(text)


      ],


    );


  }






  String monthName(int month){


    const months=[

      "",
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


    return months[month];


  }



}